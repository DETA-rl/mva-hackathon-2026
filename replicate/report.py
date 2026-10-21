"""results/results.json and results/REPLICATION_REPORT.md.

The two result files carry metric values, ranks, labels, hashes and timings only: no input path, no file name
of an input, no genomic coordinate. Free text that could carry one (error messages) is redacted. Raw script
output stays in logs/ and steps/, which are private.
"""
from __future__ import annotations

import json
import os
import platform
import re

from replicate import __version__, system
from replicate.config import REPO_ROOT

LOCK = REPO_ROOT / "env" / "requirements_freeze.txt"
KEY_PACKAGES = ["numpy", "scipy", "pandas", "pysam", "pyyaml", "torch", "transformers", "evo2", "vtx", "flash-attn",
                "transformer-engine", "pytest"]


def redact(text):
    if not text:
        return text
    text = re.sub(r"(/[^\s'\":]+)+", "<path>", str(text))
    text = re.sub(r"\b\d{7,}\b", "<n>", text)
    return text


def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.6g}"
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(", ", ": "))
    return str(v)


def _gb(v):
    return "not recorded" if v is None else f"{v} GB"


def environment(cfg):
    probe = system.python_probe(cfg.python)
    lock = system.read_lock(LOCK) if LOCK.exists() else {}
    pk = probe.get("packages", {})
    diffs = {k: {"lock": v, "installed": pk.get(k)} for k, v in lock.items() if pk.get(k) != v}
    total, _ = system.mem_gb()
    return {"harness_version": __version__, "git": system.git_state(), "os": system.os_info(),
            "cpu_count": os.cpu_count(), "ram_total_gb": round(total, 1) if total else None,
            "python": probe.get("python"), "python_implementation": probe.get("implementation"),
            "key_packages": {k: pk.get(k) for k in KEY_PACKAGES},
            "lock_file": "env/requirements_freeze.txt", "lock_mismatches": diffs,
            "gpus": [{k: g[k] for k in ("index", "name", "memory_total_gb", "driver")} for g in system.gpus()],
            "cuda_version_driver": system.cuda_version(), "cuda_toolkit": system.cuda_toolkit(),
            "torch_cuda": system.torch_cuda(cfg.python) if pk.get("torch") else None,
            "harness_python": platform.python_version(),
            "settings": {"cuda_visible_devices": cfg.cuda_visible_devices, "allow_network": cfg.allow_network,
                         "write_guard": cfg.write_guard, "PYTHONHASHSEED": "0"}}


def write_report(runner, records, rules, started, finished):
    cfg, exp = runner.cfg, runner.expected
    env = environment(cfg)
    inputs = {}
    for k, st in runner.input_state.items():
        spec = exp["inputs"].get(k, {})
        inputs[k] = {"what": spec.get("what"), "state": st["state"],
                     "observed_sha256": st.get("sha256") if st["state"] in ("match", "differs") else None,
                     "expected_sha256": spec.get("sha256"), "source": spec.get("source")}
    for r in records:
        r["reason"] = redact(r.get("reason"))
        r["artifacts"] = {k: (os.path.relpath(v, runner.workdir) if str(v).startswith(str(runner.workdir)) else "<supplied>")
                          for k, v in (r.get("artifacts") or {}).items()}
    counts = {}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    res = {"title": "MVA Hackathon 2026: replication report", "tier": runner.tier, "started_utc": started,
           "finished_utc": finished, "summary": counts, "environment": env, "inputs": inputs,
           "rules": {k: {"ok": v["ok"], "expected": v.get("expected"), "observed": v.get("observed"),
                         "not_shipped": v.get("not_shipped", False)} for k, v in rules.items()},
           "intermediates_used": {k: {"origin": runner.artifact_origin.get(k), "matches_ours": runner.artifact_ok.get(k)}
                                  for k in runner.cfg.intermediates if k in runner.artifact_origin},
           "steps": records}
    out = runner.results_dir
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str))
    (out / "REPLICATION_REPORT.md").write_text(markdown(res))
    return res


