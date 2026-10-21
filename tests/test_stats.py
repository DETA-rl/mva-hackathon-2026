"""AUC and stratified bootstrap of the calibration scripts (protein_calibration.py, evo2_auc_bootstrap.py),
checked against an independent Mann-Whitney computation and against the CALIBRATION_RULE.md thresholds."""
import ast
import random
import re

import pytest
from scipy.stats import mannwhitneyu

from conftest import run_script
from replicate.steps import verdict


def _scores(tmp, P, B, child=(-1.0, 1.0, 0.5)):
    lines = ["gene\tpos\tref\talt\tlabel\tvcf_pos\tesm1v_llr\tesm2_llr\tam"]
    for k, v in enumerate(P):
        lines.append(f"G{k}\t{k + 1}\tA\tV\t1\t{k}\t{-v}\t{-v}\t{v}")
    for k, v in enumerate(B):
        lines.append(f"H{k}\t{k + 1}\tA\tV\t0\t{k}\t{-v}\t{-v}\t{v}")
    lines.append(f"CHILD\t1\tN\tK\tNA\t1\t{child[0]}\t{child[1]}\t{child[2]}")
    (tmp / "scores.tsv").write_text("\n".join(lines) + "\n")
    return tmp / "scores.tsv"


def _parse(out):
    res = {}
    for name, auc, lo, hi, v in re.findall(r"^(\S+): nP=\d+ nB=\d+ AUC=([\d.]+) CI=\[([\d.]+),([\d.]+)\] -> (\S+)", out, re.M):
        res[name.rstrip(":")] = (float(auc), float(lo), float(hi), v)
    return res


def test_auc_matches_mann_whitney(tmp_path):
    rng = random.Random(3)
    P = [rng.gauss(1.0, 1.0) for _ in range(40)]
    B = [rng.gauss(0.0, 1.0) for _ in range(45)]
    out = run_script("models/protein_rule/protein_calibration.py", tmp_path, args=[_scores(tmp_path, P, B)]).stdout
    auc = mannwhitneyu(P, B).statistic / (len(P) * len(B))
    res = _parse(out)
    for model in ("ESM-1v", "ESM-2", "AlphaMissense"):
        a, lo, hi, _ = res[model]
        assert a == pytest.approx(auc, abs=5e-4)
        assert lo <= a <= hi


def test_perfect_and_tied_scores(tmp_path):
    out = run_script("models/protein_rule/protein_calibration.py", tmp_path,
                     args=[_scores(tmp_path, [5, 6, 7, 8], [1, 2, 3, 4])]).stdout
    a, lo, hi, v = _parse(out)["ESM-1v"]
    assert (a, lo, hi, v) == (1.0, 1.0, 1.0, "INFORMATIVE")
    out = run_script("models/protein_rule/protein_calibration.py", tmp_path,
                     args=[_scores(tmp_path, [1, 1, 1], [1, 1, 1])]).stdout
    a, lo, hi, v = _parse(out)["ESM-1v"]
    assert a == 0.5 and v == "NOT"            # "NOT USED (lower bound below 0.6)"
    assert "child value not reported" in out  # rule section 3: no percentile from a model that does not pass


def test_bootstrap_is_deterministic(tmp_path):
    rng = random.Random(5)
    P = [rng.random() + 0.3 for _ in range(30)]
    B = [rng.random() for _ in range(30)]
    s = _scores(tmp_path, P, B)
    a = run_script("models/protein_rule/protein_calibration.py", tmp_path, args=[s]).stdout
    b = run_script("models/protein_rule/protein_calibration.py", tmp_path, args=[s]).stdout
    assert a == b


def test_child_percentile(tmp_path):
    out = run_script("models/protein_rule/protein_calibration.py", tmp_path,
                     args=[_scores(tmp_path, [5, 6, 7, 8], [1, 2, 3, 4], child=(-4.5, -4.5, 4.5))]).stdout
    # damage 4.5: controls with damage <= 4.5 are 1, 2, 3, 4 -> 4 of 8
    assert re.search(r"child candidate_missense damage=4\.5000 percentile among 8 controls=0\.500", out)


def test_evo2_auc_bootstrap(tmp_path):
    rng = random.Random(9)
    ctrl = ["id\tlabel\tchrom\tpos\tref\talt\tcsq\tclass"]
    out = ["id\tlabel\tchrom\tpos\tref\talt\tref_check\twindow_bp\tll_ref\tll_alt\tdelta\tscore_s\terror"]
    P, B = [], []
    for k in range(60):
        lab = 1 if k < 30 else 0
        csq = "missense" if k % 2 else "nonsense"
        d = rng.gauss(-2.0 if lab else 0.0, 1.0)
        (P if lab else B).append(-d)
        ctrl.append(f"v{k}\t{lab}\tchr1\t{k + 1}\tA\tG\t{csq}\t{'P' if lab else 'B'}")
        out.append(f"v{k}\t{lab}\tchr1\t{k + 1}\tA\tG\tok\t2049\t0\t0\t{d}\t0\t")
    (tmp_path / "controls_rule.tsv").write_text("\n".join(ctrl) + "\n")
    (tmp_path / "evo2_rule_controls_out.tsv").write_text("\n".join(out) + "\n")
    res = run_script("models/evo2/evo2_auc_bootstrap.py", tmp_path).stdout
    nP, nB, auc, lo, hi = ast.literal_eval(re.search(r"^ALL .*?: (\(.*\))$", res, re.M).group(1))
    assert (nP, nB) == (30, 30)
    assert auc == pytest.approx(mannwhitneyu(P, B).statistic / 900, abs=5e-4)
    assert lo <= auc <= hi


@pytest.mark.parametrize("lo,want", [(0.71, "INFORMATIVE"), (0.7, "EXPLORATORY"), (0.6, "EXPLORATORY"), (0.599, "NOT USED")])
def test_rule_thresholds(lo, want):
    """CALIBRATION_RULE.md section 2: informative only if the lower bound is ABOVE 0.7."""
    assert verdict(lo) == want
