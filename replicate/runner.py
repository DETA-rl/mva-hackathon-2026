"""Execute the step graph under resource guards and record everything needed for the report."""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path

from replicate import __version__, system
from replicate.compare import compare_metrics, step_status
from replicate.config import Config
from replicate.framework import RULES, Ctx, StepError
from replicate.hashing import HashCache
from replicate.registry import (artifact_match, input_match, load_expected, rule_status, select, topo_order)
from replicate.steps import PROVIDER, root_missing, route

TMP_MARKER = ".created_by_replicate"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def say(msg):
    print(msg, flush=True)


def guard(step, cfg, workdir):
    """Reasons to refuse before starting; [] means go."""
    why = []
    free = system.disk_free_gb(workdir)
    need = step.disk_gb + cfg.disk_margin_gb
    if free - step.disk_gb < cfg.disk_floor_gb or free < need:
        why.append(f"disk: {free:.1f} GB free at the workdir; step budget {step.disk_gb} GB + margin "
                   f"{cfg.disk_margin_gb} GB, floor {cfg.disk_floor_gb} GB")
    _, avail = system.mem_gb()
    if avail is not None and avail < step.ram_gb + cfg.ram_margin_gb:
        why.append(f"RAM: {avail:.1f} GB available; step needs {step.ram_gb} GB + margin {cfg.ram_margin_gb} GB")
    if step.gpu:
        g = system.gpus()
        if not g:
            why.append("GPU: nvidia-smi found no GPU")
        else:
            devs = [d for d in cfg.cuda_visible_devices.split(",") if d.strip() != ""]
            if not devs:
                why.append("GPU: cuda_visible_devices is empty")
            if len(devs) > 1:
                why.append("GPU: more than one device selected; the Evo 2 load failed on two GPUs, so steps run on one")
            for d in devs:
                gg = [x for x in g if str(x["index"]) == d.strip()]
                if not gg:
                    why.append(f"GPU {d}: not present")
                elif gg[0]["memory_free_gb"] < step.vram_gb + cfg.vram_margin_gb:
                    why.append(f"GPU {d}: {gg[0]['memory_free_gb']:.1f} GB free; step needs {step.vram_gb} GB + margin "
                               f"{cfg.vram_margin_gb} GB")
    return why


def companions_missing(cfg, expected, keys):
    miss = []
    for k in keys:
        spec = expected["inputs"].get(k) or {}
        p = cfg.input(k)
        for suf in spec.get("companions", []):
            if p and not os.path.exists(p + suf):
                miss.append(f"{k}{suf}")
    return miss


