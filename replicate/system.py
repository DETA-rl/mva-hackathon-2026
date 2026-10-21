"""Probes of the machine: OS, memory, disk, GPUs, external tools, Python packages, git state."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

from replicate.config import REPO_ROOT

GB = 1024 ** 3


def mem_gb():
    """(total, available) in GiB from /proc/meminfo; (None, None) where unavailable."""
    try:
        info = {}
        with open("/proc/meminfo") as fh:
            for line in fh:
                k, v = line.split(":", 1)
                info[k] = int(v.split()[0]) * 1024
        return info["MemTotal"] / GB, info.get("MemAvailable", info.get("MemFree", 0)) / GB
    except (OSError, KeyError, ValueError):
        return None, None


def disk_free_gb(path: Path) -> float:
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    return shutil.disk_usage(p).free / GB


def dir_size_gb(path: Path) -> float:
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp):
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    return total / GB


def gpus():
    """List of dicts (index, name, memory_total_gb, memory_used_gb, memory_free_gb, driver), or [] if no nvidia-smi."""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return []
    try:
        out = subprocess.run([exe, "--query-gpu=index,name,memory.total,memory.used,memory.free,driver_version",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    res = []
    for line in out.strip().splitlines():
        p = [x.strip() for x in line.split(",")]
        if len(p) < 6:
            continue
        res.append({"index": int(p[0]), "name": p[1], "memory_total_gb": float(p[2]) / 1024,
                    "memory_used_gb": float(p[3]) / 1024, "memory_free_gb": float(p[4]) / 1024, "driver": p[5]})
    return res


def cuda_version():
    """CUDA version the driver supports (nvidia-smi header: 'CUDA Version' or, newer drivers, 'CUDA UMD Version')."""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None
    try:
        out = subprocess.run([exe], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"CUDA (?:UMD )?Version:\s*([0-9.]+)", out)
    return m.group(1) if m else None


def cuda_toolkit():
    """nvcc release, if a CUDA toolkit is on PATH or in /usr/local/cuda."""
    exe = shutil.which("nvcc") or ("/usr/local/cuda/bin/nvcc" if os.path.exists("/usr/local/cuda/bin/nvcc") else None)
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"release ([0-9.]+)", out)
    return m.group(1) if m else None


def torch_cuda(python: str):
    """torch version, the CUDA it was built for, and whether it sees a GPU, in the analysis interpreter."""
    code = ("import json\ntry:\n import torch\n print(json.dumps({'torch': torch.__version__, 'cuda_build': torch.version.cuda,"
            " 'cuda_available': torch.cuda.is_available()}))\nexcept Exception as e:\n print(json.dumps({'error': str(e)[:200]}))")
    try:
        out = subprocess.run([python, "-s", "-c", code], capture_output=True, text=True, timeout=300).stdout
        return json.loads(out.strip().splitlines()[-1])
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired) as e:
        return {"error": str(e)[:200]}


def gpu_compute_processes():
    exe = shutil.which("nvidia-smi")
    if not exe:
        return []
    try:
        out = subprocess.run([exe, "--query-compute-apps=pid,gpu_uuid,used_memory", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in out.strip().splitlines() if line.strip()]


def tool_versions(names):
    res = {}
    for n in names:
        exe = shutil.which(n)
        res[n] = exe is not None
    return res


_PROBE = r"""
import json, platform, sys
import importlib.metadata as md
pk = {}
for d in md.distributions():
    try:
        pk[d.metadata["Name"].lower().replace("_", "-")] = d.version
    except Exception:
        pass
print(json.dumps({"python": platform.python_version(), "implementation": platform.python_implementation(),
                  "executable": sys.executable, "packages": pk}))
"""


def python_probe(python: str):
    """Version and installed packages of the interpreter that runs the analysis scripts."""
    try:
        out = subprocess.run([python, "-s", "-c", _PROBE], capture_output=True, text=True, timeout=120)
        return json.loads(out.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        return {"error": str(e)}


def read_lock(path: Path):
    lock = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, ver = line.split("==", 1)
        lock[name.strip().lower().replace("_", "-")] = ver.strip()
    return lock


def git_state():
    def g(*args):
        try:
            r = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, timeout=30)
            return r.stdout.strip() if r.returncode == 0 else None
        except OSError:
            return None
    commit = g("rev-parse", "HEAD")
    dirty = g("status", "--porcelain", "--untracked-files=no")
    return {"commit": commit, "dirty": bool(dirty) if dirty is not None else None}


def os_info():
    return {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
            "distribution": _os_release()}


def _os_release():
    try:
        for line in open("/etc/os-release"):
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return None
