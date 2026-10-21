"""Preflight: does this machine meet the requirements to replicate the selected steps?"""
from __future__ import annotations

import json
import os
import shutil

from replicate import system
from replicate.config import REPO_ROOT, ConfigError
from replicate.hashing import HashCache
from replicate.porting import audit as port_audit
from replicate.registry import (ARTIFACT_HASHES, artifact_match, input_match, load_expected, rule_status, select,
                                topo_order)
from replicate.steps import BY_ID, PROVIDER, route

OURS = {"python": "3.13.5", "driver": "615.71.09", "cuda_umd": "13.4", "cuda_toolkit": "13.1",
        "os": "Debian GNU/Linux 13 (trixie)"}
CPU_PACKAGES = ["numpy", "scipy", "pandas", "pysam", "pyyaml"]
GPU_PACKAGES = ["torch", "transformers", "evo2"]
TOOLS = {"bash": None, "zcat": None, "awk": None, "head": None, "tabix": ["P2"], "curl": ["T2-TRIAL-01"]}


class Report:
    def __init__(self):
        self.rows = []

    def add(self, area, item, status, detail=""):
        self.rows.append({"area": area, "item": item, "status": status, "detail": detail})

    def worst(self):
        s = {r["status"] for r in self.rows}
        return "FAIL" if "FAIL" in s else ("WARN" if "WARN" in s else "PASS")

    def table(self):
        w1 = max(len(r["area"]) for r in self.rows)
        w2 = max(len(r["item"]) for r in self.rows)
        out = [f"{'area'.ljust(w1)}  {'item'.ljust(w2)}  status  detail"]
        for r in self.rows:
            out.append(f"{r['area'].ljust(w1)}  {r['item'].ljust(w2)}  {r['status'].ljust(6)}  {r['detail']}")
        return "\n".join(out)


