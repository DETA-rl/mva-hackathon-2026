"""The spike-in library and the EPCR construction (the ported code itself) on synthetic data.

No real data of any person is used: the calls, the trial table and the HPO files are built here. The harness
steps PRE-REG-SPIKEIN-G1, PRE-REG-SPIKEIN-TRIALS and PRE-REG-SPIKEIN check the same code against the recorded
results on the organisers' data; these tests check the rules a reader can run with no inputs at all.
"""
import importlib.util
import json
import os

import pytest
import yaml

from conftest import ANALYSIS, ROOT, run_script

SPIKEIN = "track1/spikein"
# consequence-table columns the ranking library reads: 0-3 key, 4 gt, 9 frequency class, 11 gene, 12 consequence
HEADER = ("chrom\tpos\tref\talt\tgt\tfilter\tgene_listed\tgnomad_status\tgnomad_af\tclass\ttranscript\tgene\t"
          "consequence\n")


def call(pos, csq, gene="GENEA", gt="0/1", chrom="1"):
    return [chrom, str(pos), "A", "G", gt, "PASS", gene, "found", "0.0001", "rare", "ENST" + gene, gene, csq]


def _hpo(d):
    (d / "hp.obo").write_text("[Term]\nid: HP:0000001\nname: All\n\n[Term]\nid: HP:0001508\n"
                              "is_a: HP:0000001 ! All\n")
    (d / "genes_to_phenotype.txt").write_text("ncbi_gene_id\tgene_symbol\thpo_id\thpo_name\n"
                                              "1\tGENEA\tHP:0001508\tx\n")


