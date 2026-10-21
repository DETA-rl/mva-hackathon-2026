"""Ranking rules v1 to v4 (the ported scripts themselves) on a synthetic consequence table.

Each synthetic gene is built to exercise one clause of the frozen rule files in rules/: weights, the x1.5
homozygous factor, the score >= 3 or homozygous threshold, the paralog exclusion, the male chrX filter with
the pseudoautosomal regions, the cluster-artifact filter, the ClinVar tier, the compound tier and the
phenotype layer with is_a ancestry.
"""
import csv
import gzip

import pytest

from conftest import run_script

HEADER = "chrom\tpos\tref\talt\tgt\tfilter\tgene_listed\tgnomad_status\tgnomad_af\tclass\ttranscript\tgene\tconsequence\n"


def row(chrom, pos, gene, csq, gt="0/1", cls="rare"):
    return f"{chrom}\t{pos}\tA\tG\t{gt}\tPASS\t{gene}\tfound\t0.0001\t{cls}\tENST{gene}\t{gene}\t{csq}\n"


ROWS = [
    row("1", 1000, "GENEA", "nonsense"), row("1", 1010, "GENEA", "missense"),        # 3 + 1 = 4, compound
    row("1", 2000, "GENEB", "missense", "1/1", "unobserved"),                         # 1.5, homozygous
    row("1", 3000, "GENEC", "missense"), row("1", 3010, "GENEC", "missense"),        # 2: not ranked
    row("1", 4000, "GENED", "frameshift"),                                            # 3
    row("2", 5000, "ZNF999", "nonsense"), row("2", 5010, "ZNF999", "nonsense"),      # paralog family
    row("2", 6000, "GENEE", "nonsense", cls="common_or_low"),                         # not rare
    row("2", 7000, "GENEF", "synonymous"),                                            # not protein-altering
    row("X", 50_000_000, "GENEX", "nonsense"),                                        # het, non-PAR chrX
    row("X", 100_000, "GENEXP", "nonsense"),                                          # het, PAR1
    row("X", 60_000_000, "GENEXH", "missense", "1/1"),                                # hom, non-PAR chrX
] + [row("3", 8000 + 100 * k, "GENECL", "missense", "1/1") for k in range(5)]       # 5 hom in 1 kb


@pytest.fixture
def table(tmp_path):
    for name in ("child_exonic_consequence.tsv", "child_exonic_consequence_fixed.tsv"):
        (tmp_path / name).write_text(HEADER + "".join(ROWS))
    return tmp_path


def summary(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


@pytest.mark.parametrize("script,out", [("ranking_v1.py", "ranking_v1_summary.tsv"),
                                        ("ranking_v1_fixed.py", "ranking_v1_summary_fixed.tsv")])
def test_v1_weights_threshold_paralogs(table, script, out):
    p = run_script(f"track1/ranking/{script}", table)
    rows = {r["gene"]: r for r in summary(table / out)}
    order = [r["gene"] for r in summary(table / out)]
    assert float(rows["GENECL"]["score_v1"]) == 7.5            # 5 x missense 1 x 1.5
    assert float(rows["GENEA"]["score_v1"]) == 4.0
    assert float(rows["GENED"]["score_v1"]) == 3.0
    assert float(rows["GENEB"]["score_v1"]) == 1.5             # ranked through the homozygous clause
    assert "GENEC" not in rows and "GENEE" not in rows and "GENEF" not in rows and "ZNF999" not in rows
    assert order == ["GENECL", "GENEA", "GENED", "GENEX", "GENEXP", "GENEB", "GENEXH"]   # score, then name
    assert "paralog-family calls excluded from ranking: 2 genes: 1" in p.stdout


def test_v2_male_x_and_cluster(table):
    p = run_script("track1/ranking/ranking_v2.py", table)
    genes = [r["gene"] for r in summary(table / "ranking_v2_summary.tsv")]
    assert "GENEX" not in genes                                 # het non-PAR chrX excluded
    assert "GENEXP" in genes and "GENEXH" in genes              # PAR het and non-PAR hom kept
    assert "GENECL" not in genes                                # cluster artifact
    assert "excluded: 1 | genes: ['GENEX']" in p.stdout
    assert "flagged and excluded: ['GENECL']" in p.stdout


def _clinvar(path, records):
    with gzip.open(path, "wt") as fh:
        fh.write("##fileformat=VCFv4.1\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for chrom, pos, sig in records:
            fh.write(f"{chrom}\t{pos}\t1\tA\tG\t.\t.\tCLNSIG={sig};MC=SO:1|x\n")


def _hpo(tmp):
    (tmp / "hp.obo").write_text(
        "[Term]\nid: HP:0000001\nname: All\n\n[Term]\nid: HP:0000118\nis_a: HP:0000001 ! All\n\n"
        "[Term]\nid: HP:0001508\nis_a: HP:0000118 ! x\n\n[Term]\nid: HP:9999999\nis_a: HP:0001508 ! x\n")
    (tmp / "genes_to_phenotype.txt").write_text(
        "ncbi_gene_id\tgene_symbol\thpo_id\thpo_name\n1\tGENEB\tHP:9999999\tx\n2\tGENEA\tHP:0000118\tx\n")


def test_v3_tiers_and_v4_phenotype(table):
    _clinvar(table / "clinvar.vcf.gz", [("1", 4000, "Pathogenic"), ("1", 2000, "Benign")])
    p = run_script("track1/ranking/ranking_v3.py", table)
    rows = summary(table / "ranking_v3_summary.tsv")
    tier = {r["gene"]: r["tier"] for r in rows}
    assert tier["GENED"] == "A"                                 # ClinVar Pathogenic call
    assert tier["GENEA"] == "B"                                 # nonsense + missense
    assert tier["GENEB"] == "C"
    assert [r["gene"] for r in rows][:2] == ["GENED", "GENEA"]
    assert "tier A (ClinVar P/LP): ['GENED']" in p.stdout
    _hpo(table)
    q = run_script("track1/ranking/ranking_v4.py", table)
    v4 = summary(table / "ranking_v4_summary.tsv")
    ph = {r["gene"]: int(r["pheno_score"]) for r in v4}
    assert ph["GENEB"] == 1          # annotated to a descendant of a child term
    assert ph["GENEA"] == 0          # annotated to an ancestor only: does not count
    c_tier = [r["gene"] for r in v4 if r["tier"] == "C"]
    assert c_tier[0] == "GENEB"      # phenotype score orders within tier before the v2 score
    assert "genes with phenotype score >= 1: 1" in q.stdout


def test_v4b_amendment_excludes_mt(table):
    (table / "ranking_v3_summary.tsv").write_text(
        "gene\ttier\tv2score\tcalls\trank_v3\nMT-CYB\tC\t3.0\t1\t1\nGENEB\tC\t1.5\t1\t2\n")
    _hpo(table)
    run_script("track1/ranking/ranking_v4b.py", table)
    genes = [r["gene"] for r in summary(table / "ranking_v4b_summary.tsv")]
    assert genes == ["GENEB"]
    run_script("track1/ranking/ranking_v4.py", table)
    assert "MT-CYB" in [r["gene"] for r in summary(table / "ranking_v4_summary.tsv")]