def run_check(cfg, tier="quick", only=None, with_deps=False, hash_inputs=True):
    rep = Report()
    expected = load_expected()
    selected = select(tier, only, with_deps)
    order = [s for s in topo_order() if s.id in selected]
    runnable = [s for s in order if s.kind in ("script", "harness")]
    gpu_steps = [s for s in runnable if s.gpu]

    # workdir
    workdir = None
    try:
        workdir = cfg.require_workdir(create=True)
        rep.add("workdir", "location", "PASS", "outside the repository; the harness writes only here")
    except ConfigError as e:
        rep.add("workdir", "location", "FAIL", str(e))

    if getattr(cfg, "unset", None):
        by_var = {}
        for item, names in cfg.unset.items():
            for n in names:
                by_var.setdefault(n, []).append(item.split(".", 1)[1])
        for n, items in sorted(by_var.items()):
            rep.add("config", f"${{{n}}}", "INFO", f"not set: left unconfigured: {', '.join(items)}")

    # OS and Python
    osi = system.os_info()
    rep.add("system", "OS", "PASS" if osi["system"] == "Linux" else "WARN",
            f"{osi.get('distribution') or osi['system']} {osi['release']} {osi['machine']} (ours: {OURS['os']})")
    probe = system.python_probe(cfg.python)
    pv = probe.get("python")
    if not pv:
        rep.add("python", "interpreter", "FAIL", f"cannot run the analysis interpreter: {probe.get('error')}")
        pk = {}
    else:
        major_minor = tuple(int(x) for x in pv.split(".")[:2])
        st = "PASS" if pv == OURS["python"] else ("WARN" if major_minor >= (3, 12) else "FAIL")
        rep.add("python", "version", st, f"{pv} (ours {OURS['python']}; >= 3.12 required: an analysis script uses "
                "PEP 701 f-strings)")
        pk = probe.get("packages", {})
    lock = system.read_lock(REPO_ROOT / "env" / "requirements_freeze.txt")
    need = CPU_PACKAGES + (GPU_PACKAGES if gpu_steps else [])
    for p in need:
        have, want = pk.get(p), lock.get(p)
        if have is None:
            rep.add("python", p, "FAIL", f"not installed (lock {want})")
        else:
            rep.add("python", p, "PASS" if have == want else "WARN", f"{have} (lock {want})")
    diffs = [k for k, v in lock.items() if pk.get(k) != v]
    quick_lock = REPO_ROOT / "env" / "requirements-quick.txt"
    if not gpu_steps and quick_lock.exists():
        # CPU-only selection: the quick-tier lock (the packages the CPU scripts import) is the one that must match
        lq = system.read_lock(quick_lock)
        dq = [k for k, v in lq.items() if pk.get(k) != v]
        rep.add("python", "lock file (quick)", "PASS" if not dq else "WARN",
                f"{len(lq) - len(dq)}/{len(lq)} packages of env/requirements-quick.txt at the locked version" +
                (f"; differing: {', '.join(dq)}" if dq else ""))
        rep.add("python", "lock file (full)", "INFO",
                f"{len(lock) - len(diffs)}/{len(lock)} packages of env/requirements_freeze.txt installed at the locked "
                "version (the full lock is needed only for GPU steps)")
    else:
        rep.add("python", "lock file", "PASS" if not diffs else "WARN",
                f"{len(lock) - len(diffs)}/{len(lock)} packages at the locked version" +
                (f"; differing: {', '.join(diffs[:10])}{' ...' if len(diffs) > 10 else ''}" if diffs else ""))

    # tools
    for t, users in TOOLS.items():
        used = users is None or any(u in selected for u in users)
        ok = shutil.which(t) is not None
        if used:
            rep.add("tools", t, "PASS" if ok else "FAIL", "found" if ok else f"missing (needed by {', '.join(users or ['shell steps'])})")
    if "ALIGN-01" in selected:
        rep.add("tools", "docker", "PASS" if shutil.which("docker") else "WARN", "for the external alignment step only")

    # GPU
    g = system.gpus()
    cuda = system.cuda_version()
    if g:
        desc = "; ".join(f"{x['index']}: {x['name']} {x['memory_total_gb']:.0f} GB, {x['memory_free_gb']:.1f} GB free"
                         for x in g)
        rep.add("gpu", "devices", "INFO", f"{len(g)} GPU(s): {desc}")
        drv = g[0]["driver"]
        tk = system.cuda_toolkit()
        same = drv == OURS["driver"] and cuda == OURS["cuda_umd"] and tk == OURS["cuda_toolkit"]
        rep.add("gpu", "driver / CUDA", "PASS" if same else "WARN",
                f"driver {drv}, CUDA (driver UMD) {cuda}, toolkit {tk} (ours {OURS['driver']}, {OURS['cuda_umd']}, "
                f"{OURS['cuda_toolkit']})")
        if gpu_steps:
            tc = system.torch_cuda(cfg.python)
            ok = tc.get("cuda_available") is True
            rep.add("gpu", "torch", "PASS" if ok else "FAIL",
                    f"torch {tc.get('torch')} built for CUDA {tc.get('cuda_build')}, GPU visible: {tc.get('cuda_available')}"
                    if "error" not in tc else f"cannot import torch: {tc['error']}")
        procs = system.gpu_compute_processes()
        if procs:
            rep.add("gpu", "other GPU processes", "INFO", f"{len(procs)} compute process(es) already running")
    if gpu_steps:
        need_v = max(s.vram_gb for s in gpu_steps) + cfg.vram_margin_gb
        devs = [d.strip() for d in cfg.cuda_visible_devices.split(",") if d.strip()]
        if not g:
            rep.add("gpu", "for GPU steps", "FAIL", "no NVIDIA GPU found (nvidia-smi)")
        elif len(devs) != 1:
            rep.add("gpu", "for GPU steps", "FAIL", "set cuda_visible_devices to exactly one GPU (two-GPU Evo 2 load failed)")
        else:
            gg = [x for x in g if str(x["index"]) == devs[0]]
            ok = bool(gg) and gg[0]["memory_free_gb"] >= need_v
            rep.add("gpu", "for GPU steps", "PASS" if ok else "FAIL",
                    f"GPU {devs[0]}: {gg[0]['memory_free_gb']:.1f} GB free, largest step needs {need_v:.1f} GB" if gg
                    else f"GPU {devs[0]} not present")
    else:
        rep.add("gpu", "for GPU steps", "PASS", "no GPU step selected" + ("" if g else " (and no GPU present)"))

    # RAM and disk
    total, avail = system.mem_gb()
    if runnable:
        need_r = max(s.ram_gb for s in runnable) + cfg.ram_margin_gb
        if avail is None:
            rep.add("memory", "RAM", "WARN", "cannot read /proc/meminfo")
        else:
            rep.add("memory", "RAM", "PASS" if avail >= need_r else "FAIL",
                    f"{avail:.1f} GB available of {total:.1f} GB; largest step needs {need_r:.1f} GB")
    if workdir:
        budget = sum(s.disk_gb for s in runnable)
        free = system.disk_free_gb(workdir)
        ok = free - budget - cfg.disk_margin_gb >= cfg.disk_floor_gb
        rep.add("disk", "workdir free space", "PASS" if ok else "FAIL",
                f"{free:.1f} GB free; plan budget {budget:.2f} GB + margin {cfg.disk_margin_gb} GB; "
                f"never below {cfg.disk_floor_gb} GB free")

    # inputs
    cache = HashCache(workdir)
    keys = sorted({k for s in runnable for k in s.inputs})
    for k in keys:
        spec = expected["inputs"].get(k, {})
        if hash_inputs:
            st, got = input_match(cfg, expected, cache, k, progress=lambda d, t: print(f"  hashing {k}: {d / 2**30:.0f}/{t / 2**30:.0f} GiB", flush=True))
        else:
            p = cfg.input(k)
            st, got = ("unconfigured", None) if not p else (("present", None) if os.path.exists(p) else ("missing", None))
        users = [s.id for s in runnable if k in s.inputs]
        if st in ("unconfigured", "missing"):
            rep.add("inputs", k, "FAIL", f"{st}; needed by {', '.join(users)}")
            continue
        if st == "match":
            rep.add("inputs", k, "PASS", f"sha256 matches ({spec.get('source', '')})")
        elif st == "differs":
            rep.add("inputs", k, "WARN", f"sha256 differs from ours ({(got or '')[:16]}); steps run, exact metrics become NOT COMPARABLE")
        else:
            rep.add("inputs", k, "INFO", st if not got else f"{st}: {got}")
        for suf in spec.get("companions", []):
            p = cfg.input(k) + suf
            if not os.path.exists(p):
                rep.add("inputs", k + suf, "FAIL", "index missing; it would be created next to the input")

    # intermediates for steps not run in this tier
    produced = {key for s in runnable for key in s.provides}
    missing_for = {}
    for s in runnable:
        for key in s.needs:
            if key not in produced:
                missing_for.setdefault(key, []).append(s.id)
    for key, users in missing_for.items():
        prod = BY_ID[PROVIDER[key]]
        p = cfg.intermediates.get(key)
        if p and os.path.exists(p):
            ok = artifact_match(expected, cache, key, p) if key in ARTIFACT_HASHES else None
            rep.add("intermediates", key, "PASS" if ok else "WARN",
                    f"supplied in place of {prod.id}; " + ("identical to our stored output" if ok else "differs from our stored output"))
        else:
            rep.add("intermediates", key, "WARN",
                    f"produced by {prod.id} ({prod.tier} tier) and not supplied; {', '.join(users)} and the steps "
                    f"downstream of them will be NOT RUN. To get it: {route(key)}")

    # rules and ported code
    for name, v in rule_status(cfg).items():
        users = [s.id for s in runnable if name in s.rules]
        if v.get("not_shipped"):
            if v["ok"]:
                rep.add("rules", name, "PASS", "verified from rules_extra_dir")
            elif v.get("observed") is None:
                rep.add("rules", name, "WARN", "not shipped (held back: contains a local file name); available to "
                        "organisers on request; give its folder as rules_extra_dir" +
                        (f"; {', '.join(users)} will be REFUSED" if users else ""))
            else:
                rep.add("rules", name, "FAIL", "the file in rules_extra_dir does not match its recorded sha256")
        else:
            rep.add("rules", name, "PASS" if v["ok"] else "FAIL",
                    "sha256 matches SHA256SUMS.txt" + (f" (used by {', '.join(users)})" if users else "") if v["ok"]
                    else "sha256 MISMATCH: steps using this rule will be refused")
    bad = port_audit()
    rep.add("code", "ported scripts", "PASS" if not bad else "FAIL",
            "all ported scripts match PORTING.json" if not bad else "; ".join(bad[:5]))
    gs = system.git_state()
    rep.add("code", "git", "INFO" if gs.get("commit") else "WARN",
            f"commit {gs.get('commit')}{' with uncommitted changes' if gs.get('dirty') else ''}" if gs.get("commit")
            else "no commit (results cannot name the code version)")
    rep.add("network", "allow_network", "INFO",
            f"{cfg.allow_network}; network steps: " + ", ".join(s.id for s in order if s.network))

    result = {"tier": tier, "selected_steps": [s.id for s in order], "overall": rep.worst(), "checks": rep.rows}
    if workdir:
        (workdir / "results").mkdir(exist_ok=True)
        (workdir / "results" / "check.json").write_text(json.dumps(result, indent=1))
    return rep, result