class Runner:
    def __init__(self, cfg: Config, tier: str, only=None, with_deps=False, rerun=False):
        self.cfg = cfg
        self.tier = tier
        self.selected = select(tier, only, with_deps)
        self.rerun = rerun
        self.expected = load_expected()
        self.workdir = cfg.require_workdir(create=True)
        self.cache = HashCache(self.workdir)
        self.results_dir = self.workdir / "results"
        self.results_dir.mkdir(exist_ok=True)
        # full step records with private paths: kept outside results/, which holds only shareable files
        self.state_path = self.workdir / "state.json"
        old = self.results_dir / "state.json"
        if old.exists() and not self.state_path.exists():
            os.rename(old, self.state_path)
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {"steps": {}}
        self.commit = system.git_state().get("commit")
        self.artifacts = {}          # key -> path, available in this run
        self.artifact_origin = {}    # key -> description
        self.artifact_ok = {}        # key -> bool (matches our stored output)
        self.input_state = {}

    # ------------------------------------------------------------------
    def inputs_used(self, order):
        keys = sorted({k for s in order if s.id in self.selected for k in s.inputs})
        for k in keys:
            if k not in self.input_state:
                say(f"  hashing input {k} ...")
                st, got = input_match(self.cfg, self.expected, self.cache, k,
                                      progress=lambda d, t: say(f"    {d / 2**30:.0f}/{t / 2**30:.0f} GiB"))
                self.input_state[k] = {"state": st, "sha256": got}
        return keys

    def register_artifact(self, key, path, origin):
        self.artifacts[key] = str(path)
        self.artifact_origin[key] = origin
        self.artifact_ok[key] = artifact_match(self.expected, self.cache, key, str(path), self.artifact_ok)

    def exact_ok(self, spec):
        bad = []
        for item in spec.get("exact_if", []) or []:
            kind, key = item.split(":", 1)
            if kind == "input":
                if self.input_state.get(key, {}).get("state") != "match":
                    bad.append(item)
            elif kind == "artifact":
                if not self.artifact_ok.get(key):
                    bad.append(item)
        return not bad, bad

    # ------------------------------------------------------------------
    def run(self):
        started = now()
        order = topo_order()
        say(f"replicate run: tier {self.tier}; {len(self.selected)} steps selected; workdir {self.workdir}")
        rules = rule_status(self.cfg)
        self.inputs_used(order)
        budget = sum(s.disk_gb for s in order if s.id in self.selected)
        free = system.disk_free_gb(self.workdir)
        if free - budget < self.cfg.disk_floor_gb:
            raise SystemExit(f"refusing to start: {free:.1f} GB free, plan budget {budget:.1f} GB, floor {self.cfg.disk_floor_gb} GB")
        records = []
        for step in order:
            rec = self.run_step(step, rules)
            records.append(rec)
            self.state["steps"][step.id] = json.loads(json.dumps(rec, default=str))   # full record, private paths included
            self.state_path.write_text(json.dumps(self.state, indent=1))
        finished = now()
        from replicate.report import write_report
        res = write_report(self, records, rules, started, finished)
        return res

    def run_step(self, step, rules):
        spec = self.expected["steps"].get(step.id, {"metrics": []})
        rec = {"id": step.id, "title": step.title, "register": step.register, "tier": step.tier, "kind": step.kind,
               "decision_rule": spec.get("decision_rule", ""), "rule_file": spec.get("rule_file"),
               "info_note": spec.get("info_note"),
               "declared": {"gpu": step.gpu, "vram_gb": step.vram_gb, "ram_gb": step.ram_gb, "disk_gb": step.disk_gb,
                            "network": step.network, "runtime": step.runtime},
               "inputs": {k: self.input_state.get(k, {}).get("state", "not hashed") for k in step.inputs},
               "artifacts_used": {}, "metrics": [], "info": [], "note": step.note, "privacy": step.privacy,
               "code_commit": self.commit}

        def not_run(reason, status="NOT RUN"):
            rec.update(status=status, reason=reason)
            # a step that is not run can still make its artifact available: from a previous run or an intermediate
            for key, rel in step.provides.items():
                prev = self.state["steps"].get(step.id, {})
                prev_art = (prev.get("artifacts") or {}).get(key)
                if key in self.cfg.intermediates:
                    p = self.cfg.intermediates[key]
                    if os.path.exists(p):
                        self.register_artifact(key, p, "supplied intermediate (config 'intermediates')")
                        rec["artifacts_used"][key] = {"origin": "intermediate",
                                                      "matches_ours": self.artifact_ok[key]}
                elif prev_art and prev.get("status") in ("PASS", "FAIL", "INCONCLUSIVE") and os.path.exists(prev_art):
                    self.register_artifact(key, prev_art, f"previous run in this workdir ({prev.get('finished')})")
            say(f"[{step.id}] {status}: {reason}")
            return rec

        prev = self.state["steps"].get(step.id)
        if step.id not in self.selected and prev and prev.get("status") not in (None, "NOT RUN") and prev.get("metrics") is not None:
            # incremental run (--steps): keep the earlier result of this step, say so, and reuse its outputs
            rec = json.loads(json.dumps(prev))
            rec["reused"] = f"result of an earlier run in this workdir (finished {prev.get('finished')}); not re-run now"
            for key, path in (prev.get("artifacts") or {}).items():
                if os.path.exists(path):
                    self.register_artifact(key, path, f"earlier run in this workdir ({prev.get('finished')})")
            say(f"[{step.id}] {rec['status']} (kept from the earlier run)")
            return rec
        if step.id not in self.selected:
            if self.tier == "quick" and step.tier == "full":
                return not_run("full-tier step (GPU, network, container or long); not run in the quick tier")
            return not_run("not selected (--steps)")
        if step.kind == "placeholder":
            return not_run("placeholder: the analysis is being run now; script and expected values are not in the register yet")
        if step.kind == "external":
            return not_run("external step, not run by the harness: procedure in replicate/EXTERNAL_STEPS.md")
        if step.network and not self.cfg.allow_network:
            return not_run("network step and allow_network is false", "REFUSED")
        missing = [k for k in step.needs if k not in self.artifacts]
        if missing:
            roots = sorted(set().union(*(root_missing(k, self.artifacts) for k in missing)))
            return not_run("upstream output not available: " + ", ".join(missing) + ". It depends on " +
                           "; ".join(f"{r} from {PROVIDER[r]}: {route(r)}" for r in roots))
        unconf = [k for k in step.inputs if self.input_state.get(k, {}).get("state") in ("unconfigured", "missing")]
        if unconf:
            return not_run("input not configured or missing: " + ", ".join(unconf), "REFUSED")
        comp = companions_missing(self.cfg, self.expected, step.inputs)
        if comp:
            return not_run("index file missing (it would be created next to the input): " + ", ".join(comp), "REFUSED")
        for r in step.rules:
            st = rules.get(r, {})
            if st.get("not_shipped") and st.get("observed") is None:
                return not_run(f"rule file {r} not shipped (held back: contains a local file name); available to "
                               "organisers on request (then give its folder as rules_extra_dir)", "REFUSED")
            if not st.get("ok"):
                return not_run(f"rule file {r} does not match its recorded sha256", "REFUSED")
        for k in step.needs_input_match:
            if self.input_state.get(k, {}).get("state") != "match":
                spec = (self.expected.get("inputs") or {}).get(k) or {}
                where = f" Get the recorded release: {spec['url']}" if spec.get("url") else ""
                return not_run(f"input {k} is not the release this step was pre-registered against "
                               f"(sha256 does not match the recorded value), so its strata cannot be "
                               f"built and none of its expected values would apply.{where}", "REFUSED")
        if "evo2_weights" in step.inputs and self.input_state.get("evo2_weights", {}).get("state") != "match":
            return not_run("Evo 2 weights sha256 does not match the published LFS id; the unsafe-pickle override is "
                           "only allowed after a match", "REFUSED")
        why = guard(step, self.cfg, self.workdir)
        if why:
            return not_run("resource guard: " + "; ".join(why), "REFUSED")

        sdir = self.workdir / "steps" / step.id
        if sdir.exists():
            if not self.rerun:
                return not_run(f"step folder exists from an earlier run ({sdir}); use --rerun to move it aside", "REFUSED")
            keep = self.workdir / "steps" / "_previous"
            keep.mkdir(parents=True, exist_ok=True)
            os.rename(sdir, keep / f"{step.id}-{int(time.time())}")
        sdir.mkdir(parents=True)
        logdir = self.workdir / "logs" / step.id
        if logdir.exists():
            keep = self.workdir / "logs" / "_previous"
            keep.mkdir(parents=True, exist_ok=True)
            os.rename(logdir, keep / f"{step.id}-{int(time.time())}")
        tmp = self.workdir / "tmp" / step.id
        tmp.mkdir(parents=True, exist_ok=True)
        (tmp / TMP_MARKER).write_text("temporary folder of one step; removed by the harness when the step ends\n")
        ctx = Ctx(self.cfg, step, self.workdir, self.artifacts, logdir, tmp)
        for k in step.needs:
            rec["artifacts_used"][k] = {"origin": self.artifact_origin.get(k), "matches_ours": self.artifact_ok.get(k)}
        rec["started"] = now()
        say(f"[{step.id}] running: {step.title}")
        t0 = time.time()
        gpu_before = system.gpus() if step.gpu else None
        try:
            step.execute(ctx)
            for key, rel in step.provides.items():
                p = (self.workdir / rel[1:]) if rel.startswith("@") else (sdir / rel)
                self.register_artifact(key, p, "produced in this run")
            observed = step.parse(ctx)
            ok, bad = self.exact_ok(spec)
            rows, extra = compare_metrics(spec.get("metrics", []), observed, ok)
            rec.update(status=step_status(rows), metrics=rows, info=extra,
                       exact_conditions={"all_match": ok, "differs": bad})
        except (StepError, Exception) as e:  # noqa: BLE001 - every failure is recorded, none is hidden
            rec.update(status="ERROR", reason=str(e)[:2000])
            (logdir / "harness_traceback.log").write_text(traceback.format_exc())
        finally:
            rec["finished"] = now()
            rec["seconds"] = round(time.time() - t0, 1)
            rec["runs"] = ctx.runs
            rec["measured"] = {"wall_s": rec["seconds"],
                               "peak_rss_gb": max([r.get("peak_rss_gb", 0) for r in ctx.runs] or [0]),
                               "step_folder_gb": round(system.dir_size_gb(sdir), 4)}
            if gpu_before is not None:
                rec["measured"]["gpu_before"] = gpu_before
            if (tmp / TMP_MARKER).exists():
                shutil.rmtree(tmp)      # only the folder this step created, marked above
        rec["artifacts"] = {k: self.artifacts[k] for k in step.provides if k in self.artifacts}
        say(f"[{step.id}] {rec['status']} in {rec['seconds']} s" + (f": {rec.get('reason', '')[:200]}" if rec["status"] == "ERROR" else ""))
        return rec