@pytest.fixture
def lib(tmp_path, monkeypatch):
    """spikelib.py loaded with the step folder pointed at tmp_path (it reads the HPO files when imported)."""
    _hpo(tmp_path)
    monkeypatch.setenv("REPL_OUT", str(tmp_path))
    spec = importlib.util.spec_from_file_location("spikelib_t", ANALYSIS / SPIKEIN / "spikelib.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ the draft ROW-MAP rule (R0)
def test_row_map_one_and_two_calls(lib):
    a, b = call(100, "nonsense"), call(200, "missense")
    assert lib.row_map([a]) == [lib.key(a)]
    assert set(lib.row_map([a, b])) == {lib.key(a), lib.key(b)}


def test_row_map_picks_heaviest_lof_and_lowest_position_missense(lib):
    """More than two calls: the highest-weight LoF-type call (ties by lowest position) plus the
    lowest-position missense. This is the clause the ROW-MAP test was written to challenge."""
    splice, nons, mis_hi, mis_lo = call(300, "splice_region"), call(100, "nonsense"), call(400, "missense"), call(50, "missense")
    assert lib.row_map([splice, nons, mis_hi, mis_lo]) == [lib.key(nons), lib.key(mis_lo)]
    # two LoF-type calls of equal weight: the lower position wins
    assert lib.row_map([call(900, "frameshift"), nons, mis_lo]) == [lib.key(nons), lib.key(mis_lo)]


def test_row_map_fill_in_when_the_draft_rule_does_not_cover(lib):
    """No missense, or no LoF-type call: the first two by weight then position (logged in the pre-registration)."""
    got = lib.row_map([call(300, "splice_region"), call(100, "nonsense"), call(200, "frameshift")])
    assert got == [lib.key(call(100, "nonsense")), lib.key(call(200, "frameshift"))]
    got = lib.row_map([call(300, "missense"), call(100, "missense"), call(200, "missense")])
    assert got == [lib.key(call(100, "missense")), lib.key(call(200, "missense"))]


# ------------------------------------------------------------------ the scorer re-implementation
def test_scorer_reproduces_the_two_published_outcomes_for_the_submitted_row_1(lib):
    """Spike-in RESULT section 4: with the frozen EPCR vector, if the pair is the answer the row scores 100
    points and F-max 1.0; if only one of its two variants is the answer, 50 points and F-max 0.667."""
    epcr = [0.533223, 0.413611, 0.001641, 0.001631, 0.001621, 0.001611, 0.001601, 0.001591, 0.001581, 0.001571]
    pair = [("15", "1", "T", "G"), ("15", "2", "T", "G")]
    rows = [pair] + [[("1", str(i), "A", "G")] for i in range(3, 12)]
    pts, fmax = lib.score(rows, epcr, set(pair))
    assert (pts, round(fmax, 3)) == (100, 1.0)
    pts, fmax = lib.score(rows, epcr, {pair[0]})
    assert (pts, round(fmax, 3)) == (50, 0.667)


def test_scorer_rank_points_ladder(lib):
    assert [lib.rank_points(r) for r in (1, 2, 3, 4, 5, 6, 10, 11)] == [100, 50, 50, 25, 25, 10, 10, 0]


# ------------------------------------------------------------------ the EPCR construction (analyze.py itself)
TRIAL_COLS = ("stratum\ttid\tversion\tgene\tgtype\talleles\thit_rank\thit_gene\thit_tier\thit_pheno\tfull_row\t"
              "half_row\trows10\n")
ROWS10 = "2:2|" + "|".join(["1:0"] * 9)          # ten rows, the causal pair in row 1


def _trial(stratum, tid, version, rank, gtype="CH"):
    hit = str(rank) if rank else "none"
    return (f"{stratum}\t{tid}\t{version}\tGENEA\t{gtype}\t1:10:A:G;1:20:A:G\t{hit}\tGENEA\tA\t1\t"
            f"{'True' if rank == 1 else 'False'}\tFalse\t{ROWS10}\n")


@pytest.fixture
def trial_dir(tmp_path):
    """A trial table with, in stratum A, two trials at rank 1, one at rank 2 and one not ranked."""
    _hpo(tmp_path)
    rows = [TRIAL_COLS]
    for ver in ("v4", "v3"):
        for i, r in enumerate([1, 1, 2, None], 1):
            rows.append(_trial("A", f"A-{i:03d}", ver, r))
        for s in ("A-BUB", "B", "C1", "C2-HOM", "C2-CH", "D", "E"):
            rows.append(_trial(s, f"{s}-001", ver, 1))
    (tmp_path / "trials.tsv").write_text("".join(rows))
    (tmp_path / "alleles.tsv").write_text(
        "stratum\ttid\tallele\tgt\tmode\tsource\textracted\tconsequence\tfreq_class\tcandidate\t"
        "clinvar_plp_visible\taf_src\n"
        "C1\tC1-001\t1:10:A:G\t1/1\tvisible\tclinvar\tTrue\tUTR_noncoding_exon\tunobserved\tFalse\tFalse\tnone\n")
    (tmp_path / "sanity.json").write_text(json.dumps(
        {"S2_masked_equals_original_minus_bub1b": True, "S3_bub1b_v4_rank": 1}))
    # a GENCODE-shaped line so the A-pc subset can be built
    import gzip
    with gzip.open(tmp_path / "gencode.v44.basic.annotation.gtf.gz", "wt") as fh:
        fh.write('chr1\tx\ttranscript\t1\t9\t.\t+\t.\tgene_name "GENEA"; transcript_type "protein_coding"; '
                 'tag "Ensembl_canonical";\n')
    # analyze.py attaches the EPCR column to the ten draft rows; only their count and columns matter here
    cols = ["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1", "chrom_2", "pos_2", "ref_2", "alt_2",
            "epcr", "finding_type", "notes"]
    draft = [",".join(cols)] + [f"PROBAND01,chr1,{10 + i},A,G,,,,,,primary,GENEA" for i in range(10)]
    (tmp_path / "draft.csv").write_text("\n".join(draft) + "\n")
    return tmp_path


def test_epcr_is_strictly_decreasing_and_follows_the_pre_registered_construction(trial_dir):
    """Section 8 of the pre-registration: smooth each rank's recall as (k + 0.5)/(N + 1), enforce monotonicity by
    isotonic regression, then subtract 1e-5 per rank so the vector is strictly decreasing. With k = (2, 1, 0...)
    of N = 4 the smoothed values are 0.5, 0.3 and 0.1, which are already decreasing, so the published rule gives
    0.5, 0.3 - 1e-5, 0.1 - 2e-5, 0.1 - 3e-5, ... at six decimals."""
    run_script(f"{SPIKEIN}/analyze.py", trial_dir, env={"REPL_DRAFT_CSV": trial_dir / "draft.csv"})
    e = json.load(open(trial_dir / "summary.json"))["epcr"]["epcr"]
    assert len(e) == 10
    assert all(0 < v <= 1 for v in e)
    assert all(e[i] > e[i + 1] for i in range(9)), e
    assert e[:4] == [0.5, 0.29999, 0.09998, 0.09997]


def test_pre_registered_bars_are_applied_as_written(trial_dir):
    """D1 needs rank-1 recall 0.80 with a lower interval bound of 0.70; 0.5 of 4 trials meets neither."""
    run_script(f"{SPIKEIN}/analyze.py", trial_dir, env={"REPL_DRAFT_CSV": trial_dir / "draft.csv"})
    s = json.load(open(trial_dir / "summary.json"))
    assert s["strata"]["A"]["v4"]["p1"] == 0.5
    assert s["decisions"]["D1_falsified"] is True
    assert s["decisions"]["D1"] == "partly robust"
    assert s["decisions"]["D6_gate"] is False          # N_A = 4 is below the pre-registered minimum of 50


# ------------------------------------------------------------------ wiring
def test_spikein_steps_are_declared_with_scripts_and_expected_values():
    from replicate.steps import BY_ID
    expected = yaml.safe_load(open(ROOT / "replicate" / "expected.yaml"))
    for sid in ("PRE-REG-SPIKEIN-G1", "PRE-REG-SPIKEIN-TRIALS", "PRE-REG-SPIKEIN"):
        step = BY_ID[sid]
        assert step.register == "PRE-REG-SPIKEIN-EPCR" and step.privacy == "patient"
        assert step.scripts, sid
        for s in step.scripts:
            assert (ANALYSIS / s).exists(), (sid, s)
        assert expected["steps"][sid]["metrics"], sid

# ------------------------------------------------------------------ the no-input EPCR check
def _epcr_helper():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "epcr_t", ROOT / "replicate" / "helpers" / "epcr_from_counts.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_epcr_isotonic_pools_adjacent_violators():
    """The recorded counts are already decreasing, so the real run never exercises the isotonic step. A
    non-monotone input must be pooled into the closest non-increasing sequence, by weighted mean."""
    m = _epcr_helper()
    def close(a, b):
        return len(a) == len(b) and all(abs(x - y) < 1e-12 for x, y in zip(a, b))

    assert close(m.isotonic([0.5, 0.3, 0.1]), [0.5, 0.3, 0.1])    # already decreasing: unchanged
    assert close(m.isotonic([0.2, 0.4]), [0.3, 0.3])              # one violation: pooled to the mean
    got = m.isotonic([0.9, 0.1, 0.5, 0.3])
    assert close(got, [0.9, 0.3, 0.3, 0.3])
    assert all(got[i] >= got[i + 1] for i in range(3))
    assert abs(sum(got) - sum([0.9, 0.1, 0.5, 0.3])) < 1e-12      # pooling preserves the total


def test_epcr_tie_break_widens_decimals_until_strictly_decreasing():
    """A flat isotonic run must come out strictly decreasing and inside (0, 1]."""
    m = _epcr_helper()
    e, dec = m.strictly_decreasing([0.5] * 10)
    assert all(e[i] > e[i + 1] for i in range(9)) and all(0 < x <= 1 for x in e)
    assert dec >= 6 and e[0] == 0.5


def test_epcr_smoothing_is_add_half_over_n_plus_one():
    m = _epcr_helper()
    s = m.smooth({r: 0 for r in range(1, 11)} | {1: 160, 2: 124}, 300)
    assert s[0] == 160.5 / 301 and s[1] == 124.5 / 301 and s[2] == 0.5 / 301
