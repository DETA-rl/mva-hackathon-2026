"""Expected values, DAG order, step selection and hash matching shared by check, plan and run."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from replicate.config import REPO_ROOT
from replicate.framework import RULES
from replicate.hashing import HashCache
from replicate.steps import BY_ID, PROVIDER, STEPS

EXPECTED_PATH = REPO_ROOT / "replicate" / "expected.yaml"

# artifact key -> stored-output hash keys in expected.yaml (for exact_if and supplied intermediates)
ARTIFACT_HASHES = {
    "child_exonic_calls": {"": "child_exonic_calls"},
    "gnomad_parts": {f"child_exonic_gnomad_exomes.part{k}.tsv": f"gnomad_part{k}" for k in range(4)},
    "consequence_orig": {"": "consequence_orig"},
    "consequence_fixed": {"": "consequence_fixed"},
    "ranking_v1": {"": "ranking_v1"}, "ranking_v2": {"": "ranking_v2"}, "ranking_v3": {"": "ranking_v3"},
    "ranking_v4": {"": "ranking_v4"}, "ranking_v4b": {"": "ranking_v4b"},
    "ranking_v1_fixed": {"": "ranking_v1_fixed"}, "ranking_v2_fixed": {"": "ranking_v2_fixed"},
    "ranking_v3_fixed": {"": "ranking_v3_fixed"}, "ranking_v4_fixed": {"": "ranking_v4_fixed"},
    "controls_rule": {"": "controls_rule"},
    "evo2_control_scores": {"": "evo2_control_scores"},
    "protein_controls_dir": {"controls.tsv": "protein_controls"},
    "protein_scores": {"": "protein_scores"},
    "spikein_trials": {"trials.tsv": "spikein_trials_tsv", "alleles.tsv": "spikein_alleles_tsv"},
}
# artifacts with no stored hash: they match when the artifacts they are derived from match
DERIVED_MATCH = {"candidate": ["consequence_fixed", "ranking_v4b_fixed"],
                 "ranking_v4b_fixed": ["ranking_v3_fixed"]}       # no stored copy: deterministic from its input


def load_expected():
    with open(EXPECTED_PATH) as fh:
        return yaml.safe_load(fh)


def topo_order():
    order, seen = [], set()

    def visit(s, stack=()):
        if s.id in seen:
            return
        if s.id in stack:
            raise RuntimeError(f"cycle at {s.id}")
        for k in s.needs:
            if k in PROVIDER:
                visit(BY_ID[PROVIDER[k]], stack + (s.id,))
        seen.add(s.id)
        order.append(s)
    for s in STEPS:
        visit(s)
    return order


def deps_of(step):
    return sorted({PROVIDER[k] for k in step.needs if k in PROVIDER})


def select(tier: str, only=None, with_deps=False):
    """Steps selected to run. quick = steps of tier quick; full = every step."""
    tiers = {"quick": {"quick"}, "full": {"quick", "full"}}[tier]
    chosen = {s.id for s in STEPS if s.tier in tiers}
    if only:
        unknown = [x for x in only if x not in BY_ID]
        if unknown:
            raise SystemExit(f"unknown step id(s): {', '.join(unknown)}")
        want = set(only)
        if with_deps:
            stack = list(want)
            while stack:
                for d in deps_of(BY_ID[stack.pop()]):
                    if d not in want:
                        want.add(d)
                        stack.append(d)
        chosen = want
    return chosen


def rule_status(cfg):
    """sha256 of each rule file vs rules/SHA256SUMS.txt (and the per-rule .sha256 files)."""
    sums = {}
    for line in open(RULES / "SHA256SUMS.txt"):
        p = line.split()
        if len(p) == 2:
            sums[p[1]] = p[0]
    res = {}
    from replicate.hashing import sha256_file
    for name, want in sums.items():
        f = RULES / name
        got = sha256_file(f) if f.exists() else None
        per = RULES / (name[:-3] + ".sha256")
        per_hashes = set()
        if per.exists():
            per_hashes = {w for w in per.read_text().split() if len(w) == 64}
        res[name] = {"expected": want, "observed": got, "ok": got == want and (not per_hashes or got in per_hashes),
                     "per_rule_file": sorted(per_hashes)}
    # rules referenced in the register but not shipped
    for per in RULES.glob("*.sha256"):
        name = per.name[:-7] + ".md"
        if name not in res:
            extra = cfg.rules_extra_dir / name if cfg.rules_extra_dir else None
            want = [w for w in per.read_text().split() if len(w) == 64]
            got = sha256_file(extra) if extra and extra.exists() else None
            res[name] = {"expected": want[0] if want else None, "observed": got,
                         "ok": bool(got and got in want), "not_shipped": True}
    return res


def input_match(cfg, expected, cache: HashCache, key, progress=None):
    """(state, detail): state in match | differs | missing | unconfigured | no_expected."""
    spec = expected["inputs"].get(key)
    p = cfg.input(key)
    if not p:
        return "unconfigured", None
    if not os.path.exists(p):
        return "missing", None
    if spec is None:
        return "no_expected", None
    if "files" in spec:
        bad = []
        for fn, want in spec["files"].items():
            fp = os.path.join(p, fn)
            if not os.path.exists(fp):
                bad.append(f"{fn} missing")
            elif cache.sha256(fp, progress) != want:
                bad.append(f"{fn} differs")
        return ("match", None) if not bad else ("differs", "; ".join(bad))
    if not cfg.hash_large_inputs and os.path.getsize(p) > (20 << 30):
        size = spec.get("size")
        return ("unhashed", f"size {os.path.getsize(p)}" + ("" if size is None else f" (expected {size})"))
    got = cache.sha256(p, progress)
    return ("match" if got == spec["sha256"] else "differs"), got


def artifact_match(expected, cache: HashCache, key, path, known=None):
    if key in DERIVED_MATCH:
        known = known or {}
        return all(known.get(k) for k in DERIVED_MATCH[key])
    m = ARTIFACT_HASHES.get(key)
    if not m or path is None:
        return False
    for rel, hkey in m.items():
        fp = Path(path) / rel if rel else Path(path)
        if not fp.exists() or cache.sha256(str(fp)) != expected["artifacts"][hkey]["sha256"]:
            return False
    return True
