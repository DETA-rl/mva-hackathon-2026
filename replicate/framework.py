"""Step model, artifact resolution and script execution."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from replicate.config import REPO_ROOT, Config

ANALYSIS = REPO_ROOT / "replicate" / "analysis"
SANDBOX = REPO_ROOT / "replicate" / "_sandbox" / "run.py"
HELPERS = REPO_ROOT / "replicate" / "helpers"
RULES = REPO_ROOT / "rules"


class StepError(Exception):
    pass


class Refused(Exception):
    pass


@dataclass
class Step:
    id: str                       # register ID, or register ID + suffix for sub-steps
    title: str
    register: str                 # register entry the expected values come from
    track: str                    # T1, T2, M (models), H (harness)
    tier: str                     # quick | full
    kind: str = "script"          # script | harness | external | placeholder
    gpu: bool = False
    vram_gb: float | None = 0.0   # None: not recorded (external steps only; the harness never runs them)
    ram_gb: float | None = 1.0
    disk_gb: float | None = 0.1
    network: bool = False
    runtime: str = "unknown"
    inputs: tuple = ()            # config input keys
    needs_input_match: tuple = ()  # inputs whose sha256 must match the record before the step may run
    needs: tuple = ()             # artifact keys consumed
    provides: dict = field(default_factory=dict)   # artifact key -> path relative to the step folder
    rules: tuple = ()             # rule files whose sha256 must match before the step may run
    scripts: tuple = ()           # analysis scripts (relative to replicate/analysis; as_run/... for external steps)
    execute: Callable | None = None
    parse: Callable | None = None
    note: str = ""
    privacy: str = "public"       # public | patient (step reads patient-derived data)

    def describe(self):
        return {"id": self.id, "title": self.title, "register": self.register, "track": self.track,
                "tier": self.tier, "kind": self.kind, "gpu": self.gpu, "vram_gb": self.vram_gb,
                "ram_gb": self.ram_gb, "disk_gb": self.disk_gb, "network": self.network,
                "runtime": self.runtime, "inputs": list(self.inputs), "needs_input_match": list(self.needs_input_match),
                "needs": list(self.needs),
                "provides": dict(self.provides), "rules": list(self.rules), "scripts": list(self.scripts),
                "privacy": self.privacy, "note": self.note}


class Ctx:
    """What a step sees while it runs."""

    def __init__(self, cfg: Config, step: Step, workdir: Path, artifacts: dict, logdir: Path, tmpdir: Path):
        self.cfg = cfg
        self.step = step
        self.workdir = workdir
        self.dir = workdir / "steps" / step.id
        self.private = workdir / "private"
        self.artifacts = artifacts      # key -> absolute path
        self.logdir = logdir
        self.tmpdir = tmpdir
        self.runs = []                  # one record per script call
        self.notes = []

    # inputs and artifacts -------------------------------------------------
    def input(self, key) -> str:
        p = self.cfg.input(key)
        if not p:
            raise StepError(f"input '{key}' is not configured")
        return p

    def artifact(self, key) -> str:
        if key not in self.artifacts:
            raise StepError(f"artifact '{key}' is not available")
        return self.artifacts[key]

    def link(self, name: str, target: str):
        """Make `target` readable inside the step folder under `name` (a symlink; writes through it are blocked)."""
        dst = self.dir / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_symlink() or dst.exists():
            if dst.is_symlink() and os.path.realpath(dst) == os.path.realpath(target):
                return dst
            raise StepError(f"step folder already has {name}")
        os.symlink(os.path.abspath(target), dst)
        return dst

    def path(self, rel) -> Path:
        return self.dir / rel

    # execution -------------------------------------------------------------
    def base_env(self, extra=None):
        keep = ("PATH", "HOME", "LANG", "LC_ALL", "USER", "LOGNAME", "SHELL", "TERM", "LD_LIBRARY_PATH")
        env = {k: os.environ[k] for k in keep if k in os.environ}
        cache = self.tmpdir / "cache"
        cache.mkdir(parents=True, exist_ok=True)
        env.update({
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "TMPDIR": str(self.tmpdir),
            "REPL_WORKDIR": str(self.workdir),
            "REPL_OUT": str(self.dir),
            "REPL_WRITE_GUARD": self.cfg.write_guard,
            "REPL_ALLOW_NETWORK": "1" if (self.step.network and self.cfg.allow_network) else "0",
            "XDG_CACHE_HOME": str(cache),
            "HF_HOME": str(cache / "huggingface"),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "TORCH_HOME": str(cache / "torch"),
            "TRITON_CACHE_DIR": str(cache / "triton"),
            "CUDA_CACHE_PATH": str(cache / "nv"),
            "MPLCONFIGDIR": str(cache / "mpl"),
            "CUDA_VISIBLE_DEVICES": self.cfg.cuda_visible_devices if self.step.gpu else "",
        })
        pybin = str(Path(self.cfg.python).parent)
        env["PATH"] = pybin + os.pathsep + env.get("PATH", "")
        if extra:
            env.update({k: str(v) for k, v in extra.items()})
        return env

    def run_py(self, script: str, args=(), env=None, name=None, cwd=None, timeout=None):
        """Run replicate/analysis/<script> under the guard, cwd = step folder, stdout/stderr to the logs."""
        path = ANALYSIS / script
        cmd = [self.cfg.python, "-s", str(SANDBOX), str(path), *[str(a) for a in args]]
        return self._run(cmd, env, name or Path(script).stem, cwd, timeout, script)

    def run_helper(self, script: str, args=(), env=None, name=None):
        """Run harness code (replicate/helpers/<script>) under the same guard; not an analysis script."""
        path = HELPERS / script
        cmd = [self.cfg.python, "-s", str(SANDBOX), str(path), *[str(a) for a in args]]
        return self._run(cmd, env, name or Path(script).stem, None, None, "helpers/" + script)

    def run_sh(self, script: str, args=(), env=None, name=None, cwd=None, timeout=None):
        path = ANALYSIS / script
        cmd = ["bash", str(path), *[str(a) for a in args]]
        return self._run(cmd, env, name or Path(script).stem, cwd, timeout, script)

    def _run(self, cmd, env, name, cwd, timeout, script):
        self.dir.mkdir(parents=True, exist_ok=True)
        self.logdir.mkdir(parents=True, exist_ok=True)
        out_p = self.logdir / f"{name}.stdout.log"
        err_p = self.logdir / f"{name}.stderr.log"
        t0 = time.time()
        with open(out_p, "w") as so, open(err_p, "w") as se:
            p = subprocess.Popen(cmd, cwd=str(cwd or self.dir), env=self.base_env(env), stdout=so, stderr=se)
            try:
                _, status, ru = os.wait4(p.pid, 0)
            except KeyboardInterrupt:
                p.terminate()
                raise
            p.returncode = os.waitstatus_to_exitcode(status)
        dt = time.time() - t0
        # ru_maxrss: kilobytes on Linux (largest resident set of this process or a descendant it waited for)
        rss_gb = ru.ru_maxrss / (1024 ** 2) if os.uname().sysname == "Linux" else ru.ru_maxrss / (1024 ** 3)
        rec = {"script": script, "name": name, "returncode": p.returncode, "seconds": round(dt, 1),
               "peak_rss_gb": round(rss_gb, 2),
               "stdout_log": str(out_p.relative_to(self.workdir)), "stderr_log": str(err_p.relative_to(self.workdir))}
        self.runs.append(rec)
        if p.returncode != 0:
            tail = err_p.read_text()[-1500:]
            raise StepError(f"{script} exited with code {p.returncode}; stderr tail:\n{tail}")
        return out_p.read_text()

    def stdout(self, name) -> str:
        return (self.logdir / f"{name}.stdout.log").read_text()

    def save_patient_json(self, name, obj):
        self.private.mkdir(parents=True, exist_ok=True)
        p = self.private / name
        p.write_text(json.dumps(obj, indent=1))
        return p


def copy_into(ctx: Ctx, rel_in_analysis: str, dst_rel: str):
    """Copy a shipped file (for example the modified Evo 2 config) into the step folder."""
    src = ANALYSIS / rel_in_analysis
    dst = ctx.dir / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst
