"""Harness machinery: tolerances, write/network guard, resource guard, porting audit, privacy of shipped files."""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ROOT, SANDBOX
from replicate import compare
from replicate.porting import audit


# ------------------------------------------------------------------ tolerances
@pytest.mark.parametrize("obs,exp,tol,ok", [
    (5101, 5101, "exact", True), (5100, 5101, "exact", False),
    (0.0436, 0.043, {"round": 3}, False), (0.0434, 0.043, {"round": 3}, True),
    (1.44e-01, 0.14, {"sigfig": 2}, True), (2.6e-11, 3e-11, {"sigfig": 1}, True), (2.4e-11, 3e-11, {"sigfig": 1}, False),
    (0.687, 0.677, {"abs": 0.02}, True), (0.70, 0.677, {"abs": 0.02}, False),
    (["B", "A"], ["A", "B"], "set", True), (["A", "B", "C"], ["A", "C"], "subset", True), (["A"], ["A", "C"], "subset", False),
    ([0.602, 0.748], [0.602, 0.748], "exact", True), ({"a": 1}, {"a": 1}, "exact", True),
    (0.01, 0.05, {"lt": 0.05}, True), (0.05, 0.05, {"lt": 0.05}, False),
    ("not ranked", "not ranked", "exact", True), (True, True, "exact", True),
])
def test_tolerances(obs, exp, tol, ok):
    assert compare.check(obs, exp, tol) is ok


def test_not_comparable_when_inputs_differ():
    spec = [{"name": "depth", "expected": 47, "tol": "exact"},
            {"name": "het", "expected": True, "tol": "exact", "tol_alt": "exact"}]
    rows, _ = compare.compare_metrics(spec, {"depth": 45, "het": True}, exact_ok=False)
    assert [r["verdict"] for r in rows] == [compare.NC, compare.PASS]
    assert compare.step_status(rows) == "INCONCLUSIVE"
    rows, _ = compare.compare_metrics(spec, {"depth": 45, "het": True}, exact_ok=True)
    assert compare.step_status(rows) == "FAIL"
    rows, extra = compare.compare_metrics(spec, {"het": True, "other": 1}, exact_ok=True)
    assert rows[0]["verdict"] == compare.MISSING and extra[0]["metric"] == "other"


# ------------------------------------------------------------------ write and network guard
def _guarded(tmp_path, code, net="0"):
    work = tmp_path / "work"
    work.mkdir(exist_ok=True)
    script = work / "s.py"
    script.write_text(code)
    env = {"PATH": os.environ["PATH"], "REPL_WORKDIR": str(work), "REPL_WRITE_GUARD": "enforce",
           "REPL_ALLOW_NETWORK": net, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-s", str(SANDBOX), str(script)], cwd=work, env=env,
                          capture_output=True, text=True)


def test_guard_allows_writes_inside_workdir(tmp_path):
    p = _guarded(tmp_path, "open('ok.txt','w').write('x')\nimport os\nos.makedirs('a/b')\nos.remove('ok.txt')\n")
    assert p.returncode == 0, p.stderr


def test_guard_blocks_writes_outside(tmp_path):
    outside = tmp_path / "outside.txt"
    p = _guarded(tmp_path, f"open({str(outside)!r}, 'w').write('x')\n")
    assert p.returncode != 0 and "blocked write outside the workdir" in p.stderr
    assert not outside.exists()


def test_guard_blocks_write_through_symlink(tmp_path):
    target = tmp_path / "input.txt"
    target.write_text("original")
    work = tmp_path / "work"
    work.mkdir()
    os.symlink(target, work / "linked.txt")
    p = _guarded(tmp_path, "open('linked.txt', 'a').write('tampered')\n")
    assert p.returncode != 0
    assert target.read_text() == "original"


def test_guard_blocks_delete_and_rename_outside(tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("keep")
    p = _guarded(tmp_path, f"import os\nos.remove({str(victim)!r})\n")
    assert p.returncode != 0 and victim.exists()
    p = _guarded(tmp_path, f"import os\nos.rename({str(victim)!r}, 'moved.txt')\n")
    assert p.returncode != 0 and victim.exists()


def test_guard_blocks_network(tmp_path):
    p = _guarded(tmp_path, "import socket\nsocket.getaddrinfo('example.org', 443)\n")
    assert p.returncode != 0 and "network not allowed" in p.stderr


# ------------------------------------------------------------------ resource guard
class _Cfg:
    disk_margin_gb, disk_floor_gb, ram_margin_gb, vram_margin_gb = 5.0, 20.0, 2.0, 1.0
    cuda_visible_devices = "0"


def test_resource_guard(monkeypatch, tmp_path):
    from replicate import runner, system
    from replicate.framework import Step
    s = Step("X", "x", "x", "T1", "quick", ram_gb=4, disk_gb=10)
    monkeypatch.setattr(system, "disk_free_gb", lambda p: 100.0)
    monkeypatch.setattr(system, "mem_gb", lambda: (64.0, 32.0))
    assert runner.guard(s, _Cfg, tmp_path) == []
    monkeypatch.setattr(system, "disk_free_gb", lambda p: 25.0)   # 25 - 10 < floor 20
    assert any(w.startswith("disk") for w in runner.guard(s, _Cfg, tmp_path))
    monkeypatch.setattr(system, "disk_free_gb", lambda p: 100.0)
    monkeypatch.setattr(system, "mem_gb", lambda: (64.0, 5.0))    # 5 < 4 + 2
    assert any(w.startswith("RAM") for w in runner.guard(s, _Cfg, tmp_path))
    g = Step("G", "g", "g", "M", "full", gpu=True, vram_gb=16)
    monkeypatch.setattr(system, "mem_gb", lambda: (64.0, 60.0))
    monkeypatch.setattr(system, "gpus", lambda: [{"index": 0, "memory_free_gb": 10.0}])
    assert any(w.startswith("GPU 0") for w in runner.guard(g, _Cfg, tmp_path))
    class Two(_Cfg):
        cuda_visible_devices = "0,1"
    monkeypatch.setattr(system, "gpus", lambda: [{"index": 0, "memory_free_gb": 24.0}, {"index": 1, "memory_free_gb": 24.0}])
    assert any("more than one device" in w for w in runner.guard(g, Two, tmp_path))


# ------------------------------------------------------------------ porting audit
def test_ported_scripts_differ_only_on_logged_lines():
    assert audit() == []


def test_no_unported_path_constant_in_ported_code():
    for p in (ROOT / "replicate" / "analysis").rglob("*"):
        if p.is_file() and p.suffix in (".py", ".sh"):
            t = p.read_text()
            assert "/home/" not in t and "/media/" not in t and "HACKATON" not in t and "expanduser" not in t, p


# ------------------------------------------------------------------ privacy of shipped files
# The candidate's coordinates, protein change and proband label are our published Track 1 answer and are not
# checked here; what may never ship is checked: sequencing data, local user and session paths, secrets.
SECRET = re.compile(r"(hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})")
# A folder of a real local user (home, macOS user, removable-disk mount, temporary session folder): the public copies
# keep the path layout but carry [redacted] (or a <placeholder>) where the user, disk or session name was.
USER_PATH = re.compile(r"/(?:home|Users|media)/(?!\[redacted\]|<|\()[^/\s'\"`]+|/private/tmp/(?!\[redacted\]|<|\()[^/\s'\"`]+|-Users-[A-Za-z]")
# The child's sequencing data never ships, in any form: no VCF, BAM, CRAM or FASTQ (or their indexes).
DATA_FILE = re.compile(r"\.(?:vcf|vcf\.gz|vcf\.bgz|bcf|bam|bai|cram|crai|fastq|fq|fastq\.gz|fq\.gz|tbi|csi)$", re.I)
# every shipped file
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}


def _files():
    for f in ROOT.rglob("*"):
        if f.is_file() and not SKIP_PARTS & set(f.relative_to(ROOT).parts) and f.name != "config.yaml":
            yield f


def test_shipped_files_hold_no_sequencing_data_local_path_or_secret():
    """The candidate's coordinates, protein change and proband label are our published answer and may appear;
    the child's data files, our machines' user and session paths and secrets may not."""
    hits = []
    for f in _files():
        raw = f.read_bytes()
        text = raw.decode(errors="ignore")
        rel = f.relative_to(ROOT)
        if DATA_FILE.search(f.name) or raw.startswith(b"##fileformat=VCF") or raw[:4] == b"BAM\x01":
            hits.append(f"{rel}: sequencing data file")
        if SECRET.search(text):
            hits.append(f"{rel}: secret-like string")
        if USER_PATH.search(text):
            hits.append(f"{rel}: path with a local user, disk or session name")
    assert not hits, hits


# ------------------------------------------------------------------ messages and config for an outsider
def test_held_back_rule_is_reported_as_not_shipped(tmp_path):
    from replicate import config, registry
    cfg = config.Config({"workdir": str(tmp_path / "w")}, None)
    st = registry.rule_status(cfg)["CNV_RULE_v1.md"]
    assert st["not_shipped"] and st["observed"] is None and not st["ok"]


def test_unset_variable_leaves_input_unconfigured(monkeypatch, tmp_path):
    from replicate import config
    monkeypatch.delenv("MVA_TEST_UNSET", raising=False)
    monkeypatch.setenv("MVA_TEST_SET", str(tmp_path))
    cfg = config.Config({"workdir": str(tmp_path / "w"), "inputs": {"vcf": "${MVA_TEST_SET}/a.vcf.gz",
                                                                   "evo2_weights": "${MVA_TEST_UNSET}/e.pt"}}, None)
    assert cfg.input("vcf") == f"{tmp_path}/a.vcf.gz" and cfg.input("evo2_weights") is None
    assert cfg.unset == {"inputs.evo2_weights": ["MVA_TEST_UNSET"]}
    with pytest.raises(config.ConfigError):
        config.Config({"workdir": "${MVA_TEST_UNSET}/w"}, None)


def test_missing_intermediate_names_its_root_and_route():
    from replicate.steps import ROUTES, root_missing
    assert root_missing("candidate", {}) == {"gnomad_parts"}
    assert root_missing("ranking_v1", {"gnomad_parts": "x"}) == {"consequence_orig"}
    assert "BLIND-01B" in ROUTES["gnomad_parts"] and "organisers approve" in ROUTES["gnomad_parts"]


def test_candidate_protein_changes_are_compared_by_digest():
    from replicate.steps import protein_changes_digest
    assert protein_changes_digest(["X2Y", "A1B"]) == hashlib.sha256(b"A1B,X2Y").hexdigest()


def test_s01_length_normalised_ratio(tmp_path):
    from replicate import steps
    a = 1000
    lines = [f"chr{i}: mapped={a} ratio_to_autosome_mean=1.0000" for i in (15, 18, 19)] + [f"autosome_mean_mapped={a}"]

    class C:
        def stdout(self, name):
            return "\n".join(lines) + "\n"
    m = steps.s01_parse(C())
    L = steps.GRCH38_UNGAPPED
    auto = sum(L[f"chr{i}"] for i in range(1, 23))
    assert m["chr19_ratio_to_autosome"] == 1.0
    assert m["chr19_per_mb_ratio_to_autosome"] == round((a / L["chr19"]) / (22 * a / auto), 4)
    assert m["chr19_per_mb_ratio_to_autosome"] > m["chr18_per_mb_ratio_to_autosome"]


def test_answer_data_warns_and_local_paths_fail(tmp_path):
    """leak_scan.py reports the proband label as a warning (published answer) and a local user folder as a failure."""
    label = "PRO" + "BAND" + "99"                    # built at run time, so this test file does not hold one
    (tmp_path / "a.md").write_text(f"proband {label}\n")
    scan = lambda: subprocess.run([sys.executable, str(ROOT / "tools" / "leak_scan.py"), str(tmp_path), "--quiet"],
                                  capture_output=True, text=True)
    r = scan()
    assert r.returncode == 0 and "1 warning(s)" in r.stdout
    (tmp_path / "b.md").write_text("/home/" + "someone" + "/data\n")
    r = scan()
    assert r.returncode == 1 and "FAIL local user folder: 1" in r.stdout
    (tmp_path / "b.md").unlink()
    (tmp_path / "x.vcf").write_text("##fileformat=VCFv4.2\n")
    assert scan().returncode == 1
