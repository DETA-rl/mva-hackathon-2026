"""Consequence calls on plus- and minus-strand toy transcripts, against a truth computed from the CDS string.

The corrected script must agree with the truth on both strands. The original script (the one that produced the
first consequence table) must agree on the plus strand and must be caught disagreeing on the minus strand: that
is the bug recorded in register entry C-FIX-01.
"""
import pytest

import toyworld as tw
from conftest import load_namespace


def _ns(toy, script):
    seq, txs, p = toy
    return load_namespace(f"track1/blind_exonic/{script}", {"REPL_OUT": p["dir"], "REPL_FASTA": p["fasta"]})


def _all_snvs(seq, t):
    for i in range(len(tw.CDS)):
        for alt in "ACGT":
            if alt == tw.CDS[i]:
                continue
            pos, ref, a = tw.snv_at(t, seq, i, alt)
            yield i, alt, pos, ref, a, tw.truth_class(t, i, alt)


@pytest.mark.parametrize("script", ["consequence.py", "consequence_fixed.py"])
def test_cds_reference_matches_toy_genome(toy, script):
    seq, txs, _ = toy
    ns = _ns(toy, script)
    assert set(ns["tx"]) == {t.tid for t in txs}
    for t in txs:
        assert seq[t.cds_positions()[0] - 1] == ("A" if t.strand == "+" else "T")


def test_fixed_matches_truth_on_both_strands(toy):
    seq, txs, _ = toy
    ns = _ns(toy, "consequence_fixed.py")
    for t in txs:
        assert ns["cds_seq"](t.tid)[0] == tw.CDS, f"{t.strand} strand CDS not rebuilt correctly"
        bad = [(i, alt, want, ns["classify"](t.tid, pos, ref, a))
               for i, alt, pos, ref, a, want in _all_snvs(seq, t) if ns["classify"](t.tid, pos, ref, a) != want]
        assert not bad, f"{t.strand} strand: {len(bad)} wrong calls, e.g. {bad[:3]}"


def test_original_matches_truth_on_plus_strand(toy):
    seq, txs, _ = toy
    ns = _ns(toy, "consequence.py")
    t = [x for x in txs if x.strand == "+"][0]
    assert ns["cds_seq"](t.tid)[0] == tw.CDS
    assert all(ns["classify"](t.tid, pos, ref, a) == want for _, _, pos, ref, a, want in _all_snvs(seq, t))


def test_minus_strand_reversal_bug_is_caught(toy):
    """The original script reverses minus-strand CDS blocks before the whole-string reverse complement."""
    seq, txs, _ = toy
    ns = _ns(toy, "consequence.py")
    t = [x for x in txs if x.strand == "-"][0]
    assert ns["cds_seq"](t.tid)[0] != tw.CDS
    wrong = [1 for _, _, pos, ref, a, want in _all_snvs(seq, t) if ns["classify"](t.tid, pos, ref, a) != want]
    assert len(wrong) > 10


def test_non_cds_and_indel_classes(toy):
    seq, txs, _ = toy
    ns = _ns(toy, "consequence_fixed.py")
    for t in txs:
        (e1s, e1e) = sorted(t.exons)[0]
        (c1s, c1e) = sorted(t.cds)[0]
        utr_pos = e1s if c1s > e1s else e1e        # a base of the first genomic exon outside the CDS
        assert ns["classify"](t.tid, utr_pos, seq[utr_pos - 1], "A" if seq[utr_pos - 1] != "A" else "C") == "UTR_noncoding_exon"
        intron = e1e + 1
        assert ns["classify"](t.tid, intron, seq[intron - 1], "A") == "splice_region"
        mid = t.cds_positions()[7]
        r = seq[mid - 1]
        assert ns["classify"](t.tid, mid, r, r + "G") == "frameshift"
        assert ns["classify"](t.tid, mid, r, r + "GGA") == "inframe_indel"


def test_validate_consequence_reports_both_versions(toy, tmp_path):
    """validate_consequence.py on a toy ClinVar file: original fails on minus strand, fixed does not."""
    import gzip
    from conftest import run_script
    seq, txs, p = toy
    recs = []
    for t in txs:
        for i, alt, pos, ref, a, want in _all_snvs(seq, t):
            mc = {"missense": "SO:0001583|missense_variant", "nonsense": "SO:0001587|nonsense",
                  "synonymous": "SO:0001819|synonymous_variant"}.get(want)
            if mc:
                recs.append((pos, ref, a, f"GENEINFO={t.gene}:1;MC={mc}"))
    recs.sort()
    cv = tmp_path / "clinvar_toy.vcf.gz"
    with gzip.open(cv, "wt") as fh:
        fh.write("##fileformat=VCFv4.1\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for k, (pos, ref, a, info) in enumerate(recs):
            fh.write(f"1\t{pos}\t{k}\t{ref}\t{a}\t.\t.\t{info}\n")
    from conftest import ANALYSIS
    out = run_script("track1/blind_exonic/validate_consequence.py", p["dir"],
                     args=[ANALYSIS / "track1/blind_exonic/consequence.py", ANALYSIS / "track1/blind_exonic/consequence_fixed.py", cv],
                     env={"REPL_FASTA": p["fasta"]}).stdout
    plus = [l for l in out.splitlines() if l.startswith("strand +")][0]
    minus = [l for l in out.splitlines() if l.startswith("strand -")][0]
    o_m, f_m = minus.split("original ")[1].split(";")[0], minus.split("fixed ")[1]
    assert f_m.endswith("= 1.000")
    assert not o_m.endswith("= 1.000")
    assert plus.split("original ")[1].split(";")[0].endswith("= 1.000")
