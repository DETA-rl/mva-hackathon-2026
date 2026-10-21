"""End to end: `replicate run --tier quick` on a fully synthetic world (no real data).

Every CPU-only step whose inputs exist in the toy world runs through the real step code, the guard and the
report writer. The toy values differ from the register, so most steps report FAIL; what is tested is that they
run and are parsed (no ERROR), that steps without inputs are refused, that full-tier steps are not run, that
T2-POWER-01 (no inputs) reproduces the register exactly, and that nothing is written outside the workdir.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pysam
import pytest
import yaml

import toyworld as tw
from conftest import ROOT

# CDS index, alt base (transcript orientation), genotype
CALLS_P = [(4, "A", "0/1"), (8, "A", "0/1")]          # GENEP: A2D missense, W3* nonsense
CALLS_M = [(13, "A", "1/1"), (14, "T", "0/1")]        # GENEM: P5H missense (hom), P5P synonymous


def _world(d):
    seq, txs = tw.build_genome()
    tw.write_fasta(str(d / "toy.fa"), seq)
    tw.write_gtf(str(d / "toy.gtf.gz"), txs)
    tp, tm = txs
    calls = []
    for t, spec in ((tp, CALLS_P), (tm, CALLS_M)):
        for i, alt, gt in spec:
            pos, ref, a = tw.snv_at(t, seq, i, alt)
            calls.append((pos, ref, a, gt, t.gene))
    calls.sort()
    vcf = d / "toy.vcf"
    with open(vcf, "w") as fh:
        fh.write("##fileformat=VCFv4.2\n##contig=<ID=1,length=%d>\n" % len(seq))
        fh.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="g">\n')
        fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tTOY\n")
        for pos, ref, a, gt, _ in calls:
            fh.write(f"1\t{pos}\t.\t{ref}\t{a}\t50\tPASS\t.\tGT:AD:DP\t{gt}:10,10:20\n")
    pysam.tabix_index(str(vcf), preset="vcf", force=True)
    with open(d / "exons.bed", "w") as fh:
        for t in txs:
            for s, e in t.exons:
                fh.write(f"1\t{s}\t{e}\t{t.gene}\n")
    parts = d / "parts"
    parts.mkdir()
    head = "chrom\tpos\tref\talt\tgt\tfilter\tgenes\tgnomad_status\tgnomad_af\tgnomad_ac\tgnomad_an\tgnomad_filter\n"
    for k in range(4):
        rows = "".join(f"1\t{p}\t{r}\t{a}\t{gt}\tPASS\t{g}\tfound\t1e-05\t1\t100000\tPASS\n"
                       for p, r, a, gt, g in calls) if k == 0 else ""
        (parts / f"child_exonic_gnomad_exomes.part{k}.tsv").write_text(head + rows)
    # ClinVar-like file: the GENEP nonsense call is Pathogenic; every other CDS SNV is a labelled control
    recs = []
    nons = [c for c in calls if c[4] == "GENEP"][1]
    for t in txs:
        for i in range(3, len(tw.CDS) - 3):
            for alt in "ACGT":
                if alt == tw.CDS[i]:
                    continue
                pos, ref, a = tw.snv_at(t, seq, i, alt)
                cls = tw.truth_class(t, i, alt)
                if cls not in ("missense", "nonsense", "synonymous"):
                    continue
                mc = {"missense": "SO:0001583|missense_variant", "nonsense": "SO:0001587|nonsense",
                      "synonymous": "SO:0001819|synonymous_variant"}[cls]
                sig = "Pathogenic" if (pos, a) == (nons[0], nons[2]) else ("Likely_pathogenic" if i % 2 else "Benign")
                recs.append((pos, ref, a, sig, mc, t.gene))
    recs.sort()
    with gzip.open(d / "clinvar.vcf.gz", "wt") as fh:
        fh.write("##fileformat=VCFv4.1\n##fileDate=2026-10-11\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for k, (pos, ref, a, sig, mc, g) in enumerate(recs):
            fh.write(f"1\t{pos}\t{900000 + k}\t{ref}\t{a}\t.\t.\tCLNSIG={sig};CLNVC=single_nucleotide_variant;"
                     f"CLNREVSTAT=criteria_provided,_single_submitter;MC={mc};GENEINFO={g}:1\n")
    (d / "hp.obo").write_text("[Term]\nid: HP:0001508\nname: x\n\n[Term]\nid: HP:9000001\nis_a: HP:0001508 ! x\n")
    (d / "g2p.txt").write_text("ncbi_gene_id\tgene_symbol\thpo_id\thpo_name\n1\tGENEP\tHP:9000001\tx\n")
    rng = np.random.default_rng(2)
    genes = ["BUB1B", "SIRT2", "NAMPT", "NMNAT1", "BUB1", "TRIP13", "CEP57", "MTOR", "CDC20", "PPP2R5B"] + \
            [f"NULL{k}" for k in range(30)]
    n = 250
    with open(d / "CRISPRGeneEffect.csv", "w") as fh:
        fh.write("ModelID," + ",".join(f"{g} ({k + 1})" for k, g in enumerate(genes)) + "\n")
        for i in range(n):
            fh.write(f"ACH-{i:06d}," + ",".join(f"{v:.5f}" for v in rng.normal(-0.3, 0.4, len(genes))) + "\n")
    with open(d / "Model.csv", "w") as fh:
        fh.write("ModelID,OncotreeLineage\n" + "".join(f"ACH-{i:06d},{'Lymphoid' if i < 30 else 'Bowel'}\n" for i in range(n)))
    return {"vcf": str(vcf) + ".gz", "vcf_tbi": str(vcf) + ".gz.tbi", "fasta": str(d / "toy.fa"),
            "gtf": str(d / "toy.gtf.gz"), "exon_bed": str(d / "exons.bed"), "clinvar_vcf": str(d / "clinvar.vcf.gz"),
            "hpo_obo": str(d / "hp.obo"), "hpo_genes_to_phenotype": str(d / "g2p.txt"),
            "depmap_gene_effect": str(d / "CRISPRGeneEffect.csv"), "depmap_model": str(d / "Model.csv")}, parts


TOY_RUNS = ["BLIND-01A", "BLIND-01C", "CONSEQ-V1", "C-FIX-01", "C-FIX-01-FU", "RANK-V1", "RANK-V2", "RANK-V3",
            "RANK-V4", "RANK-V4B", "RANK-V1F", "RANK-V2F", "RANK-V3F", "RANK-V4F", "RANK-V4BF", "C-FIX-02", "T1-CANDIDATE",
            "P2", "T2-DEPMAP-01", "T2-P4", "T2-P5", "PRE-REG-B", "T2-POWER-01", "M-EVO2-CAL-01-CONTROLS", "M-PROT-CAL-02-BUILD"]


_RERUN = {}


@pytest.fixture(scope="module")
def toy_run(tmp_path_factory):
    from replicate import system
    from replicate.steps import BY_ID
    _, avail = system.mem_gb()
    need = max(BY_ID[k].ram_gb for k in TOY_RUNS) + 0.5       # the guard's budget: declared RAM + the toy margin below
    if avail is not None and avail < need:
        pytest.skip(f"only {avail:.1f} GB RAM available (< {need} GB): the resource guard would refuse toy steps")
    d = tmp_path_factory.mktemp("toyworld")
    inputs, parts = _world(d)
    before = sorted(os.listdir(d))
    work = tmp_path_factory.mktemp("work") / "w"
    cfg = {"workdir": str(work), "python": sys.executable, "allow_network": False, "disk_floor_gb": 0,
           "disk_margin_gb": 0, "ram_margin_gb": 0.5, "inputs": inputs, "intermediates": {"gnomad_parts": str(parts)}}
    cpath = d.parent / "toy_config.yaml"
    cpath.write_text(yaml.safe_dump(cfg))
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    p = subprocess.run([sys.executable, "-s", "-m", "replicate", "run", "--config", str(cpath), "--tier", "quick",
                        "--skip-check"], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=900)
    res = json.loads((work / "results" / "results.json").read_text())
    _RERUN["fn"] = lambda steps: subprocess.run(
        [sys.executable, "-s", "-m", "replicate", "run", "--config", str(cpath), "--tier", "quick", "--skip-check",
         "--steps", steps, "--rerun"], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=900)
    return p, res, d, before, work


def test_run_completes_and_reports(toy_run):
    p, res, d, before, work = toy_run
    assert (work / "results" / "REPLICATION_REPORT.md").exists(), p.stdout[-2000:] + p.stderr[-2000:]
    st = {s["id"]: s for s in res["steps"]}
    errors = {k: v.get("reason", "")[:300] for k, v in st.items() if v["status"] == "ERROR"}
    assert not errors, errors
    for k in TOY_RUNS:
        assert st[k]["status"] in ("PASS", "FAIL", "INCONCLUSIVE"), (k, st[k]["status"], st[k].get("reason"))
    assert st["T2-POWER-01"]["status"] == "PASS"


def test_refusals_and_tiers(toy_run):
    _, res, *_ = toy_run
    st = {s["id"]: s for s in res["steps"]}
    for k in ("READCHECK", "P1", "P3"):
        assert st[k]["status"] == "REFUSED" and "bam" in st[k]["reason"]
    for k in ("ALIGN-01", "BLIND-01B", "M-EVO2-CAL-01-SCORE", "M-PROT-CAL-02-SCORE", "PRE-REG-D", "T2-TRIAL-01"):
        assert st[k]["status"] == "NOT RUN"
    assert st["M-EVO2-CAL-01"]["status"] == "NOT RUN"       # its GPU upstream was neither run nor supplied
    assert st["T2-CLASS-01"]["status"] == "NOT RUN"


def test_candidate_comes_from_the_ranking(toy_run):
    _, res, *_ = toy_run
    c = {s["id"]: s for s in res["steps"]}["T1-CANDIDATE"]
    obs = {m["metric"]: m["observed"] for m in c["metrics"]}
    assert obs["gene"] == "GENEP"
    # compared through a digest: the shareable results never carry the candidate's protein changes
    assert obs["protein_changes_sha256"] == hashlib.sha256(b"A2D,W3*").hexdigest()
    assert obs["consequences"] == ["missense", "nonsense"]
    assert "A2D" not in json.dumps(res) and "W3*" not in json.dumps(res)


def test_nothing_written_outside_and_no_paths_in_results(toy_run):
    _, res, d, before, work = toy_run
    assert sorted(os.listdir(d)) == before
    text = (work / "results" / "results.json").read_text() + (work / "results" / "REPLICATION_REPORT.md").read_text()
    assert str(d) not in text
    assert not (work / "tmp").exists() or not any((work / "tmp").iterdir())


def test_incremental_rerun_keeps_earlier_results(toy_run):
    """--steps reruns only the named step; the report keeps the other steps' earlier results, marked as such."""
    _, res, _, _, work = toy_run
    before = {s["id"]: s["status"] for s in res["steps"]}
    _RERUN["fn"]("T2-POWER-01")
    after = json.loads((work / "results" / "results.json").read_text())
    st = {s["id"]: s for s in after["steps"]}
    assert st["T2-POWER-01"]["status"] == "PASS" and not st["T2-POWER-01"].get("reused")
    assert st["BLIND-01A"]["status"] == before["BLIND-01A"] and st["BLIND-01A"].get("reused")
    assert (work / "steps" / "_previous").exists()          # the old step folder was moved aside, not deleted
