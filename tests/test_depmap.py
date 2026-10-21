"""DepMap scripts on synthetic tables: the lever screen (Spearman, genome-wide percentile null and the
pre-registered labels) and the T2-P4 on-target dependency flag (fraction < -0.5 >= 0.25)."""
import random
import re
import statistics

import numpy as np
import pytest
from scipy.stats import spearmanr

from conftest import run_script

CAND = ["FBXW7", "AURKB", "PPP2R5A", "PPP2R5B", "PPP2R5C", "PPP2R5D", "PPP2R5E", "KIF18A"]


def _effects(path, cols, n):
    with open(path, "w") as fh:
        fh.write(",".join(["ModelID"] + [f"{g} ({k + 1})" for k, g in enumerate(cols)]) + "\n")
        for i in range(n):
            fh.write(",".join([f"ACH-{i:06d}"] + [f"{cols[g][i]:.6f}" for g in cols]) + "\n")


@pytest.fixture
def lever_data(tmp_path):
    rng = np.random.default_rng(11)
    n = 300
    bub = rng.normal(-1, 0.4, n)
    cols = {"BUB1B": bub,
            "PPP2R5B": bub * 0.9 + rng.normal(0, 0.15, n),      # strongly co-varying
            "PPP2R5A": bub * 0.15 + rng.normal(0, 0.4, n),      # weak positive
            "SIRT2": rng.normal(0, 0.3, n)}
    for k in range(250):
        cols[f"NULL{k}"] = rng.normal(0, 0.3, n)
    _effects(tmp_path / "CRISPRGeneEffect.csv", cols, n)
    return tmp_path, cols


def _rule(rho, pct):
    if rho >= 0.20 and pct >= 95:
        return "CO-DEPENDENT"
    if rho < 0.10 or pct < 50:
        return "not co-dependent"
    return "indeterminate"


def test_lever_screen_spearman_null_and_labels(lever_data):
    tmp, cols = lever_data
    out = run_script("track2/depmap/lever_screen.py", tmp).stdout
    genome = np.array([spearmanr(cols["BUB1B"], v)[0] for g, v in cols.items() if g != "BUB1B"] +
                      [spearmanr(cols["BUB1B"], cols["BUB1B"])[0]])
    assert f"genes tested genome-wide: {len(genome)}; lines with BUB1B: 300" in out
    lines = dict((g, (float(r), float(p), lab)) for g, r, p, lab in
                 re.findall(r"^(\S+)(?: \(control\))? \| ([+-][\d.]+) \| ([\d.]+) \| (.+)$", out, re.M))
    for g in ("PPP2R5B", "PPP2R5A", "SIRT2"):
        rho = spearmanr(cols["BUB1B"], cols[g])[0]
        pct = float((genome < rho).mean() * 100)
        assert lines[g][0] == pytest.approx(rho, abs=5e-4)
        assert lines[g][1] == pytest.approx(pct, abs=0.05)
        assert lines[g][2] == _rule(rho, pct)
    assert lines["PPP2R5B"][2] == "CO-DEPENDENT"
    assert lines["SIRT2"][2] == "not co-dependent"
    p95 = float(re.search(r"95th percentile of rho: (\S+)", out).group(1))
    assert p95 == pytest.approx(np.percentile(genome, 95), abs=5e-4)
    assert "FBXW7 | not tested" in out


def test_p4_flag_rule_and_blood_median(tmp_path):
    n = 100
    rnd = random.Random(1)
    blood = set(range(20))

    def col(k_below):
        v = [-0.9 if i < k_below else 0.1 for i in range(n)]
        rnd.shuffle(v)
        return v
    cols = {"MTOR": col(30), "CDC20": col(25), "SIRT2": col(24)}
    with open(tmp_path / "CRISPRGeneEffect.csv", "w") as fh:
        fh.write("ModelID," + ",".join(f"{g} ({k})" for k, g in enumerate(cols)) + "\n")
        for i in range(n):
            fh.write(f"ACH-{i:06d}," + ",".join(f"{cols[g][i]}" for g in cols) + "\n")
    with open(tmp_path / "Model.csv", "w") as fh:
        fh.write("ModelID,OncotreeLineage\n")
        for i in range(n):
            fh.write(f"ACH-{i:06d},{'Myeloid' if i in blood else 'Lung'}\n")
    out = run_script("track2/depmap/p4_depmap_safety.py", tmp_path).stdout
    rows = {t: (float(f), fl, float(bm), int(bn)) for t, _, f, fl, bm, bn in
            re.findall(r"^(\S+) \| (\d+) \| ([\d.]+) \| (YES|no) \| (\S+) \| (\d+)$", out, re.M)}
    assert rows["MTOR"][:2] == (0.30, "YES")
    assert rows["CDC20"][:2] == (0.25, "YES")      # boundary: >= 0.25 flags
    assert rows["SIRT2"][:2] == (0.24, "no")
    for t in cols:
        assert rows[t][2] == pytest.approx(statistics.median([cols[t][i] for i in blood]), abs=5e-4)
        assert rows[t][3] == 20
    assert "PLK4 | not in DepMap columns" in out
