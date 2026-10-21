"""Configuration: config.yaml (see config.example.yaml) plus environment overrides.

Precedence (highest first): command-line --config path, $REPLICATE_CONFIG, ./config.yaml in the repo.
Individual values can be overridden with environment variables:
  REPLICATE_WORKDIR, REPLICATE_PYTHON, REPLICATE_CUDA_VISIBLE_DEVICES, REPLICATE_ALLOW_NETWORK (0/1),
  REPLICATE_INPUT_<KEY>=path, REPLICATE_INTERMEDIATE_<KEY>=path   (KEY in upper case, e.g. REPLICATE_INPUT_VCF)
Values may use ~ and ${ENV_VAR}. An input or intermediate whose path uses an unset variable is left unconfigured
(`check` lists it); an unset variable anywhere else is an error.
No default in this file points at a patient file: every input path must be supplied by the user.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKER = ".replicate_workdir"

DEFAULTS = {
    "workdir": None,
    "python": None,
    "cuda_visible_devices": "0",
    "allow_network": False,
    "disk_margin_gb": 5.0,
    "disk_floor_gb": 20.0,
    "ram_margin_gb": 2.0,
    "vram_margin_gb": 1.0,
    "write_guard": "enforce",
    "hash_large_inputs": True,
    "rules_extra_dir": None,
    "inputs": {},
    "intermediates": {},
}


class ConfigError(Exception):
    pass


def _expand(v):
    if isinstance(v, str):
        def sub(m):
            name = m.group(1)
            if name not in os.environ:
                raise ConfigError(f"environment variable {name} is used in the config but not set")
            return os.environ[name]
        return os.path.expanduser(re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", sub, v))
    if isinstance(v, dict):
        return {k: _expand(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_expand(x) for x in v]
    return v


class Config:
    def __init__(self, data: dict, path: Path | None):
        self.path = path
        d = dict(DEFAULTS)
        d.update({k: v for k, v in (data or {}).items() if v is not None or k not in d})
        d["inputs"] = dict(d.get("inputs") or {})
        d["intermediates"] = dict(d.get("intermediates") or {})
        for k, v in os.environ.items():
            if k.startswith("REPLICATE_INPUT_"):
                d["inputs"][k[len("REPLICATE_INPUT_"):].lower()] = v
            elif k.startswith("REPLICATE_INTERMEDIATE_"):
                d["intermediates"][k[len("REPLICATE_INTERMEDIATE_"):].lower()] = v
        for key, env in [("workdir", "REPLICATE_WORKDIR"), ("python", "REPLICATE_PYTHON"),
                         ("cuda_visible_devices", "REPLICATE_CUDA_VISIBLE_DEVICES")]:
            if os.environ.get(env):
                d[key] = os.environ[env]
        if os.environ.get("REPLICATE_ALLOW_NETWORK") is not None:
            d["allow_network"] = os.environ["REPLICATE_ALLOW_NETWORK"] in ("1", "true", "yes")
        # an input or intermediate whose path uses an unset variable (for example ${MVA_MODELS} in a quick-tier run)
        # is left unconfigured and listed by `check`; an unset variable anywhere else stays an error
        self.unset = {}
        for sect in ("inputs", "intermediates"):
            for k, v in list(d[sect].items()):
                names = re.findall(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", v) if isinstance(v, str) else []
                missing = [n for n in names if n not in os.environ]
                if missing:
                    self.unset[f"{sect}.{k}"] = missing
                    d[sect][k] = None
        d = _expand(d)
        self.data = d
        self.workdir = Path(d["workdir"]).resolve() if d["workdir"] else None
        self.python = d["python"] or sys.executable
        self.cuda_visible_devices = str(d["cuda_visible_devices"])
        self.allow_network = bool(d["allow_network"])
        self.disk_margin_gb = float(d["disk_margin_gb"])
        self.disk_floor_gb = float(d["disk_floor_gb"])
        self.ram_margin_gb = float(d["ram_margin_gb"])
        self.vram_margin_gb = float(d["vram_margin_gb"])
        self.write_guard = d["write_guard"]
        self.hash_large_inputs = bool(d["hash_large_inputs"])
        self.rules_extra_dir = Path(d["rules_extra_dir"]) if d["rules_extra_dir"] else None
        self.inputs = {k: str(v) for k, v in d["inputs"].items() if v}
        self.intermediates = {k: str(v) for k, v in d["intermediates"].items() if v}

    def input(self, key):
        return self.inputs.get(key)

    def require_workdir(self, create=False) -> Path:
        w = self.workdir
        if w is None:
            raise ConfigError("workdir is not set (config 'workdir' or REPLICATE_WORKDIR)")
        repo = REPO_ROOT.resolve()
        if w == repo or repo in w.parents:
            raise ConfigError(f"workdir must be outside the repository ({repo})")
        if w.exists() and any(w.iterdir()) and not (w / MARKER).exists():
            raise ConfigError(f"workdir {w} exists, is not empty and was not created by this harness; choose an empty folder")
        if create:
            w.mkdir(parents=True, exist_ok=True)
            m = w / MARKER
            if not m.exists():
                m.write_text("created by the MVA replication harness; it writes only inside this folder\n")
        return w


def load(path: str | None = None) -> Config:
    p = path or os.environ.get("REPLICATE_CONFIG")
    p = Path(p) if p else REPO_ROOT / "config.yaml"
    if not p.exists():
        if path or os.environ.get("REPLICATE_CONFIG"):
            raise ConfigError(f"config file not found: {p}")
        return Config({}, None)
    with open(p) as fh:
        data = yaml.safe_load(fh) or {}
    return Config(data, p)