def markdown(res):
    L = [f"# {res['title']}", "",
         f"Tier: **{res['tier']}**. Started {res['started_utc']}, finished {res['finished_utc']} (UTC).", "",
         "What the statuses mean:",
         "- PASS: the step ran and every metric matched the value recorded in the register (or, for file hashes, "
         "the authors' stored output) within the stated tolerance.",
         "- FAIL: the step ran and at least one metric is outside its tolerance, or was not produced.",
         "- INCONCLUSIVE: the step ran, but an input differs from ours (for example a BAM from a fresh alignment), "
         "so exact metrics are reported as NOT COMPARABLE rather than PASS or FAIL.",
         "- ERROR: the step started and did not finish. NOT RUN / REFUSED: the step did not start (reason given).",
         "", "## Summary", "", "| status | steps |", "|---|---|"]
    for k, v in sorted(res["summary"].items()):
        L.append(f"| {k} | {v} |")
    L += ["", "| step | register entry | tier | status | metrics passed | wall time |", "|---|---|---|---|---|---|"]
    for r in res["steps"]:
        ms = r.get("metrics", [])
        npass = sum(1 for m in ms if m["verdict"] == "PASS")
        L.append(f"| {r['id']} | {r['register']} | {r['tier']} | {r['status']}{' (earlier run)' if r.get('reused') else ''} | "
                 f"{f'{npass}/{len(ms)}' if ms else '-'} | {r.get('seconds', '-')} s |")
    e = res["environment"]
    L += ["", "## Environment", "",
          f"- harness {e['harness_version']}; git commit {e['git'].get('commit') or 'none'}"
          f"{' (uncommitted changes)' if e['git'].get('dirty') else ''}",
          f"- OS {e['os'].get('distribution') or e['os']['system']} {e['os']['release']} {e['os']['machine']}; "
          f"{e['cpu_count']} CPUs; {e['ram_total_gb']} GB RAM",
          f"- analysis Python {e['python']}; key packages: " +
          ", ".join(f"{k} {v}" for k, v in e["key_packages"].items() if v),
          f"- packages differing from the lock ({e['lock_file']}): {len(e['lock_mismatches'])}" +
          ("" if not e["lock_mismatches"] else " (" + ", ".join(
              f"{k} lock {v['lock']} / installed {v['installed']}" for k, v in list(e["lock_mismatches"].items())[:12]) + ")"),
          f"- GPUs: " + ("; ".join(f"{g['index']}: {g['name']} {g['memory_total_gb']:.0f} GB, driver {g['driver']}"
                                   for g in e["gpus"]) or "none") + f"; CUDA (driver UMD) {e['cuda_version_driver']}, toolkit {e['cuda_toolkit']}"
          + (f"; torch {e['torch_cuda'].get('torch')} built for CUDA {e['torch_cuda'].get('cuda_build')}" if e.get("torch_cuda") else ""),
          f"- settings: {json.dumps(e['settings'])}", "",
          "## Inputs", "", "| input | state | sha256 (observed) | expected source |", "|---|---|---|---|"]
    for k, v in sorted(res["inputs"].items()):
        L.append(f"| {k} | {v['state']} | `{(v['observed_sha256'] or '-')[:16]}` | {v.get('source') or '-'} |")
    L += ["", "## Rule files", "", "| rule | sha256 matches the recorded hash |", "|---|---|"]
    for k, v in sorted(res["rules"].items()):
        L.append(f"| {k} | {'yes' if v['ok'] else 'NO'}{' (held back, not in the repo)' if v['not_shipped'] else ''} |")
    if res["intermediates_used"]:
        L += ["", "## Supplied intermediates", "",
              "Outputs of full-tier steps given in the config instead of being recomputed in this run.", "",
              "| artifact | identical to our stored output |", "|---|---|"]
        for k, v in res["intermediates_used"].items():
            L.append(f"| {k} | {'yes' if v['matches_ours'] else 'NO'} |")
    L += ["", "## Steps", ""]
    for r in res["steps"]:
        L += [f"### {r['id']}: {r['title']}", "",
              f"- register entry: {r['register']}" + (f"; rule file `rules/{r['rule_file']}`" if r.get("rule_file") else ""),
              f"- status: **{r['status']}**" + (f" ({r['reason']})" if r.get("reason") else "") +
              (f"; {r['reused']}" if r.get("reused") else "") +
              (f"; code commit {(r.get('code_commit') or 'none')[:12]}" if r.get("code_commit") != e["git"].get("commit") else ""),
              f"- pre-registered decision rule: {r.get('decision_rule') or '-'}"]
        d = r["declared"]
        gpu = f"yes ({_gb(d['vram_gb'])} VRAM)" if d["gpu"] else "no"
        L.append(f"- declared resources: GPU {gpu}, RAM {_gb(d['ram_gb'])}, disk {_gb(d['disk_gb'])}, "
                 f"network {'yes' if d['network'] else 'no'}; runtime {d['runtime']}")
        if r.get("measured"):
            m = r["measured"]
            L.append(f"- measured: wall {m['wall_s']} s, peak RSS {m['peak_rss_gb']} GB, step folder {m['step_folder_gb']} GB")
        if r.get("inputs"):
            L.append("- inputs: " + ", ".join(f"{k} ({v})" for k, v in r["inputs"].items()))
        if r.get("artifacts_used"):
            L.append("- upstream outputs: " + ", ".join(
                f"{k} ({v['origin']}; identical to ours: {'yes' if v['matches_ours'] else 'no'})" for k, v in r["artifacts_used"].items()))
        if r.get("exact_conditions") and not r["exact_conditions"]["all_match"]:
            L.append("- exact comparison not applicable for: " + ", ".join(r["exact_conditions"]["differs"]))
        if r.get("note"):
            L.append(f"- note: {r['note']}")
        if r.get("metrics"):
            L += ["", "| metric | expected | observed | tolerance | verdict | expected value from |", "|---|---|---|---|---|---|"]
            for m in r["metrics"]:
                L.append(f"| {m['metric']} | {fmt(m['expected'])} | {fmt(m['observed'])} | {m['tolerance']} | "
                         f"{m['verdict']} | {m['source']} |")
        if r.get("info"):
            L += ["", "Other values printed by the step (no expected value in the register):", ""]
            if r.get("info_note"):
                L += [f"How to read them: {r['info_note']}", ""]
            for m in r["info"]:
                L.append(f"- {m['metric']}: {fmt(m['observed'])}")
        L.append("")
    L += ["## Privacy", "",
          "This report and results.json hold counts, ranks, labels, hashes and timings only. The step folders "
          "(steps/), logs (logs/) and private/ in the workdir contain patient-derived data and must not be shared "
          "or committed.", ""]
    return "\n".join(L)
