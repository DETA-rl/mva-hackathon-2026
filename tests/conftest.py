import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

ANALYSIS = ROOT / "replicate" / "analysis"
SANDBOX = ROOT / "replicate" / "_sandbox" / "run.py"


def run_script(script, workdir, args=(), env=None, cwd=None, check=True):
    """Run a ported analysis script the way the harness does (guarded, cwd = a folder inside workdir)."""
    e = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", ""), "PYTHONHASHSEED": "0",
         "PYTHONDONTWRITEBYTECODE": "1", "REPL_WORKDIR": str(workdir), "REPL_OUT": str(cwd or workdir),
         "REPL_WRITE_GUARD": "enforce", "REPL_ALLOW_NETWORK": "0", "TMPDIR": str(workdir)}
    e.update({k: str(v) for k, v in (env or {}).items()})
    path = script if os.path.isabs(str(script)) else ANALYSIS / script
    p = subprocess.run([sys.executable, "-s", str(SANDBOX), str(path), *map(str, args)], cwd=str(cwd or workdir),
                       env=e, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise AssertionError(f"{script} failed:\n{p.stderr[-3000:]}")
    return p


def load_namespace(script, env):
    """Tables and functions of a consequence script (text before its per-call loop), as validate_consequence.py does."""
    old = {k: os.environ.get(k) for k in env}
    os.environ.update({k: str(v) for k, v in env.items()})
    try:
        text = open(ANALYSIS / script).read().split("\nrows = []")[0]
        ns = {"__name__": "x"}
        exec(compile(text, str(script), "exec"), ns)
        return ns
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture
def toy(tmp_path):
    """Toy genome and annotation in tmp_path; returns (seq, transcripts, paths)."""
    import toyworld as tw
    seq, txs = tw.build_genome()
    fa = tmp_path / "toy.fa"
    tw.write_fasta(str(fa), seq)
    gtf = tmp_path / "gencode.v44.basic.annotation.gtf.gz"
    tw.write_gtf(str(gtf), txs)
    return seq, txs, {"fasta": fa, "gtf": gtf, "dir": tmp_path}
