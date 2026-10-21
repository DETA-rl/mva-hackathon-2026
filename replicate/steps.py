"""The replication steps, keyed by register ID.

Each step runs the ported analysis script(s) (replicate/analysis/, see PORTING_LOG.md) inside its own folder
of the workdir, then parses the script's own printed output and files into named metrics. The expected values
and tolerances live in replicate/expected.yaml; this file only says how to run and how to read.

Harness-side logic (no analysis decision is changed) is limited to: choosing the candidate from the upstream
ranking (T1-CANDIDATE), diffs between original and corrected tables, and applying a pre-registered decision
rule to numbers a script printed (P1, P2, P3, PRE-REG-D, calibration verdicts). Each such place says so.
"""
from __future__ import annotations

import ast
import collections
import csv
import glob
import hashlib
import json
import math
import os
import re
from concurrent.futures import ThreadPoolExecutor

from replicate.config import REPO_ROOT
from replicate.framework import ANALYSIS, Step, StepError, copy_into
from replicate.hashing import sha256_file

PA = {"nonsense", "frameshift", "missense", "inframe_indel", "stop_lost", "splice_region"}
RARE = ("rare", "unobserved")
GENCODE_NAME = "gencode.v44.basic.annotation.gtf.gz"
PART_GLOB = "child_exonic_gnomad_exomes.part*.tsv"


# ---------------------------------------------------------------- parsing helpers
def grab(text, pattern, cast=str):
    m = re.search(pattern, text, re.M)
    if not m:
        raise StepError(f"expected output line not found: /{pattern}/")
    return cast(m.group(1))


def lit(text, pattern):
    return ast.literal_eval(grab(text, pattern))


def rank_value(s):
    s = s.strip()
    return int(s) if s.isdigit() else s


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def first_tx_rows(table):
    """First canonical transcript per call, as the analysis scripts do (seen.setdefault on chrom,pos,ref,alt)."""
    seen = {}
    with open(table) as fh:
        next(fh)
        for line in fh:
            f = line.rstrip("\n").split("\t")
            seen.setdefault((f[0], f[1], f[2], f[3]), f)
    return list(seen.values())


def link_parts(ctx):
    parts = sorted(glob.glob(os.path.join(ctx.artifact("gnomad_parts"), PART_GLOB)))
    if len(parts) != 4:
        raise StepError(f"expected 4 gnomAD part files, found {len(parts)}")
    for p in parts:
        ctx.link(os.path.basename(p), p)


# ---------------------------------------------------------------- Track 1: exonic chain
def blind01a_run(ctx):
    ctx.link("protein_coding_exons_hg38.bed", ctx.input("exon_bed"))
    ctx.run_py("track1/blind_exonic/child_exonic_calls.py", env={"REPL_VCF": ctx.input("vcf")})


def blind01a_parse(ctx):
    out = ctx.stdout("child_exonic_calls")
    return {"n_calls": grab(out, r"child (?:exonic )?non-ref(?:erence)? calls(?: inside protein-coding exons)?: (\d+)", int),
            "sha256_child_exonic_calls": sha256_file(ctx.path("child_exonic_calls.tsv"))}


def blind01b_run(ctx):
    ctx.link("child_exonic_calls.tsv", ctx.artifact("child_exonic_calls"))

    def worker(k):
        # supervise.sh restarted a worker until its log said DONE; the same resume loop, bounded
        for attempt in range(30):
            try:
                out = ctx.run_py("track1/blind_exonic/gnomad_match.py", args=[k, 4], name=f"gnomad_match.{k}.{attempt}")
            except StepError:
                continue
            if re.search(r"^DONE", out, re.M):
                return attempt
        raise StepError(f"gnomad_match worker {k} did not finish after 30 attempts")

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(worker, range(4)))


def blind01b_parse(ctx):
    res = {}
    total = 0
    for k in range(4):
        p = ctx.path(f"child_exonic_gnomad_exomes.part{k}.tsv")
        res[f"sha256_part{k}"] = sha256_file(p)
        total += sum(1 for _ in open(p)) - 1
    res["rows_total"] = total
    return res


def blind01c_run(ctx):
    link_parts(ctx)
    ctx.run_py("track1/blind_exonic/blind_rare_exonic.py")


def blind01c_parse(ctx):
    out = ctx.stdout("blind_rare_exonic")
    classes = lit(out, r"^classes: (\{.*\})$")
    status = lit(out, r"^gnomAD status: (\{.*\})$")
    return {"rows": grab(out, r"^rows (\d+)", int),
            "class_common_or_low": classes.get("common_or_low", 0),
            "class_rare": classes.get("rare", 0),
            "class_unobserved": classes.get("absent_in_gnomad_exomes", 0),
            "class_unknown_af": classes.get("unknown_af", 0),
            "status_not_in_exome_release": status.get("not_in_exome_release", 0),
            "genes_with_2plus_rare_or_unobserved": grab(out, r"^genes with >=2 rare exonic calls: (\d+)", int)}


def _consequence(ctx, script, table):
    ctx.link(GENCODE_NAME, ctx.input("gtf"))
    link_parts(ctx)
    ctx.run_py(f"track1/blind_exonic/{script}", env={"REPL_FASTA": ctx.input("fasta")})
    ctx.run_py("track1/blind_exonic/summarize_consequence.py", env={"REPL_CONSEQUENCE_TSV": ctx.path(table)},
               name="summarize_" + table.replace(".tsv", ""))


def _consequence_metrics(ctx, script_name, table):
    out = ctx.stdout(script_name)
    s = ctx.stdout("summarize_" + table.replace(".tsv", ""))
    return {"canonical_transcripts": grab(out, r"canonical protein-coding transcripts: (\d+)", int),
            "calls_read": grab(out, r"^calls: (\d+)", int),
            "table_rows": grab(s, r"consequence rows \(per transcript-call\): (\d+)", int),
            "protein_altering_rare_first_tx": grab(s, r"protein-altering rare or unobserved calls \(first canonical transcript\): (\d+)", int),
            "by_consequence": lit(s, r"^  by consequence: (\{.*\})$"),
            "homozygous": grab(s, r"^  homozygous: (\d+)", int),
            "sha256_table": sha256_file(ctx.path(table)),
            "stop_lost_rows": sum(1 for line in open(ctx.path(table)) if line.rstrip("\n").endswith("\tstop_lost"))}


def _pa_counts(table):
    """Harness count: (call, transcript) rows that are protein-altering and rare/unobserved, and distinct calls among them."""
    rows, calls = 0, set()
    with open(table) as fh:
        next(fh)
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if f[12] in PA and f[9] in RARE:
                rows += 1
                calls.add((f[0], f[1], f[2], f[3]))
    return rows, len(calls)


def conseq_v1_run(ctx):
    _consequence(ctx, "consequence.py", "child_exonic_consequence.tsv")


def conseq_v1_parse(ctx):
    m = _consequence_metrics(ctx, "consequence", "child_exonic_consequence.tsv")
    m["protein_altering_rare_rows_any_tx"], m["protein_altering_rare_distinct_any_tx"] = _pa_counts(ctx.path("child_exonic_consequence.tsv"))
    return m


def cfix01_run(ctx):
    _consequence(ctx, "consequence_fixed.py", "child_exonic_consequence_fixed.tsv")


def cfix01_parse(ctx):
    m = _consequence_metrics(ctx, "consequence_fixed", "child_exonic_consequence_fixed.tsv")
    m["protein_altering_rare_rows_any_tx"], m["protein_altering_rare_distinct_any_tx"] = _pa_counts(ctx.path("child_exonic_consequence_fixed.tsv"))
    # harness diff: consequence class per (call, transcript) row, original vs corrected table
    def load(p):
        d = {}
        with open(p) as fh:
            next(fh)
            for line in fh:
                f = line.rstrip("\n").split("\t")
                d[(f[0], f[1], f[2], f[3], f[10])] = f[12]
        return d
    a = load(ctx.artifact("consequence_orig"))
    b = load(ctx.path("child_exonic_consequence_fixed.tsv"))
    if set(a) != set(b):
        raise StepError("original and corrected tables do not have the same (call, transcript) rows")
    trans = collections.Counter((a[k], b[k]) for k in a if a[k] != b[k])
    m["rows_changed"] = sum(trans.values())
    for (x, y), n in trans.items():
        m[f"change {x}->{y}"] = n
    return m


def cfix01fu_run(ctx):
    ctx.link("child_exonic_consequence.tsv", ctx.artifact("consequence_orig"))
    ctx.link("child_exonic_consequence_fixed.tsv", ctx.artifact("consequence_fixed"))
    ctx.run_py("track1/blind_exonic/compound_check.py")
    ctx.run_py("track1/blind_exonic/compound_check_fixed.py")


def _compound(out):
    bub = lit(out, r"^BUB1B rows: (\[.*\])$")
    n = grab(out, r"possible compound het, phase unknown\): (\d+)", int)
    lines = out.split("phase unknown): ")[1].splitlines()[1:]
    genes = [l.split(" ", 1)[0] for l in lines if l and not l.startswith("homozygous")]
    return {"n": n, "bub": sorted(r[1] for r in bub), "genes": genes,
            "hom": grab(out, r"homozygous protein-altering rare or unobserved, all: (\d+)", int)}


def cfix01fu_parse(ctx):
    o = _compound(ctx.stdout("compound_check"))
    f = _compound(ctx.stdout("compound_check_fixed"))
    return {"compound_genes_original": o["n"], "compound_genes_corrected": f["n"],
            "hom_rows_original": o["hom"], "hom_rows_corrected": f["hom"],
            "bub1b_consequences_original": o["bub"], "bub1b_consequences_corrected": f["bub"],
            "compound_gene_list_original": o["genes"], "compound_gene_list_corrected": f["genes"]}


# ---------------------------------------------------------------- rankings
def _rank_v12(version, fixed):
    table = "child_exonic_consequence_fixed.tsv" if fixed else "child_exonic_consequence.tsv"
    art = "consequence_fixed" if fixed else "consequence_orig"
    script = f"ranking_v{version}{'_fixed' if fixed else ''}.py"
    summary = f"ranking_v{version}_summary{'_fixed' if fixed else ''}.tsv"

    def run(ctx):
        ctx.link(table, ctx.artifact(art))
        ctx.run_py(f"track1/ranking/{script}")

    def parse(ctx):
        out = ctx.stdout(script[:-3])
        rows = read_tsv(ctx.path(summary))
        genes = [r["gene"] for r in rows]
        m = {"sha256_summary": sha256_file(ctx.path(summary)), "summary_genes": len(rows)}
        if version == 1:
            r = re.search(r"BUB1B rank under v1: (.+?) \| under ablation A: (.+?) \| under shuffled B: (.+)$", out, re.M)
            m.update(candidate_calls=grab(out, r"candidate calls \(rare or unobserved, protein-altering\): (\d+)", int),
                     paralog_calls_excluded=grab(out, r"paralog-family calls excluded from ranking: (\d+)", int),
                     paralog_genes=grab(out, r"paralog-family calls excluded from ranking: \d+ genes: (\d+)", int),
                     ranked_genes=grab(out, r"ranked genes under rule v1: (\d+)", int),
                     bub1b_rank=rank_value(r.group(1)), bub1b_rank_ablation_a=rank_value(r.group(2)),
                     bub1b_rank_shuffled=rank_value(r.group(3)), top7=genes[:7],
                     shuffled_top10=lit(out, r"top 10 under shuffled labels \(baseline\): (\[.*\])$"))
            b = [x for x in rows if x["gene"] == "BUB1B"]
            if b:
                m["bub1b_score"] = float(b[0]["score_v1"])
        else:
            r = re.search(r"BUB1B: rank v2 (.+?) \| ablation A (.+?) \| shuffled baseline (.+)$", out, re.M)
            m.update(x_het_excluded=grab(out, r"A\. male chrX het non-PAR calls excluded: (\d+)", int),
                     x_het_genes=lit(out, r"\| genes: (\[.*\])$"),
                     cluster_genes=lit(out, r"B\. cluster-artifact genes flagged and excluded: (\[.*\])$"),
                     candidate_calls_after_ab=grab(out, r"candidate calls after A and B: (\d+)", int),
                     ranked_genes=grab(out, r"^ranked genes: (\d+)", int),
                     bub1b_rank=rank_value(r.group(1)), bub1b_rank_ablation_a=rank_value(r.group(2)),
                     bub1b_rank_shuffled=rank_value(r.group(3)), top9=genes[:9],
                     shuffled_top10=lit(out, r"top 10 shuffled baseline: (\[.*\])$"))
        return m
    return run, parse


def _rank_v3(fixed):
    table = "child_exonic_consequence_fixed.tsv" if fixed else "child_exonic_consequence.tsv"
    art = "consequence_fixed" if fixed else "consequence_orig"
    script = "ranking_v3_fixed" if fixed else "ranking_v3"
    summary = "ranking_v3_summary_fixed.tsv" if fixed else "ranking_v3_summary.tsv"

    def run(ctx):
        ctx.link(table, ctx.artifact(art))
        ctx.link("clinvar.vcf.gz", ctx.input("clinvar_vcf"))
        ctx.run_py(f"track1/ranking/{script}.py")

    def parse(ctx):
        out = ctx.stdout(script)
        rows = read_tsv(ctx.path(summary))
        r = re.search(r"BUB1B rank v3: (.+?) \| A0 \(v2 only\): (.+)$", out, re.M)
        s = re.search(r"shuffled-ClinVar baseline: tier A genes (\[.*\]) \| BUB1B rank (.+)$", out, re.M)
        b = [x for x in rows if x["gene"] == "BUB1B"]
        return {"candidate_calls": grab(out, r"candidate calls after filters: (\d+)", int),
                "plp_calls": grab(out, r"ClinVar P/LP matched calls: (\d+)", int),
                "tier_a": lit(out, r"tier A \(ClinVar P/LP\): (\[.*\])$"),
                "tier_b": [x["gene"] for x in rows if x["tier"] == "B"],
                "top3": [x["gene"] for x in rows[:3]],
                "bub1b_rank": rank_value(r.group(1)), "bub1b_rank_a0": rank_value(r.group(2)),
                "bub1b_tier": b[0]["tier"] if b else None,
                "shuffled_tier_a": ast.literal_eval(s.group(1)), "bub1b_rank_shuffled": rank_value(s.group(2)),
                "summary_genes": len(rows), "sha256_summary": sha256_file(ctx.path(summary))}
    return run, parse


def _rank_v4(variant):
    """orig = ranking_v4.py (run 1); b = ranking_v4b.py (Amendment 1); fixed = ranking_v4_fixed.py (as run on the
    corrected table, no Amendment 1); bfixed = ranking_v4b.py on the corrected v3 summary, linked under the file name
    the script reads (the frozen rule with Amendment 1 on the corrected table; see BUG-V4-CHRM)."""
    script = {"orig": "ranking_v4", "b": "ranking_v4b", "fixed": "ranking_v4_fixed", "bfixed": "ranking_v4b"}[variant]
    v3art = "ranking_v3_fixed" if variant in ("fixed", "bfixed") else "ranking_v3"
    v3name = "ranking_v3_summary_fixed.tsv" if variant == "fixed" else "ranking_v3_summary.tsv"
    summary = {"orig": "ranking_v4_summary.tsv", "b": "ranking_v4b_summary.tsv", "fixed": "ranking_v4_summary_fixed.tsv",
               "bfixed": "ranking_v4b_summary.tsv"}[variant]

    def run(ctx):
        ctx.link(v3name, ctx.artifact(v3art))
        ctx.link("hp.obo", ctx.input("hpo_obo"))
        ctx.link("genes_to_phenotype.txt", ctx.input("hpo_genes_to_phenotype"))
        ctx.run_py(f"track1/ranking/{script}.py")

    def parse(ctx):
        out = ctx.stdout(script)
        rows = read_tsv(ctx.path(summary))
        r = re.search(r"BUB1B rank: v4 (.+?) \| P0 \(no phenotype\) (.+?) \| P-only (.+?) \| shuffled (.+)$", out, re.M)
        ranks = [rank_value(r.group(i)) for i in range(1, 5)]
        m = {"candidate_genes": grab(out, r"candidate genes \(v3\): (\d+)", int),
             "genes_with_phenotype_match": grab(out, r"genes with phenotype score >= 1: (\d+)", int),
             "phenotype_scores": {x["gene"]: int(x["pheno_score"]) for x in rows if int(x["pheno_score"]) > 0},
             "bub1b_terms": lit(out, r"BUB1B phenotype score: \S+ matched terms: (\[.*\])$"),
             "bub1b_rank": ranks[0], "bub1b_ranks_v4_p0_ponly_shuffled": ranks,
             "mt_genes": [x["gene"] for x in rows if x["gene"].startswith("MT-")],
             "mt_ranks": {x["gene"]: int(x["rank_v4"]) for x in rows if x["gene"].startswith("MT-")},
             "top10": [x["gene"] for x in rows[:10]],
             "summary_lines_incl_header": len(rows) + 1,
             "sha256_summary": sha256_file(ctx.path(summary))}
        return m
    return run, parse


def cfix02_run(ctx):
    ctx.link(GENCODE_NAME, ctx.input("gtf"))
    ctx.run_py("track1/blind_exonic/validate_consequence.py",
               args=[ANALYSIS / "track1/blind_exonic/consequence.py", ANALYSIS / "track1/blind_exonic/consequence_fixed.py",
                     ctx.input("clinvar_vcf")], env={"REPL_FASTA": ctx.input("fasta")})


def cfix02_parse(ctx):
    out = ctx.stdout("validate_consequence")
    m = {"clinvar_snvs_checked": grab(out, r"ClinVar SNVs checked .*?: (\d+)", int)}
    for strand, tag in (("+", "plus"), ("-", "minus")):
        r = re.search(rf"^strand {re.escape(strand)}: original (\d+/\d+) = [\d.]+; fixed (\d+/\d+) = [\d.]+", out, re.M)
        if not r:
            raise StepError(f"strand {strand} line not found")
        m[f"{tag}_original"], m[f"{tag}_fixed"] = r.group(1), r.group(2)
    # harness diff of the ranking summaries (gene sets), original vs corrected
    for v in (1, 2, 3, 4):
        a = {x["gene"] for x in read_tsv(ctx.artifact(f"ranking_v{v}"))}
        b = {x["gene"] for x in read_tsv(ctx.artifact(f"ranking_v{v}_fixed"))}
        m[f"v{v}_only_original"] = sorted(a - b)
        m[f"v{v}_only_corrected"] = sorted(b - a)
    return m


# ---------------------------------------------------------------- candidate (harness)
def candidate_run(ctx):
    # rank 1 of the frozen v4 rule WITH Amendment 1 on the corrected table (RANK-V4BF), not of ranking_v4_fixed.py
    rows = read_tsv(ctx.artifact("ranking_v4b_fixed"))
    top = [r["gene"] for r in rows if r["rank_v4"] == "1"]
    if len(top) != 1:
        raise StepError("ranking v4 with Amendment 1 (corrected table) has no unique rank-1 gene")
    gene = top[0]
    calls = []
    for f in first_tx_rows(ctx.artifact("consequence_fixed")):
        if f[11] == gene and f[12] in PA and f[9] in RARE:
            calls.append({"chrom": f[0], "pos": int(f[1]), "ref": f[2], "alt": f[3], "gt": f[4],
                          "gnomad_class": f[9], "transcript": f[10], "consequence": f[12]})
    calls.sort(key=lambda c: c["pos"])
    ctx.link(GENCODE_NAME, ctx.input("gtf"))
    out = ctx.run_helper("candidate_protein.py", env={
        "REPL_FASTA": ctx.input("fasta"),
        "REPL_CONSEQUENCE_SCRIPT": ANALYSIS / "track1/blind_exonic/consequence_fixed.py",
        "REPL_CANDIDATE_CALLS": json.dumps(calls)})
    calls = json.loads(out.strip().splitlines()[-1])
    cand = {"gene": gene, "source": "rank 1 of ranking v4 with Amendment 1 on the corrected consequence table", "calls": calls}
    p = ctx.save_patient_json("candidate.json", cand)
    ctx.artifacts["candidate"] = str(p)


def protein_changes_digest(proteins):
    """sha256 of the candidate's protein changes, sorted and comma-joined: the report compares the value without
    printing it (the protein changes are the child's alleles)."""
    return hashlib.sha256(",".join(sorted(proteins)).encode()).hexdigest()


def candidate_parse(ctx):
    c = json.load(open(ctx.artifact("candidate")))
    return {"gene": c["gene"], "n_calls": len(c["calls"]),
            "consequences": sorted(x["consequence"] for x in c["calls"]),
            "protein_changes_sha256": protein_changes_digest(x["protein"] for x in c["calls"] if x["protein"]),
            "all_heterozygous": all(x["gt"] in ("0/1", "0|1", "1|0") for x in c["calls"])}


def load_candidate(ctx):
    return json.load(open(ctx.artifact("candidate")))


def bam_contig(chrom):
    return chrom if chrom.startswith("chr") else "chr" + chrom


# ---------------------------------------------------------------- read-level steps
def readcheck_run(ctx):
    c = load_candidate(ctx)
    sites = [[bam_contig(x["chrom"]), x["pos"], x["ref"], x["alt"],
              f"{x['consequence']} {x['protein']} (ref {x['ref']}, alt {x['alt']})"] for x in c["calls"]]
    ctx.run_py("track1/readlevel/bub1b_readcheck.py",
               env={"REPL_BAM": ctx.input("bam"), "REPL_CANDIDATE_SITES": json.dumps(sites)})


def readcheck_parse(ctx):
    d = json.load(open(ctx.path("bub1b_readcheck.json")))
    m = {"sha256_readcheck_json": sha256_file(ctx.path("bub1b_readcheck.json"))}
    for label, v in d.items():
        k = label.split(" ", 1)[0]
        fwd, rev = v["alt_strand"].get("fwd", 0), v["alt_strand"].get("rev", 0)
        m.update({f"{k}_depth": v["depth"], f"{k}_alt_reads": v["alt_reads"], f"{k}_alt_fraction": v["alt_fraction"],
                  f"{k}_alt_mapq_median": v["alt_mapq_median"], f"{k}_alt_fwd": fwd, f"{k}_alt_rev": rev,
                  # harness reading of 'consistent with heterozygous'
                  f"{k}_consistent_with_het": bool(v["alt_fraction"] is not None and 0.25 <= v["alt_fraction"] <= 0.75
                                                   and fwd > 0 and rev > 0)})
    return m


def p1_run(ctx):
    c = load_candidate(ctx)
    pos = sorted(x["pos"] for x in c["calls"])
    chrom = c["calls"][0]["chrom"].replace("chr", "")
    a, b = pos[0], pos[-1]
    out = ctx.run_sh("track1/readlevel/p1_het_list_vcf.sh", env={
        "REPL_VCF": ctx.input("vcf"), "REPL_P1_CHROM": chrom, "REPL_P1_START": a, "REPL_P1_END": b})
    recs = [l.split(" ") for l in out.strip().splitlines() if l.strip()]
    het = sorted(int(r[0]) for r in recs if len(r) >= 4 and r[3].split(":")[0] in ("0/1", "0|1", "1|0")
                 and len(r[1]) == 1 and len(r[2]) == 1)
    if len(het) < 2:
        raise StepError("fewer than two heterozygous SNVs between the candidate sites")
    gaps = [y - x for x, y in zip(het, het[1:])]
    # window of the original run, as a function of the two sites: [floor(a/100)*100 - 100, ceil(b/100)*100]
    w0 = (a // 100) * 100 - 100
    w1 = -(-b // 100) * 100
    ctx.run_py("track1/readlevel/p1_tlen_bridging.py", env={
        "REPL_BAM": ctx.input("bam"), "REPL_P1_WINDOW_START": w0, "REPL_P1_WINDOW_END": w1,
        "REPL_P1_GAP1": gaps[0]})
    ctx.save_patient_json("p1_sites.json", {"records": recs, "het_snvs": het, "gaps": gaps})


def p1_parse(ctx):
    d = json.load(open(ctx.private / "p1_sites.json"))
    out = ctx.stdout("p1_tlen_bridging")
    recs, gaps = d["records"], d["gaps"]
    max_tlen = grab(out, r"max \|TLEN\| in window: (\d+)", int)
    m = {"records_in_interval": len(recs), "het_snvs_in_interval": len(d["het_snvs"]),
         "hom_records_in_interval": sum(1 for r in recs if r[3].split(":")[0] in ("1/1", "1|1")),
         "read1_templates": grab(out, r"proper read1 templates in window \(MAPQ>=30\): (\d+)", int),
         "max_abs_tlen": max_tlen, "gap1_bp": gaps[0], "gap2_bp": gaps[1] if len(gaps) > 1 else None,
         "templates_spanning_gap1": grab(out, r"needs >= \d+\): (\d+)$", int)}
    # harness: a template longer than the largest gap is necessary for any bridge; none -> UNRESOLVED
    m["templates_spanning_gap2_upper_bound"] = 0 if len(gaps) > 1 and max_tlen < gaps[1] else None
    m["decision"] = "UNRESOLVED" if max_tlen < max(gaps) else "NOT DECIDED (allele-level bridge count not run)"
    return m


P2_GENES = ["RNU4ATAC", "RNU6ATAC", "ZRSR2", "SNRNP48", "ESCO2", "PCNT", "CENPF", "BUB1B", "TRIP13", "CEP57",
            "SMC5", "MAD1L1", "CEP192", "TRIM37", "CDC20", "MAD2L1BP", "CENATAC", "SLF2"]


def p2_run(ctx):
    ctx.link(GENCODE_NAME, ctx.input("gtf"))
    link_parts(ctx)
    ctx.run_py("track1/readlevel/p2_annot.py", env={"REPL_VCF": ctx.input("vcf")})


def p2_parse(ctx):
    out = ctx.stdout("p2_annot")
    m = {}
    reported = 0
    for g in P2_GENES:
        r = re.search(rf"^{g}: (\d+) non-ref calls; (\d+) in exonic table$", out, re.M)
        if r:
            reported += 1
            m[f"{g}_nonref_calls"] = int(r.group(1))
            m[f"{g}_exonic_calls"] = int(r.group(2))
        elif re.search(rf"^{g} no coordinates$", out, re.M):
            reported += 1
            m[f"{g}_nonref_calls"] = "no coordinates"
    m["genes_reported"] = reported
    # harness: the pre-registered flag rule applied to the corrected consequence table
    rows = [f for f in first_tx_rows(ctx.artifact("consequence_fixed")) if f[11] in P2_GENES and f[9] in RARE]
    het = lambda f: f[4] in ("0/1", "0|1", "1|0")
    hom = lambda f: f[4] in ("1/1", "1|1")
    pa = [f for f in rows if f[12] in PA]
    m["genes_with_rare_protein_altering_calls"] = sorted({f[11] for f in pa})
    m["bub1b_rare_protein_altering"] = sorted(f[12] for f in pa if f[11] == "BUB1B")
    flagged = set()
    for g in P2_GENES:
        g_pa = [f for f in pa if f[11] == g]
        if any(hom(f) for f in g_pa) or sum(1 for f in g_pa if het(f)) >= 2:
            flagged.add(g)
    m["flagged_genes"] = sorted(flagged)
    m["genes_with_rare_hom_any_consequence"] = sorted({f[11] for f in rows if hom(f)})
    return m


def p3_run(ctx):
    ctx.run_py("track1/readlevel/cenatac_check.py", env={
        "REPL_GTF": ctx.input("gtf"), "REPL_FASTA": ctx.input("fasta"), "REPL_VCF": ctx.input("vcf"),
        "REPL_BAM": ctx.input("bam")})


def p3_parse(ctx):
    out = ctx.stdout("cenatac_check")
    r = re.search(r"^transcript (\S+) strand (\S) ", out, re.M)
    bases = lit(out, r"BAM bases at c\.803 genomic position .*?: (\{.*\})$")
    strand = r.group(2)
    alt = "T" if strand == "+" else "A"
    split = grab(out, r"reads with a >=15 bp deletion in the CENATAC junction window \(MAPQ>=30\): (\d+)", int)
    n_alt = bases.get(alt, 0)

    def rule(n):  # PRE-REG-C decision rule
        return "POSITIVE" if n >= 3 else ("NEGATIVE" if n == 0 else "INDETERMINATE")
    return {"transcript": r.group(1), "strand": strand,
            "c803_reference_base": grab(out, r"c\.803 genomic \S+ reference \(transcript orientation\) = (\S)", str),
            "vcf_records_at_c803": len(re.findall(r"^VCF at c\.803 position:", out, re.M)),
            "bam_reads_c803": sum(bases.values()), "bam_alt_reads_c803": n_alt, "split_reads_15bp": split,
            "decision_c803AT": rule(n_alt), "decision_del18": rule(split)}



# ---------------------------------------------------------------- Track 1: stage 0 to 2 (read-level and depth)
def s01_run(ctx):
    ctx.run_py("track1/stage1_targeted/s01_sex_from_bai.py", env={"REPL_BAM": ctx.input("bam")})


# Public reference constants (not child data): non-N bases per chromosome of GCA_000001405.15_GRCh38_no_alt_plus_
# hs38d1_analysis_set.fna (the input 'fasta'), counted by the authors on 2026-10-20. In the analysis set the chrY PARs
# are N-masked, so chrY's ungapped length excludes them.
GRCH38_UNGAPPED = {
    "chr1": 230481014, "chr2": 240548237, "chr3": 198100142, "chr4": 189752667, "chr5": 178983193,
    "chr6": 170078523, "chr7": 158970135, "chr8": 144768136, "chr9": 121790553, "chr10": 133262998,
    "chr11": 134533742, "chr12": 133137819, "chr13": 97983128, "chr14": 88518101, "chr15": 84641325,
    "chr16": 81805944, "chr17": 82920216, "chr18": 80089605, "chr19": 55766397, "chr20": 63944257,
    "chr21": 38038574, "chr22": 37071985, "chrX": 154893034, "chrY": 23636355, "chrM": 16568}


def s01_parse(ctx):
    out = ctx.stdout("s01_sex_from_bai")
    m = {}
    found = re.findall(r"^(chr\w+): mapped=(\d+) ratio_to_autosome_mean=([\d.]+)$", out, re.M)
    for c, _, r in found:
        m[f"{c}_ratio_to_autosome"] = float(r)
    # harness addition (INFO only, the script's numbers are unchanged): the same counts per ungapped Mb, over the
    # autosome-wide reads per ungapped Mb, so that a short chromosome does not read like a loss
    a_mean = grab(out, r"^autosome_mean_mapped=(\d+)$", int)
    auto_len = sum(GRCH38_UNGAPPED[f"chr{i}"] for i in range(1, 23))
    for c, n, _ in found:
        if c in GRCH38_UNGAPPED:
            m[f"{c}_per_mb_ratio_to_autosome"] = round((int(n) / GRCH38_UNGAPPED[c]) / (22 * a_mean / auto_len), 4)
    return m


def h01_run(ctx):
    ctx.run_py("track1/stage1_targeted/h01_cep57_dup11.py", env={"REPL_BAM": ctx.input("bam")})


def h01_parse(ctx):
    out = ctx.stdout("h01_cep57_dup11")
    m = {}
    for name, t, i, k, per in re.findall(r"^(\S+) reads (\d+) ins9-13 (\d+) softclip9-13 (\d+) per1000 ([\d.]+)$", out, re.M):
        m.update({f"{name}_reads": int(t), f"{name}_ins9_13": int(i), f"{name}_softclip9_13": int(k), f"{name}_per1000": float(per)})
    # harness reading of the falsifier: no excess of junction signal over background
    m["decision"] = "RULED OUT" if m["CEP57_per1000"] <= m["background_per1000"] else "EXCESS OVER BACKGROUND"
    return m


def hbatch_run(ctx):
    ctx.run_py("track1/stage1_targeted/h_batch.py", env={"REPL_BAM": ctx.input("bam"), "REPL_VCF": ctx.input("vcf")})


def hbatch_parse(ctx):
    out = ctx.stdout("h_batch")
    d = {}
    for line in out.splitlines():
        if " => " in line:
            k, v = line.split(" => ", 1)
            d[k] = ast.literal_eval(v)
    h02 = next(v for k, v in d.items() if k.startswith("H02_"))
    m = {"h02_reads_G": h02["G"], "h02_reads_A": h02["A"], "h02_depth": sum(h02.values()),
         "decision_h02": "RULED OUT" if h02["A"] == 0 and sum(h02.values()) >= 20 else "NOT RULED OUT"}
    for tag, k in (("bub1b", "H03_BUB1B_intron_region"), ("background", "H03_background_chr15_60Mb")):
        for f in ("split_per1k", "clip_per1k", "disc_per1k"):
            m[f"h03_{tag}_{f}"] = d[k][f]
    lowvaf = d["H05_het_PASS_DP20_sites_per_chr_lowVAF(<15%)_over_total"]
    for c, v in lowvaf.items():
        if c not in [str(i) for i in range(1, 23)] + ["X", "Y"]:
            continue
        lo, tot = (int(x) for x in v.split("/"))
        m[f"h05_lowvaf_pct_chr{c}"] = round(100 * lo / tot, 6)
    gaps = d["H06_top10_het_gaps_bp(chr,start,end)"]
    for i, g in enumerate(gaps[:4], 1):            # sizes and chromosomes only; the positions are not reported
        m[f"h06_gap{i}_mb"] = round(g[0] / 1e6, 2)
        m[f"h06_gap{i}_chrom"] = str(g[1])
    m["h06_gaps_over_3mb"] = d["H06_gaps_over_3Mb_count"]
    naa, xbg, auto = d["H12_depth_reads_NAA10_6.3kb"], d["H12_depth_reads_chrX_bg_6.3Mb"], d["H12_depth_reads_chr1_bg_6.3Mb"]
    # reads per kb, as in the register (window lengths fixed in the script: 6,284 bp and 6,284,000 bp)
    m.update(h12_naa10_reads_per_kb=round(naa / 6.284), h12_chrX_bg_reads_per_kb=round(xbg / 6284),
             h12_chr1_bg_reads_per_kb=round(auto / 6284), h12_naa10_to_autosome=round((naa / 6.284) / (auto / 6284), 2))
    return m


def h08_run(ctx):
    ctx.run_py("track1/sv_cnv/h08_depth.py", env={"REPL_BAM": ctx.input("bam")})


def h08_parse(ctx):
    d = json.load(open(ctx.path("h08_depth_sampled.json")))
    m = {f"ratio_chr{c}": v for c, v in d["ratio_to_autosome_median"].items()}
    m["sha256_json"] = sha256_file(ctx.path("h08_depth_sampled.json"))
    return m


def detlim_run(ctx):
    ctx.run_py("track1/sv_cnv/detection_limit.py", env={"REPL_BAM": ctx.input("bam")})


def detlim_parse(ctx):
    d = json.load(open(ctx.path("detection_limit.json")))
    return {"median_cv_1mb": d["median_cv_1Mb"], "min_detectable_shift": d["min_detectable_whole_chrom_shift_fraction"],
            "sha256_json": sha256_file(ctx.path("detection_limit.json"))}


CNV_CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]


def cnv_run(ctx):
    env = {"REPL_BAM": ctx.input("bam"), "REPL_FASTA": ctx.input("fasta")}
    groups = [CNV_CHROMS[k::6] for k in range(6)]          # 6 workers, as in the original run
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda g: ctx.run_py("track1/sv_cnv/cnv_bins.py", args=g[1], env=env, name=f"cnv_bins.w{g[0]}"),
                    enumerate(groups)))
    ctx.run_py("track1/sv_cnv/cnv_call.py")


def cnv_parse(ctx):
    out = ctx.stdout("cnv_call")
    d = json.load(open(ctx.path("cnv_calls_v1.json")))
    m = {"calls": lit(out, r"^calls: (\[.*\])$"), "chromosomes_tested": len(d),
         "sha256_json": sha256_file(ctx.path("cnv_calls_v1.json"))}
    for c in ("chrX", "chr19"):
        m[f"{c}_ratio"] = d[c]["r"]
        m[f"{c}_f"] = d[c]["f"]
    return m

# ---------------------------------------------------------------- Track 2
def depmap01_run(ctx):
    ctx.link("CRISPRGeneEffect.csv", ctx.input("depmap_gene_effect"))
    ctx.run_py("track2/depmap/dep_corr.py")


def depmap01_parse(ctx):
    out = ctx.stdout("dep_corr")
    m = {"n_lines": grab(out, r"n cell lines with all genes: (\d+)", int)}
    for g, rho, p in re.findall(r"^  (\S+)\s+rho=([+-][\d.]+) p=(\S+)$", out, re.M):
        m[f"rho_{g}"] = float(rho)
        m[f"p_{g}"] = float(p)
    raw = grab(out, r"^Medians \(gene effect\): (\{.*\})$")
    med = ast.literal_eval(re.sub(r"np\.float64\(([^)]*)\)", r"\1", raw))
    for g, v in med.items():
        m[f"median_{g}"] = v
    return m


def p4_run(ctx):
    ctx.link("CRISPRGeneEffect.csv", ctx.input("depmap_gene_effect"))
    ctx.link("Model.csv", ctx.input("depmap_model"))
    ctx.run_py("track2/depmap/p4_depmap_safety.py")


def p4_parse(ctx):
    return p4_parse_text(ctx.stdout("p4_depmap_safety"))


def p4_parse_text(out):
    r = re.search(r"cell lines: (\d+); blood-lineage lines in Model\.csv: (\d+)", out)
    m = {"n_lines": int(r.group(1)), "blood_lines_in_model": int(r.group(2))}
    flagged, blood_n = [], set()
    for t, n, frac, flag, bmed, bn in re.findall(r"^(\S+) \| (\d+) \| ([\d.]+) \| (YES|no) \| (\S+) \| (\d+)$", out, re.M):
        m[f"frac_{t}"] = float(frac)
        m[f"blood_median_{t}"] = float(bmed)
        m[f"n_lines_{t}"] = int(n)
        blood_n.add(int(bn))
        if flag == "YES":
            flagged.append(t)
    m["flagged_targets"] = flagged
    m["blood_lines_with_effects"] = blood_n.pop() if len(blood_n) == 1 else sorted(blood_n)
    return m


def p5_run(ctx):
    ctx.link("CRISPRGeneEffect.csv", ctx.input("depmap_gene_effect"))
    ctx.link("Model.csv", ctx.input("depmap_model"))
    ctx.run_py("track2/depmap/p5_depmap_safety.py")


def p5_parse(ctx):
    out = ctx.stdout("p5_depmap_safety")
    m = p4_parse_text(out)
    m["not_measured"] = re.findall(r"^(\S+) \| not measured", out, re.M)
    m["genes_measured"] = grab(out, r"with a DepMap column: (\d+)", int)
    m["candidate_flag_counts"] = {c: int(n) for c, n, _, _ in
                                  re.findall(r"^(\S+) \| (\d+) \| (\S+) \| (\S+)$", out, re.M)}
    m["sha256_depmap_tsv"] = sha256_file(ctx.path("t2_p5_depmap.tsv"))
    m["sha256_candidate_counts_tsv"] = sha256_file(ctx.path("t2_p5_candidate_counts.tsv"))
    return m


def lever_run(ctx):
    ctx.link("CRISPRGeneEffect.csv", ctx.input("depmap_gene_effect"))
    ctx.run_py("track2/depmap/lever_screen.py")


def lever_parse(ctx):
    out = ctx.stdout("lever_screen")
    r = re.search(r"genes tested genome-wide: (\d+); lines with BUB1B: (\d+)", out)
    m = {"genes_tested": int(r.group(1)), "lines_with_bub1b": int(r.group(2)),
         "genome_p95_rho": grab(out, r"genome-wide 95th percentile of rho: (\S+)", float),
         "genome_median_rho": grab(out, r"genome-wide median rho: (\S+)", float)}
    labels = {}
    for g, rho, pct, lab in re.findall(r"^(\S+)(?: \(control\))? \| ([+-][\d.]+) \| ([\d.]+) \| (.+)$", out, re.M):
        m[f"rho_{g}"] = float(rho)
        m[f"pct_{g}"] = float(pct)
        m[f"label_{g}"] = lab
        labels[g] = lab
    m["n_co_dependent"] = sum(1 for v in labels.values() if v == "CO-DEPENDENT")
    return m


def power_run(ctx):
    ctx.run_py("track2/power/power_guide.py")


def power_parse(ctx):
    out = ctx.stdout("power_guide")
    m = {}
    for n, a, b, c in re.findall(r"^\s*(\d+) \|\s*([\d.]+)% \|\s*([\d.]+)% \|\s*([\d.]+)%$", out, re.M):
        m[f"power n={n}"] = [float(a), float(b), float(c)]
    d = lit(out, r"n per arm needed for 80% power: (\{.*\})$")
    m["n_per_arm_80pct"] = {str(k): v for k, v in d.items()}
    return m


def trial_run(ctx):
    ctx.run_sh("track2/trials/ctgov_nmn_nr_query.sh")


def trial_parse(ctx):
    out = ctx.stdout("ctgov_nmn_nr_query")
    m = {"total_studies": grab(out, r"total studies: (\d+)", int)}
    m["nct_status"] = {nct: st for nct, st in re.findall(r"^[* ] (NCT\d{8}) (\S+) \|", out, re.M)}
    want = ["NCT04691986", "NCT03579693", "NCT06208527", "NCT07144527", "NCT07693543", "NCT05759468",
            "NCT04342975", "NCT03176628"]
    m["nct_status"] = {k: m["nct_status"].get(k, "ABSENT") for k in want}
    return m


# ---------------------------------------------------------------- models
def controls_run(ctx):
    ctx.run_py("models/protein_rule/build_rule_controls.py", args=[ctx.input("clinvar_vcf"), ctx.dir])


def controls_parse(ctx):
    out = ctx.stdout("build_rule_controls")
    r = re.search(r"controls: (\d+) P: (\d+) B: (\d+)", out)
    m = {"controls": int(r.group(1)), "controls_P": int(r.group(2)), "controls_B": int(r.group(3)),
         "sha256_controls_rule": sha256_file(ctx.path("controls_rule.tsv")),
         "sha256_script": sha256_file(ANALYSIS / "models/protein_rule/build_rule_controls.py")}
    for line in out.splitlines():
        if line.startswith("("):
            cls, csq, n, genes = ast.literal_eval(line)
            m[f"eligible_{cls}_{csq}"] = n
            m[f"selected_genes_{cls}_{csq}"] = genes
    return m


def _evo2_env(ctx):
    return {"NVTE_ALLOW_UNSAFE_PICKLE_EXTRA_STATE": "1"}


def evo2_score_run(ctx):
    copy_into(ctx, "models/evo2/configs/evo2-7b-1m.yml", "configs/evo2-7b-1m.yml")
    ctx.link("controls_rule.tsv", ctx.artifact("controls_rule"))
    ctx.run_py("models/evo2/evo2_score_safe.py", args=[
        "--variants", "controls_rule.tsv", "--fasta", ctx.input("fasta"), "--fai", ctx.input("fasta") + ".fai",
        "--weights", ctx.input("evo2_weights"), "--out", ctx.path("evo2_rule_controls_out.tsv")], env=_evo2_env(ctx))


def evo2_score_parse(ctx):
    rows = read_tsv(ctx.path("evo2_rule_controls_out.tsv"))
    return {"rows": len(rows), "scoring_errors": sum(1 for r in rows if r["error"]),
            "ref_checks_ok": sum(1 for r in rows if r["ref_check"] == "ok"),
            "sha256_scores": sha256_file(ctx.path("evo2_rule_controls_out.tsv"))}


def verdict(lo):
    """CALIBRATION_RULE.md section 2 (harness applies the rule to the printed CI lower bound)."""
    if lo > 0.7:
        return "INFORMATIVE"
    if lo >= 0.6:
        return "EXPLORATORY"
    return "NOT USED"


def evo2_auc_run(ctx):
    ctx.link("evo2_rule_controls_out.tsv", ctx.artifact("evo2_control_scores"))
    ctx.link("controls_rule.tsv", ctx.artifact("controls_rule"))
    ctx.run_py("models/evo2/evo2_auc_bootstrap.py")


def evo2_auc_parse(ctx):
    out = ctx.stdout("evo2_auc_bootstrap")
    m = {}
    for tag, pat in (("all", r"^ALL .*?: (\(.*\))$"), ("missense", r"^missense (\(.*\))$"), ("nonsense", r"^nonsense (\(.*\))$")):
        nP, nB, auc, lo, hi = lit(out, pat)
        if tag == "all":
            m["all_nP_nB"] = [nP, nB]
            m["verdict"] = verdict(lo)
        m[f"{tag}_auc"] = auc
        m[f"{tag}_ci"] = [lo, hi]
    return m


def evo2_child_run(ctx):
    c = load_candidate(ctx)
    copy_into(ctx, "models/evo2/configs/evo2-7b-1m.yml", "configs/evo2-7b-1m.yml")
    with open(ctx.path("child_calls.tsv"), "w") as fh:
        fh.write("id\tlabel\tchrom\tpos\tref\talt\n")
        for x in c["calls"]:
            ch = bam_contig(x["chrom"])
            fh.write(f"child_{x['consequence']}_{ch}_{x['pos']}\tNA\t{ch}\t{x['pos']}\t{x['ref']}\t{x['alt']}\n")
    ctx.run_py("models/evo2/evo2_score_safe.py", args=[
        "--variants", "child_calls.tsv", "--fasta", ctx.input("fasta"), "--fai", ctx.input("fasta") + ".fai",
        "--weights", ctx.input("evo2_weights"), "--out", ctx.path("child_evo2_out.tsv")], env=_evo2_env(ctx))


def evo2_child_parse(ctx):
    rows = read_tsv(ctx.path("child_evo2_out.tsv"))
    m = {"ref_checks_ok": sum(1 for r in rows if r["ref_check"] == "ok")}
    for r in rows:
        csq = r["id"].split("_")[1]
        m[f"{csq}_delta"] = float(r["delta"]) if r["delta"] else None
    return m


def prot_build_run(ctx):
    env = {"REPL_GTF": ctx.input("gtf"), "REPL_FASTA": ctx.input("fasta")}
    # optional sanity check of the candidate missense's reference residue, only when T1-CANDIDATE ran in this workdir
    if "candidate" in ctx.artifacts:
        mis = [x for x in load_candidate(ctx)["calls"] if x["consequence"] == "missense"]
        if len(mis) == 1:
            env["REPL_CANDIDATE_RESIDUE"] = json.dumps([load_candidate(ctx)["gene"], mis[0]["aa_pos"], mis[0]["ref_aa"]])
    ctx.run_py("models/protein_rule/build_protein_rule.py", args=[ctx.artifact("controls_rule"), ctx.path("controls")],
               env=env)


def prot_build_parse(ctx):
    out = ctx.stdout("build_protein_rule")
    r = re.search(r"^kept: (\d+) P: (\d+) B: (\d+) dropped: (\{.*\})$", out, re.M)
    chk = re.search(r"\(child check\): (\S+)$", out, re.M)
    m = {"kept": int(r.group(1)), "kept_P": int(r.group(2)), "kept_B": int(r.group(3)),
         "dropped": ast.literal_eval(r.group(4)), "sha256_controls_tsv": sha256_file(ctx.path("controls/controls.tsv")),
         "candidate_residue_check": chk.group(1) if chk else "not printed"}
    if ctx.path("controls/FBN1.fasta").exists():
        fbn1 = "".join(l.strip() for l in open(ctx.path("controls/FBN1.fasta")) if not l.startswith(">"))
        m.update(FBN1_length=len(fbn1), FBN1_first_residue=fbn1[:1])
    return m


def _protein_dir(ctx):
    ctx.link("esm1v_t33_650M_UR90S_1", ctx.input("esm1v_dir"))
    ctx.link("esm2_t33_650M_UR50D", ctx.input("esm2_dir"))
    os.makedirs(ctx.path("alphamissense"), exist_ok=True)
    ctx.link("alphamissense/AlphaMissense_hg38.tsv.gz", ctx.input("alphamissense"))


def _child_missense(ctx):
    c = load_candidate(ctx)
    mis = [x for x in c["calls"] if x["consequence"] == "missense"]
    if len(mis) != 1:
        raise StepError("the candidate does not have exactly one missense call")
    return c["gene"], mis[0]


def prot_score_run(ctx):
    gene, x = _child_missense(ctx)
    ctx.link("controls", ctx.artifact("protein_controls_dir"))
    _protein_dir(ctx)
    child = {"gene": gene, "pos": x["aa_pos"], "ref": x["ref_aa"], "alt": x["alt_aa"], "label": "NA",
             "chrom": x["chrom"].replace("chr", ""), "vcf_pos": str(x["pos"]), "vcf_ref": x["ref"], "vcf_alt": x["alt"]}
    ctx.run_py("models/protein_rule/score.py", args=[ctx.dir], env={"REPL_CHILD_PROTEIN_VARIANT": json.dumps(child)})


def prot_score_parse(ctx):
    out = ctx.stdout("score")
    m = {"am_matched": grab(out, r"AM matched (\d+ of \d+)"),
         "sha256_scores": sha256_file(ctx.path("scores.tsv"))}
    for name, auc in re.findall(r"^(esm1v|esm2|am): AUC=([\d.]+)", out, re.M):
        m[f"auc_{name}"] = float(auc)
    return m


def prot_cal_run(ctx):
    ctx.link("scores.tsv", ctx.artifact("protein_scores"))
    ctx.run_py("models/protein_rule/protein_calibration.py", args=[ctx.path("scores.tsv")])


def prot_cal_parse(ctx):
    out = ctx.stdout("protein_calibration")
    m = {}
    key = {"ESM-1v": "esm1v", "ESM-2": "esm2", "AlphaMissense": "am"}
    blocks = re.split(r"^(?=(?:ESM-1v|ESM-2|AlphaMissense):)", out, flags=re.M)
    for b in blocks:
        r = re.match(r"(ESM-1v|ESM-2|AlphaMissense): nP=(\d+) nB=(\d+) AUC=([\d.]+) CI=\[([\d.]+),([\d.]+)\] -> (\S+)", b)
        if not r:
            continue
        k = key[r.group(1)]
        m[f"{k}_nP_nB"] = [int(r.group(2)), int(r.group(3))]
        m[f"{k}_auc"] = float(r.group(4))
        m[f"{k}_ci"] = [float(r.group(5)), float(r.group(6))]
        m[f"{k}_verdict"] = r.group(7)
        c = re.search(r"child \S+ damage=(\S+) percentile among (\d+) controls=([\d.]+)", b)
        if c:
            dmg = "am_child_score" if k == "am" else f"{k}_child_damage"
            m[dmg] = float(c.group(1))
            m[f"{k}_child_percentile"] = float(c.group(3))
            m[f"{k}_child_n_controls"] = int(c.group(2))
    return m


def placement_run(ctx):
    gene, x = _child_missense(ctx)
    if gene != "BUB1B":
        raise StepError(f"PRE-REG-D was registered for BUB1B alleles; the upstream candidate is {gene}")
    ctx.link("controls", ctx.artifact("protein_controls_dir"))
    ctx.link("scores.tsv", ctx.artifact("protein_scores"))
    _protein_dir(ctx)
    ctx.run_py("models/protein_rule/placement.py", env={
        "REPL_CANDIDATE_ALLELES": json.dumps([[x["protein"], x["aa_pos"], x["ref_aa"], x["alt_aa"]]])})


def placement_parse(ctx):
    out = ctx.stdout("placement")
    c = load_candidate(ctx)
    child = [x["protein"] for x in c["calls"] if x["consequence"] == "missense"][0]
    m = {}
    vals = {}
    for line in out.splitlines():
        r = re.match(r"^(\S+) \| esm1v damage=(\S+) pct=(\S+) \| esm2 damage=(\S+) pct=(\S+) \| am=(\S+) pct=(\S+)$", line)
        if r:
            # the child's allele is reported under a generic name; the two literature alleles keep theirs
            a = "candidate_missense" if r.group(1) == child else r.group(1)
            m[f"{a}_esm1v"] = [float(r.group(2)), float(r.group(3))]
            m[f"{a}_esm2"] = [float(r.group(4)), float(r.group(5))]
            m[f"{a}_am"] = [float(r.group(6)), float(r.group(7))]
            vals[a] = {"esm1v": float(r.group(3)), "esm2": float(r.group(5)), "am": float(r.group(7))}
    # harness: pre-registered falsifier, on percentiles
    trig = 0
    for model in ("esm1v", "esm2", "am"):
        lo = min(vals["I909T"][model], vals["L1012P"][model])
        hi = max(vals["I909T"][model], vals["L1012P"][model])
        t = not (lo <= vals["candidate_missense"][model] <= hi)
        trig += t
        m[f"falsifier_{model}"] = "triggered" if t else "not triggered"
    m["result"] = "NOT PLACED" if trig >= 2 else ("PLACED" if trig == 0 else "MIXED")
    return m


def placeholder_run(ctx):
    raise StepError("placeholder")


def external_run(ctx):
    raise StepError("external")


# ---------------------------------------------------------------- registry
R1o, P1o = _rank_v12(1, False)
R2o, P2o = _rank_v12(2, False)
R1f, P1f = _rank_v12(1, True)
R2f, P2f = _rank_v12(2, True)
R3o, P3o = _rank_v3(False)
R3f, P3f = _rank_v3(True)
R4o, P4o = _rank_v4("orig")
R4b, P4b = _rank_v4("b")
R4f, P4f = _rank_v4("fixed")
R4bf, P4bf = _rank_v4("bfixed")


# ---------------------------------------------------------------- Track 1: spike-in tests of the frozen rules
# Two pre-registered out-of-sample tests write PUBLIC ClinVar Pathogenic / Likely pathogenic alleles into the
# child's own exonic background and re-run the frozen consequence step and ranking rules v3 and v4 on each
# synthetic case. Every input is an artifact of the steps above or a public database, so the tests run here.
# In the as-run layout the project folder (D) and the work folder (W) were two folders; both are the step folder
# here, and every input is linked in under the name the script opens (PORTING_LOG.md).
SPIKEIN_DIR = "track1/spikein"
PREREG_SPIKEIN = REPO_ROOT / "preregistration" / "frozen" / "PRE_REG_SPIKEIN_EPCR.md"


def _spikein_links(ctx, calls=False, ranking=False, parts=False):
    """Link the public databases and the upstream artifacts the spike-in scripts open by name."""
    ctx.link("clinvar.vcf.gz", ctx.input("clinvar_vcf"))
    ctx.link("hp.obo", ctx.input("hpo_obo"))
    ctx.link("genes_to_phenotype.txt", ctx.input("hpo_genes_to_phenotype"))
    ctx.link(GENCODE_NAME, ctx.input("gtf"))
    ctx.link("child_exonic_consequence_fixed.tsv", ctx.artifact("consequence_fixed"))
    if calls:
        ctx.link("child_exonic_calls.tsv", ctx.artifact("child_exonic_calls"))
        ctx.link("protein_coding_exons_hg38.bed", ctx.input("exon_bed"))
        # the drivers launch these two by file name from the step folder (W in the as-run layout)
        copy_into(ctx, SPIKEIN_DIR + "/calls_param.py", "calls_param.py")
        copy_into(ctx, SPIKEIN_DIR + "/consequence_param.py", "consequence_param.py")
    if ranking:
        ctx.link("ranking_v3_summary_fixed.tsv", ctx.artifact("ranking_v3_fixed"))
        ctx.link("ranking_v4_summary_fixed.tsv", ctx.artifact("ranking_v4_fixed"))
    if parts:
        link_parts(ctx)


def _draft_rows(ctx):
    """The 10 draft submission rows, rebuilt from the ranking artifacts by the analysis library's own ROW-MAP
    (replicate/helpers/draft_rows_csv.py). The authors' CSV holds the child's calls and is not shipped."""
    out = ctx.private / "track1_draft_rows.csv"
    if not out.exists():
        ctx.run_helper("draft_rows_csv.py", args=[ANALYSIS / SPIKEIN_DIR, out])
    return out


def spk_g1_run(ctx):
    _spikein_links(ctx, calls=True, ranking=True, parts=True)
    ctx.run_py(SPIKEIN_DIR + "/validate.py",
               env={"REPL_FASTA": ctx.input("fasta"), "REPL_DRAFT_CSV": str(_draft_rows(ctx))})


def spk_g1_parse(ctx):
    g = json.load(open(ctx.path("val_G1.json")))
    return {k: g[k] for k in ("G1a_consequence_identical", "G1b_calls_roundtrip_identical",
                              "G1c_v3_summary_identical", "G1d_v4_summary_identical", "G1e_amended_top10",
                              "G1e_rows_equal_draft", "G1e_mt_genes_in_unamended_top10")}


def spk_trials_run(ctx):
    _spikein_links(ctx, calls=True, parts=True)
    ctx.link("PRE_REG_SPIKEIN_EPCR.md", PREREG_SPIKEIN)
    ctx.run_py(SPIKEIN_DIR + "/run_spikein.py",
               env={"REPL_VCF": ctx.input("vcf"), "REPL_FASTA": ctx.input("fasta")})


def spk_trials_parse(ctx):
    san = json.load(open(ctx.path("sanity.json")))
    log = ctx.path("run.log").read_text()
    m = {k: san[k] for k in ("removed_rows", "S2_masked_equals_original_minus_bub1b", "S1_bub_keys_absent",
                             "S1_no_bub1b_candidate", "S1_bub1b_not_ranked", "S3_bub1b_v4_rank",
                             "S3_bub1b_v3_rank", "S3_v4_order_equals_unspiked", "S3_v3_order_equals_unspiked",
                             "masked_v4_top10", "n_trials", "pool_size_set18", "child_bub1b_nonsense_in_pool")}
    m.update({"prereg_sha256": grab(log, r"pre-reg sha256 ([0-9a-f]{64})"),
              "child_vcf_unchanged": bool(re.search(r"^.*child VCF sha256 after \S+ unchanged: True$", log, re.M)),
              "eligible_pool_alleles": grab(log, r"eligible pool alleles: (\d+)", int),
              "synthetic_stop_loss_alleles": grab(log, r"synthetic stop-loss alleles: (\d+)", int),
              "trials_total": grab(log, r"trials done: (\d+)", int),
              "sha256_trials": sha256_file(ctx.path("trials.tsv")),
              "sha256_alleles": sha256_file(ctx.path("alleles.tsv"))})
    return m


def spk_analyze_run(ctx):
    _spikein_links(ctx)
    tr = ctx.artifact("spikein_trials")
    for name in ("trials.tsv", "alleles.tsv", "sanity.json"):
        ctx.link(name, os.path.join(tr, name))
    ctx.run_py(SPIKEIN_DIR + "/analyze.py", env={"REPL_DRAFT_CSV": str(_draft_rows(ctx))})


def spk_analyze_parse(ctx):
    s = json.load(open(ctx.path("summary.json")))
    st = s["strata"]
    a4, a3 = st["A"]["v4"], st["A"]["v3"]
    m = {"epcr_vector": s["epcr"]["epcr"], "epcr_decimals": s["epcr"]["decimals"],
         "A_v4_N": a4["N"], "A_v4_rank1_recall": a4["p1"], "A_v4_rank1_ci": a4["p1_ci"],
         "A_v4_top10": a4["top10"], "A_v4_top10_ci": a4["top10_ci"],
         "A_v4_rank_dist_1_10": a4["dist_1_10"], "A_v4_not_ranked": a4["none"],
         "A_v3_rank1_recall": a3["p1"],
         "A_BUB_v4_rank1_recall": st["A-BUB"]["v4"]["p1"],
         "B_v4_rank1_recall": st["B"]["v4"]["p1"], "B_v4_top10": st["B"]["v4"]["top10"],
         "C1_v4_rank1_recall": st["C1"]["v4"]["p1"], "C2_HOM_v4_top10": st["C2-HOM"]["v4"]["top10"],
         "C2_CH_v4_rank1_recall": st["C2-CH"]["v4"]["p1"],
         "D_v4_rank1_recall": st["D"]["v4"]["p1"], "D_v3_rank1_recall": st["D"]["v3"]["p1"],
         "E_v4_rank1_recall": st["E"]["v4"]["p1"], "E_v4_N": st["E"]["v4"]["N"],
         "D3_stop_alleles": s["D3"]["stop_alleles"], "D3_labelled_stop_lost": s["D3"]["labelled_stop_lost"],
         "D3_stop_allele_candidate": s["D3"]["stop_allele_candidate"],
         "D5_v4_only": s["D5"]["v4_only"], "D5_v3_only": s["D5"]["v3_only"],
         "D5_mcnemar_exact_p": s["D5"]["mcnemar_exact_p"],
         "mean_rank_points": s["score"]["mean_points"], "mean_fmax": s["score"]["mean_fmax"],
         "ordinal_vector_identical": s["score"]["ordinal_vector_identical"],
         "sha256_summary": sha256_file(ctx.path("summary.json"))}
    m.update({"decision_" + k: v for k, v in s["decisions"].items()})
    return m


# ---------------------------------------------------------------- the two checks that need no data at all
# Both read numbers this repository ships and re-derive a published result from the pre-registered rule, with a
# second implementation written from the pre-registration text rather than a call into the analysis script. They
# are the only steps that need no input of any kind, which is why they are worth having: a reader with nothing but
# a clone can check that the epcr column we submitted follows the rule we registered, from the counts we published.
def epcr_check_run(ctx):
    ctx.run_helper("epcr_from_counts.py", args=[REPO_ROOT])


def epcr_check_parse(ctx):
    out = ctx.stdout("epcr_from_counts")
    return {"epcr_vector": lit(out, r"^recomputed EPCR: (\[.*\])$"),
            "epcr_decimals": grab(out, r"^decimals: (\d+)$", int),
            "matches_submitted_vector": grab(out, r"^matches published: (\w+)$") == "True",
            "strictly_decreasing": grab(out, r"^strictly decreasing: (\w+)$") == "True",
            "all_in_unit_interval": grab(out, r"^all in \(0, 1\]: (\w+)$") == "True",
            "primary_N": grab(out, r"^primary stratum N: (\d+)$", int),
            "rank1_recall_from_counts": grab(out, r"^rank-1 recall from the counts: (\S+)$", float),
            "top10_rate_from_counts": grab(out, r"^top-10 rate from the counts: (\S+)$", float)}


def rowmap_check_run(ctx):
    ctx.run_helper("rowmap_decision_from_points.py", args=[REPO_ROOT])


def rowmap_check_parse(ctx):
    out = ctx.stdout("rowmap_decision_from_points")
    return {"primary_trials": grab(out, r"^primary trials per combination: (\d+)$", int),
            "draft_mean_points": grab(out, r"^mean rank points R0xC1: (\S+)$", float),
            "winner_mean_points": grab(out, r"^mean rank points P5xC3: (\S+)$", float),
            "winner": grab(out, r"^winner: (\S+)$"),
            "delta_vs_draft": grab(out, r"^delta vs R0xC1: (\S+)$", float),
            "condition_a_margin": grab(out, r"^condition a, .*: (\w+)$") == "True",
            "condition_b_gate": grab(out, r"^condition b, .*: (\w+)$") == "True",
            "condition_c_both_strata": grab(out, r"^condition c, .*: (\w+)$") == "True",
            "verdict": grab(out, r"^verdict: (.+)$")}

STEPS = [
    Step("ALIGN-01", "Alignment of the organiser FASTQs to GRCh38 (Parabricks 4.7.1 fq2bam)", "upstream (not a register test)",
         "T1", "full", kind="external", gpu=True, vram_gb=14.0, ram_gb=None, disk_gb=None,
         runtime="measured: 82 min 6 s on one RTX 3090 (fq2bam log); GPU memory 13.7 to 14.0 GB; peak RAM and temporary "
                 "disk not recorded", inputs=("fastq_l1_r1", "fastq_l1_r2", "fastq_l2_r1", "fastq_l2_r2",
         "fastq_l3_r1", "fastq_l3_r2", "fastq_l4_r1", "fastq_l4_r2", "fasta"),
         note="External: procedure in replicate/EXTERNAL_STEPS.md. tools/fq2bam.sh (syntax-checked only, never run) "
              "builds our command (Parabricks 4.7.1-1 fq2bam, container in env/containers.txt); give the BAM as input "
              "'bam'. A fresh alignment is not byte-identical to ours; BAM-derived counts are then compared "
              "as NOT COMPARABLE unless a tolerance for a different alignment is stated.", privacy="patient",
         execute=external_run),
    Step("S0.1", "Sex from BAI read counts (chrX and chrY versus autosomes)", "S0.1", "T1", "quick", ram_gb=1,
         disk_gb=0.01, inputs=("bam",), scripts=("track1/stage1_targeted/s01_sex_from_bai.py",),
         execute=s01_run, parse=s01_parse, privacy="patient"),
    Step("H01", "CEP57 11-bp duplication: junction signal versus background", "H01", "T1", "quick", ram_gb=1,
         disk_gb=0.01, inputs=("bam",), scripts=("track1/stage1_targeted/h01_cep57_dup11.py",),
         execute=h01_run, parse=h01_parse, privacy="patient"),
    Step("H-BATCH", "H02 site pileup, H03 split/clip/discordant rates, H05 low-VAF, H06 het gaps, H12 NAA10 depth",
         "H02, H03, H05, H06, H12", "T1", "quick", ram_gb=2, disk_gb=0.01, inputs=("bam", "vcf"),
         scripts=("track1/stage1_targeted/h_batch.py",), execute=hbatch_run, parse=hbatch_parse, privacy="patient"),
    Step("H08", "Chromosome-level depth from sampled 1 Mb bins", "Step 2 (H08 arm-level depth)", "T1", "quick", ram_gb=1,
         disk_gb=0.01, inputs=("bam",), scripts=("track1/sv_cnv/h08_depth.py",), execute=h08_run, parse=h08_parse,
         privacy="patient"),
    Step("DETECT-LIMIT", "Depth noise and the smallest detectable whole-chromosome shift", "Readout detection limit", "T1",
         "quick", ram_gb=1, disk_gb=0.01, inputs=("bam",), scripts=("track1/sv_cnv/detection_limit.py",),
         execute=detlim_run, parse=detlim_parse, privacy="patient"),
    Step("CNV-V1", "Copy-number mosaicism rule v1 (1 Mb bins, GC correction, per-chromosome call)",
         "Copy-number mosaicism rule v1, amended run", "T1", "quick", ram_gb=3, disk_gb=0.05, inputs=("bam", "fasta"),
         rules=("CNV_RULE_v1.md",), scripts=("track1/sv_cnv/cnv_bins.py", "track1/sv_cnv/cnv_call.py"),
         execute=cnv_run, parse=cnv_parse, privacy="patient",
         runtime="measured: about 3 min with 6 workers (2026-10-19, bin-file timestamps)",
         note="The rule file contains a local file name and is held back from the repository; it is available to "
              "organisers on request. The step is refused unless its folder is given as rules_extra_dir and the file "
              "matches its recorded sha256 (rules/CNV_RULE_v1.sha256)."),
    Step("SV-MANTA", "Manta 1.6.0 SV calls, SV rule v1 and ClinGen dosage overlap (H03 SV level, H04)", "Step 2: structural variants",
         "T1", "full", kind="external", ram_gb=16, disk_gb=None, inputs=("bam", "fasta", "gtf", "clingen_gene_curation"),
         privacy="patient",
         runtime="measured: 26 min 4 s for Manta (-j 12 -g 16; manta log)",
         scripts=("as_run/track1/sv_cnv/sv_rule_v1.py", "as_run/track1/sv_cnv/h03_h04_sv.py"), execute=external_run,
         note="External: procedure in replicate/EXTERNAL_STEPS.md. Manta runs in the container of env/containers.txt "
              "(launcher held back: local paths); sv_rule_v1.py and h03_h04_sv.py still carry path constants. The "
              "ClinGen list release used (16 Oct 2026) cannot be re-fetched from upstream; our copy is in references/. "
              "The Step 4 DICER1 depth script is held back (it hard-codes two of the child's calls). Expected values: "
              "register 'Step 2' and 'Step 4'."),
    Step("H13-SMN", "SMN1 / SMN2 diagnostic-base counts", "Step 5 and Step 6 (H13)", "T1", "full", kind="external",
         network=True, ram_gb=None, disk_gb=None, runtime="measured: about 3 min (session timestamps)", inputs=("bam",),
         privacy="patient", execute=external_run,
         note="External: procedure in replicate/EXTERNAL_STEPS.md. The paralog positions come from Ensembl REST "
              "sequences (network); the count scripts are held back (local path constants)."),
    Step("M-REG-BORZOI", "Borzoi regulatory-model calibration on GTEx eQTL controls", "Model calibration results (Borzoi)",
         "M", "full", kind="external", gpu=True, vram_gb=None, ram_gb=None, disk_gb=None, network=True,
         runtime="measured: 349 s for the run that produced the result, on one RTX 3090 (run log); the five runs "
                 "together, four of which stopped early, took 413 s; GPU memory not recorded",
         execute=external_run,
         scripts=("as_run/models/regulatory/borzoi_score.py", "as_run/models/regulatory/gtex_probe.py"),
         note="External: procedure in replicate/EXTERNAL_STEPS.md; needs the GTEx API (network) for the control set "
              "and one GPU; the as-run scripts are in as_run/models/regulatory/ with path constants. Register result: "
              "control AUC 0.496 (chance level)."),
    Step("BLIND-01A", "Exonic non-reference calls of the organiser VCF", "Genome-wide blind exonic pass", "T1", "quick",
         ram_gb=2, disk_gb=0.05, inputs=("vcf", "exon_bed"), provides={"child_exonic_calls": "child_exonic_calls.tsv"},
         scripts=("track1/blind_exonic/child_exonic_calls.py",), execute=blind01a_run, parse=blind01a_parse, privacy="patient"),
    Step("BLIND-01B", "gnomAD v4.1 exome frequency for each exonic call (remote indexed reads, 4 workers)",
         "Genome-wide blind exonic pass", "T1", "full", network=True, ram_gb=4, disk_gb=0.05,
         runtime="measured: about 3.5 h wall with 4 workers and restarts (2026-10-17, part-file timestamps)",
         needs=("child_exonic_calls",), provides={"gnomad_parts": "."},
         scripts=("track1/blind_exonic/gnomad_match.py",), execute=blind01b_run, parse=blind01b_parse, privacy="patient",
         note="Network: reads byte ranges of the public gnomAD S3 files around the child's calls."),
    Step("BLIND-01C", "Rarity classes of the exonic calls", "Genome-wide blind exonic pass", "T1", "quick",
         ram_gb=1, disk_gb=0.01, needs=("gnomad_parts",), scripts=("track1/blind_exonic/blind_rare_exonic.py",),
         execute=blind01c_run, parse=blind01c_parse, privacy="patient"),
    Step("CONSEQ-V1", "Consequence annotation, original script", "Consequence step (2026-10-17)", "T1", "quick",
         ram_gb=4, disk_gb=0.05, inputs=("fasta", "gtf"), needs=("gnomad_parts",),
         provides={"consequence_orig": "child_exonic_consequence.tsv"},
         scripts=("track1/blind_exonic/consequence.py", "track1/blind_exonic/summarize_consequence.py"),
         execute=conseq_v1_run, parse=conseq_v1_parse, privacy="patient"),
    Step("C-FIX-01", "Consequence annotation, minus-strand fix, and the row-level diff", "C-FIX-01", "T1", "quick",
         ram_gb=4, disk_gb=0.05, inputs=("fasta", "gtf"), needs=("gnomad_parts", "consequence_orig"),
         provides={"consequence_fixed": "child_exonic_consequence_fixed.tsv"},
         scripts=("track1/blind_exonic/consequence_fixed.py", "track1/blind_exonic/summarize_consequence.py"),
         execute=cfix01_run, parse=cfix01_parse, privacy="patient"),
    Step("C-FIX-01-FU", "Compound-pattern check on both tables", "C-FIX-01 follow-up", "T1", "quick", ram_gb=1, disk_gb=0.01,
         needs=("consequence_orig", "consequence_fixed"),
         scripts=("track1/blind_exonic/compound_check.py", "track1/blind_exonic/compound_check_fixed.py"),
         execute=cfix01fu_run, parse=cfix01fu_parse, privacy="patient"),
    Step("RANK-V1", "Ranking rule v1 (original table)", "Ranking v1", "T1", "quick", ram_gb=1, disk_gb=0.01,
         needs=("consequence_orig",), provides={"ranking_v1": "ranking_v1_summary.tsv"}, rules=("RANKING_RULE_v1.md",),
         scripts=("track1/ranking/ranking_v1.py",), execute=R1o, parse=P1o, privacy="patient"),
    Step("RANK-V2", "Ranking rule v2 (original table)", "Ranking v2", "T1", "quick", ram_gb=1, disk_gb=0.01,
         needs=("consequence_orig",), provides={"ranking_v2": "ranking_v2_summary.tsv"}, rules=("RANKING_RULE_v2.md",),
         scripts=("track1/ranking/ranking_v2.py",), execute=R2o, parse=P2o, privacy="patient"),
    Step("RANK-V3", "Ranking rule v3, ClinVar tiers (original table)", "Ranking v3", "T1", "quick", ram_gb=1, disk_gb=0.01,
         inputs=("clinvar_vcf",), needs=("consequence_orig",), provides={"ranking_v3": "ranking_v3_summary.tsv"},
         rules=("RANKING_RULE_v3.md",), scripts=("track1/ranking/ranking_v3.py",), execute=R3o, parse=P3o, privacy="patient"),
    Step("RANK-V4", "Ranking rule v4, phenotype layer, run 1 (original table)", "Ranking v4 (run 1)", "T1", "quick",
         ram_gb=1, disk_gb=0.01, inputs=("hpo_obo", "hpo_genes_to_phenotype"), needs=("ranking_v3",),
         provides={"ranking_v4": "ranking_v4_summary.tsv"}, rules=("RANKING_RULE_v4.md",),
         scripts=("track1/ranking/ranking_v4.py",), execute=R4o, parse=P4o, privacy="patient"),
    Step("RANK-V4B", "Ranking rule v4 with Amendment 1 (chrM excluded), run 2", "Ranking v4 (run 2)", "T1", "quick",
         ram_gb=1, disk_gb=0.01, inputs=("hpo_obo", "hpo_genes_to_phenotype"), needs=("ranking_v3",),
         provides={"ranking_v4b": "ranking_v4b_summary.tsv"}, rules=("RANKING_RULE_v4.md",),
         scripts=("track1/ranking/ranking_v4b.py",), execute=R4b, parse=P4b, privacy="patient"),
    Step("RANK-V1F", "Ranking rule v1 on the corrected table", "C-FIX-01", "T1", "quick", ram_gb=1, disk_gb=0.01,
         needs=("consequence_fixed",), provides={"ranking_v1_fixed": "ranking_v1_summary_fixed.tsv"},
         rules=("RANKING_RULE_v1.md",), scripts=("track1/ranking/ranking_v1_fixed.py",), execute=R1f, parse=P1f, privacy="patient"),
    Step("RANK-V2F", "Ranking rule v2 on the corrected table", "C-FIX-01", "T1", "quick", ram_gb=1, disk_gb=0.01,
         needs=("consequence_fixed",), provides={"ranking_v2_fixed": "ranking_v2_summary_fixed.tsv"},
         rules=("RANKING_RULE_v2.md",), scripts=("track1/ranking/ranking_v2_fixed.py",), execute=R2f, parse=P2f, privacy="patient"),
    Step("RANK-V3F", "Ranking rule v3 on the corrected table", "C-FIX-01", "T1", "quick", ram_gb=1, disk_gb=0.01,
         inputs=("clinvar_vcf",), needs=("consequence_fixed",), provides={"ranking_v3_fixed": "ranking_v3_summary_fixed.tsv"},
         rules=("RANKING_RULE_v3.md",), scripts=("track1/ranking/ranking_v3_fixed.py",), execute=R3f, parse=P3f, privacy="patient"),
    Step("RANK-V4F", "Ranking rule v4 on the corrected v3 summary", "C-FIX-01", "T1", "quick", ram_gb=1, disk_gb=0.01,
         inputs=("hpo_obo", "hpo_genes_to_phenotype"), needs=("ranking_v3_fixed",),
         provides={"ranking_v4_fixed": "ranking_v4_summary_fixed.tsv"}, rules=("RANKING_RULE_v4.md",),
         scripts=("track1/ranking/ranking_v4_fixed.py",), execute=R4f, parse=P4f, privacy="patient"),
    Step("RANK-V4BF", "Ranking rule v4 WITH Amendment 1 on the corrected v3 summary (frozen rule as written)",
         "BUG-V4-CHRM", "T1", "quick", ram_gb=0.5, disk_gb=0.01, inputs=("hpo_obo", "hpo_genes_to_phenotype"),
         needs=("ranking_v3_fixed",), provides={"ranking_v4b_fixed": "ranking_v4b_summary.tsv"}, rules=("RANKING_RULE_v4.md",),
         scripts=("track1/ranking/ranking_v4b.py",), execute=R4bf, parse=P4bf, privacy="patient",
         runtime="measured: about 0.3 s (same script as RANK-V4B)",
         note="ranking_v4b.py, unchanged, run on the corrected v3 summary (linked as ranking_v3_summary.tsv). "
              "This is the step that implements RANKING_RULE_v4.md including Amendment 1 on the corrected table; "
              "T1-CANDIDATE takes the candidate from it. RANK-V4F keeps ranking_v4_fixed.py to reproduce the recorded output."),
    Step("C-FIX-02", "Consequence fix validated on ClinVar; gene-level diff of the rankings", "C-FIX-02", "T1", "quick",
         ram_gb=6, disk_gb=0.01, inputs=("clinvar_vcf", "gtf", "fasta"),
         needs=("ranking_v1", "ranking_v2", "ranking_v3", "ranking_v4", "ranking_v1_fixed", "ranking_v2_fixed",
                "ranking_v3_fixed", "ranking_v4_fixed"),
         scripts=("track1/blind_exonic/validate_consequence.py",), execute=cfix02_run, parse=cfix02_parse, privacy="patient",
         note="The ClinVar validation itself uses public data only; the ranking diff reads patient-derived summaries."),
    Step("T1-CANDIDATE", "Candidate gene and calls from the upstream ranking (harness)", "harness", "H", "quick",
         kind="harness", ram_gb=4, disk_gb=0.01, inputs=("gtf", "fasta"), needs=("ranking_v4b_fixed", "consequence_fixed"),
         provides={"candidate": "@private/candidate.json"}, execute=candidate_run, parse=candidate_parse, privacy="patient",
         note="Writes private/candidate.json (patient coordinates) in the workdir; no coordinate is in code or config."),
    Step("READCHECK", "Read-level check of the candidate calls", "Read-level check of the two BUB1B calls", "T1", "quick",
         ram_gb=1, disk_gb=0.01, inputs=("bam",), needs=("candidate",),
         scripts=("track1/readlevel/bub1b_readcheck.py",), execute=readcheck_run, parse=readcheck_parse, privacy="patient"),
    Step("P1", "Read-backed phasing of the candidate pair (fragment-span survey)", "PRE-REG-2026-10-20 P1", "T1", "quick",
         ram_gb=1, disk_gb=0.01, inputs=("vcf", "bam"), needs=("candidate",),
         scripts=("track1/readlevel/p1_het_list_vcf.sh", "track1/readlevel/p1_tlen_bridging.py"),
         execute=p1_run, parse=p1_parse, privacy="patient"),
    Step("P2", "Rare-variant sweep, phenocopy and U12-spliceosome genes", "PRE-REG-2026-10-20 P2", "T1", "quick",
         ram_gb=2, disk_gb=0.01, inputs=("vcf", "vcf_tbi", "gtf"), needs=("gnomad_parts", "consequence_fixed"),
         scripts=("track1/readlevel/p2_annot.py",), execute=p2_run, parse=p2_parse, privacy="patient"),
    Step("P3", "Exact-allele check, published CENATAC family alleles", "PRE-REG-2026-10-20-C (P3)", "T1", "quick",
         ram_gb=2, disk_gb=0.01, inputs=("gtf", "fasta", "vcf", "vcf_tbi", "bam"),
         scripts=("track1/readlevel/cenatac_check.py",), execute=p3_run, parse=p3_parse, privacy="patient"),
    Step("T2-DEPMAP-01", "DepMap 24Q4 gene-effect correlation with BUB1B", "T2-DEPMAP-01", "T2", "quick",
         ram_gb=6, disk_gb=0.01, inputs=("depmap_gene_effect",), scripts=("track2/depmap/dep_corr.py",),
         execute=depmap01_run, parse=depmap01_parse),
    Step("T2-P4", "DepMap on-target dependency for candidate targets", "PRE-REG-2026-10-20 T2-P4", "T2", "quick",
         ram_gb=6, disk_gb=0.01, inputs=("depmap_gene_effect", "depmap_model"),
         scripts=("track2/depmap/p4_depmap_safety.py",), execute=p4_run, parse=p4_parse),
    Step("PRE-REG-B", "DepMap lever screen against BUB1B with a genome-wide null", "PRE-REG-2026-10-20-B", "T2", "quick",
         ram_gb=8, disk_gb=0.01, inputs=("depmap_gene_effect",), scripts=("track2/depmap/lever_screen.py",),
         execute=lever_run, parse=lever_parse),
    Step("T2-TRIAL-01", "ClinicalTrials.gov NMN / NR query", "T2-TRIAL-01", "T2", "full", network=True, ram_gb=1,
         disk_gb=0.01, scripts=("track2/trials/ctgov_nmn_nr_query.sh",), execute=trial_run, parse=trial_parse,
         note="Network: one public API query by drug names only."),
    Step("T2-POWER-01", "Illustrative power guide", "T2-POWER-01", "T2", "quick", ram_gb=0.5, disk_gb=0.01,
         scripts=("track2/power/power_guide.py",), execute=power_run, parse=power_parse),
    Step("T2-P5", "DepMap on-target dependency for the targets not covered by T2-P4", "PRE-REG-T2-P5 / T2-P5 RESULT",
         "T2", "quick", ram_gb=2.5, disk_gb=0.01, inputs=("depmap_gene_effect", "depmap_model"),
         scripts=("track2/depmap/p5_depmap_safety.py",), execute=p5_run, parse=p5_parse),
    Step("T2-CLASS-01", "Niacin and nicotinamide: one candidate or two (regulatory class)", "PRE-REG-T2-CLASS-01", "T2",
         "full", kind="external", network=True, ram_gb=None, disk_gb=None, execute=external_run,
         note="External: procedure in replicate/EXTERNAL_STEPS.md. Not a script: criteria C1 to C4 were applied to "
              "openFDA, PubMed and ChEMBL results (network, by drug name), with T2-P5 as criterion C3. Result in the "
              "register: SEPARATE, then DROP nicotinamide."),
    Step("M-EVO2-CAL-01-CONTROLS", "Calibration control pool from ClinVar (rule section 1)", "M-EVO2-CAL-01", "M", "quick",
         ram_gb=1, disk_gb=0.01, inputs=("clinvar_vcf",), provides={"controls_rule": "controls_rule.tsv"},
         rules=("CALIBRATION_RULE.md",), scripts=("models/protein_rule/build_rule_controls.py",),
         execute=controls_run, parse=controls_parse),
    Step("M-EVO2-CAL-01-SCORE", "Evo 2 7B scoring of the 198 controls", "M-EVO2-CAL-01", "M", "full", gpu=True,
         vram_gb=16, ram_gb=32, disk_gb=1, runtime="measured: about 4 min for 198 variants after model load (2026-10-20 log)",
         inputs=("evo2_weights", "fasta"), needs=("controls_rule",), provides={"evo2_control_scores": "evo2_rule_controls_out.tsv"},
         rules=("CALIBRATION_RULE.md",), scripts=("models/evo2/evo2_score_safe.py", "models/evo2/configs/evo2-7b-1m.yml"),
         execute=evo2_score_run, parse=evo2_score_parse,
         note="Peak GPU allocation 13.53 GiB in the original run. NVTE_ALLOW_UNSAFE_PICKLE_EXTRA_STATE=1 is set for this "
              "process only, and only after the weights' sha256 matches (disclosed deviation)."),
    Step("M-EVO2-CAL-01", "Evo 2 calibration AUC and bootstrap CI (rule section 2)", "M-EVO2-CAL-01", "M", "quick",
         ram_gb=0.5, disk_gb=0.01, needs=("evo2_control_scores", "controls_rule"), rules=("CALIBRATION_RULE.md",),
         scripts=("models/evo2/evo2_auc_bootstrap.py",), execute=evo2_auc_run, parse=evo2_auc_parse),
    Step("M-EVO2-CHILD-01", "Evo 2 deltas for the candidate calls (exploratory)", "M-EVO2-CHILD-01", "M", "full", gpu=True,
         vram_gb=16, ram_gb=32, disk_gb=0.1, runtime="measured: about 1 min after model load (2026-10-20 log)",
         inputs=("evo2_weights", "fasta"), needs=("candidate",), rules=("CALIBRATION_RULE.md",),
         scripts=("models/evo2/evo2_score_safe.py",), execute=evo2_child_run, parse=evo2_child_parse, privacy="patient"),
    Step("M-PROT-CAL-02-BUILD", "Protein inputs for the rule-compliant controls", "M-PROT-CAL-02", "M", "quick",
         ram_gb=4, disk_gb=0.01, inputs=("gtf", "fasta"), needs=("controls_rule",),
         provides={"protein_controls_dir": "controls"}, rules=("CALIBRATION_RULE.md",),
         scripts=("models/protein_rule/build_protein_rule.py",), execute=prot_build_run, parse=prot_build_parse,
         note="Public data only. When T1-CANDIDATE ran in the same workdir, the script also checks the reference residue "
              "of the candidate missense (INFO value candidate_residue_check); otherwise that check prints None."),
    Step("M-PROT-CAL-02-SCORE", "ESM-1v, ESM-2 and AlphaMissense scores for controls and the candidate missense",
         "M-PROT-CAL-02", "M", "full", gpu=True, vram_gb=6, ram_gb=8, disk_gb=0.1,
         runtime="measured: about 1 min (2026-10-20 log timestamps)",
         inputs=("esm1v_dir", "esm2_dir", "alphamissense"), needs=("protein_controls_dir", "candidate"),
         provides={"protein_scores": "scores.tsv"}, rules=("CALIBRATION_RULE.md",), scripts=("models/protein_rule/score.py",),
         execute=prot_score_run, parse=prot_score_parse, privacy="patient"),
    Step("M-PROT-CAL-02", "Protein-model AUC, CI and the candidate's percentile (rule sections 2 and 3)", "M-PROT-CAL-02",
         "M", "quick", ram_gb=0.5, disk_gb=0.01, needs=("protein_scores",), rules=("CALIBRATION_RULE.md",),
         scripts=("models/protein_rule/protein_calibration.py",), execute=prot_cal_run, parse=prot_cal_parse, privacy="patient"),
    Step("PRE-REG-D", "Placement of the candidate missense among BUB1B I909T and L1012P", "PRE-REG-2026-10-20-D", "M", "full",
         gpu=True, vram_gb=6, ram_gb=8, disk_gb=0.01, inputs=("esm1v_dir", "esm2_dir", "alphamissense"),
         needs=("protein_controls_dir", "protein_scores", "candidate"), rules=("CALIBRATION_RULE.md",),
         scripts=("models/protein_rule/placement.py",), execute=placement_run, parse=placement_parse, privacy="patient"),
    Step("PRE-REG-SPIKEIN-EPCR-CHECK",
         "The submitted EPCR column re-derived from the published rank counts (no input of any kind)",
         "PRE-REG-SPIKEIN-EPCR", "T1", "quick", kind="harness", ram_gb=0.5, disk_gb=0.01,
         execute=epcr_check_run, parse=epcr_check_parse,
         note="Needs nothing: no dataset, no network, no GPU, not even the organisers' VCF. It reads the primary "
              "stratum's rank counts from preregistration/spikein/summary.json, which ships, and re-derives the ten "
              "EPCR values with a second implementation of section 8 of the pre-registration "
              "(replicate/helpers/epcr_from_counts.py), written from the pre-registration text and not calling "
              "analyze.py. So it answers, for a reader with only a clone of this repository, whether the epcr column "
              "we submitted follows the rule we registered from the counts we published. It does not check the "
              "counts themselves: PRE-REG-SPIKEIN-TRIALS and PRE-REG-SPIKEIN do that, and they need the dataset."),
    Step("PRE-REG-ROWMAP-CHECK",
         "The ROW-MAP decision re-applied to the published points distributions (no input of any kind)",
         "PRE-REG-ROWMAP", "T1", "quick", kind="harness", ram_gb=0.5, disk_gb=0.01,
         execute=rowmap_check_run, parse=rowmap_check_parse,
         note="Needs nothing, like the step above. It reads the per-combination points distributions from "
              "preregistration/rowmap/summary_rowmap.json, recomputes the mean rank points of all 18 combinations "
              "and the gain over the draft rule, and re-applies decision D-RM-1 with a second implementation "
              "(replicate/helpers/rowmap_decision_from_points.py). Conditions (a) and (c) are recomputed; condition "
              "(b) is a stratified gene-cluster bootstrap over per-trial scores that are not shipped, so its "
              "interval is read from the published result rather than recomputed, and the helper says so. The test "
              "itself is the external step PRE-REG-ROWMAP."),
    Step("PRE-REG-ROWMAP", "ROW-MAP: which two variants go in a submitted row", "PRE-REG-ROWMAP", "T1", "full",
         kind="external", ram_gb=None, disk_gb=None,
         runtime="measured: 66 s wall for the trials and about 30 s for the analysis (run_rowmap.log timestamps)",
         inputs=("vcf", "clinvar_vcf", "alphamissense"), privacy="patient", execute=external_run,
         scripts=("as_run/track1/rowmap/run_rowmap.py", "as_run/track1/rowmap/analyze_rowmap.py",
                  "as_run/track1/rowmap/propose_csv.py", "as_run/track1/rowmap/mech_check.py",
                  "as_run/track1/rowmap/feasibility_decoy.py", "as_run/track1/rowmap/bub1b_interval.py"),
         note="External: procedure in replicate/EXTERNAL_STEPS.md; the as-run scripts are in as_run/track1/rowmap/ "
              "and the result in preregistration/rowmap/. Not run by the harness for three reasons named there: it "
              "imports the organisers' evaluation.py, which is not ours to ship; its gate S-R4 pins the sha256 of "
              "the as-run spike-in library, which the ported copies cannot have; and it compares its rows against "
              "the submitted CSV, which holds the child's ten rows. Register result: adopt P5 x C3, mean rank "
              "points 80.20 against 49.10 for the draft rule R0."),
    Step("PRE-REG-SPIKEIN-G1",
         "Spike-in gate G1: the spike-in code reproduces the frozen pipeline outputs on the real, unspiked data",
         "PRE-REG-SPIKEIN-EPCR", "T1", "quick", ram_gb=4, disk_gb=0.1,
         inputs=("fasta", "gtf", "clinvar_vcf", "hpo_obo", "hpo_genes_to_phenotype", "exon_bed"),
         needs=("gnomad_parts", "child_exonic_calls", "consequence_fixed", "ranking_v3_fixed", "ranking_v4_fixed"),
         rules=("RANKING_RULE_v3.md", "RANKING_RULE_v4.md"),
         scripts=(SPIKEIN_DIR + "/validate.py", SPIKEIN_DIR + "/spikelib.py", SPIKEIN_DIR + "/calls_param.py",
                  SPIKEIN_DIR + "/consequence_param.py"),
         needs_input_match=("clinvar_vcf",),
         execute=spk_g1_run, parse=spk_g1_parse, privacy="patient",
         note="The gate the pre-registration required before the spike-in was frozen: the parametrised copies of the "
              "frozen extraction and consequence scripts, and the ranking library the spike-in uses, must reproduce "
              "the recorded tables and summaries byte for byte on the real data with no spike. G1a to G1d are "
              "byte-identity against the artifacts of BLIND-01A, C-FIX-01, RANK-V3F and RANK-V4F. G1e is weaker here "
              "than in the original run: it compared the draft ROW-MAP rows against the authors' submitted CSV, which "
              "holds the child's calls and is not shipped, so the harness rebuilds those rows with the analysis "
              "library's own ROW-MAP (replicate/helpers/draft_rows_csv.py) and G1e becomes a self-consistency check."),
    Step("PRE-REG-SPIKEIN-TRIALS",
         "Spike-in trials: public ClinVar P/LP alleles written into the child's background, 1,611 synthetic cases",
         "PRE-REG-SPIKEIN-EPCR", "T1", "quick", ram_gb=4, disk_gb=0.5,
         inputs=("vcf", "fasta", "gtf", "clinvar_vcf", "hpo_obo", "hpo_genes_to_phenotype", "exon_bed"),
         needs=("gnomad_parts", "child_exonic_calls", "consequence_fixed"),
         provides={"spikein_trials": "."},
         rules=("RANKING_RULE_v3.md", "RANKING_RULE_v4.md"),
         scripts=(SPIKEIN_DIR + "/run_spikein.py", SPIKEIN_DIR + "/spikelib.py", SPIKEIN_DIR + "/calls_param.py",
                  SPIKEIN_DIR + "/consequence_param.py"),
         needs_input_match=("clinvar_vcf",),
         execute=spk_trials_run, parse=spk_trials_parse, privacy="patient",
         note="Deterministic given the pinned ClinVar release: the trial draws use fixed seeds (stratum A 101 and "
              "102, A-BUB 103, C1 301, C2-CH 302, D 401 and 402, E 501 and 502) over pools built from "
              "clinvar.vcf.gz, so a different ClinVar release changes the pools and therefore the trials. The step "
              "links the shipped frozen pre-registration in as the file the script hashes, so prereg_sha256 checks "
              "that preregistration/frozen/PRE_REG_SPIKEIN_EPCR.md is the file the run recorded. The child's VCF is "
              "read only to mask the two candidate rows out of the background and to hash it before and after; "
              "child_vcf_unchanged reports that hash comparison. trials.tsv and alleles.tsv stay in the workdir: "
              "they are 0.6 MB of per-trial rows and are not shipped."),
    Step("PRE-REG-SPIKEIN", "Spike-in strata, the EPCR vector and the pre-registered decisions D1 to D7",
         "PRE-REG-SPIKEIN-EPCR", "T1", "quick", ram_gb=2, disk_gb=0.05,
         inputs=("gtf", "clinvar_vcf", "hpo_obo", "hpo_genes_to_phenotype"),
         needs=("spikein_trials", "consequence_fixed"),
         scripts=(SPIKEIN_DIR + "/analyze.py", SPIKEIN_DIR + "/spikelib.py"),
         needs_input_match=("clinvar_vcf",),
         execute=spk_analyze_run, parse=spk_analyze_parse, privacy="patient",
         note="Sections 7 to 9 of the pre-registration applied to the trial table: per-stratum recalls with Jeffreys "
              "intervals, the McNemar comparison of v4 against v3, the EPCR vector (smoothing, isotonic regression "
              "and the tie-break that makes it strictly decreasing) and the seven pre-registered decisions. The "
              "bootstrap of the expected score uses seed 1. This is the step that produces the epcr column of the "
              "submitted CSV."),
]

# Measured on the analysis machine by this harness (quick tier, 2026-10-20): wall seconds, peak resident memory GB.
# The RAM budget the guard enforces is 1.5 x the measured peak (at least 0.5 GB).
MEASURED = {
    "BLIND-01A": (68.8, 0.14), "BLIND-01C": (0.1, 0.07), "CONSEQ-V1": (3.4, 0.19), "C-FIX-01": (3.0, 0.19),
    "C-FIX-01-FU": (0.1, 0.08), "RANK-V1": (0.1, 0.08), "RANK-V2": (0.1, 0.08), "RANK-V3": (5.1, 0.08),
    "RANK-V4": (0.3, 0.08), "RANK-V4B": (0.3, 0.08), "RANK-V1F": (0.1, 0.08), "RANK-V2F": (0.1, 0.08),
    "RANK-V3F": (5.1, 0.08), "RANK-V4F": (0.3, 0.08), "C-FIX-02": (3.8, 0.17), "T1-CANDIDATE": (1.9, 0.1),
    "READCHECK": (0.1, 0.1), "P1": (3.8, 0.1), "P2": (1.4, 0.1), "P3": (1.3, 0.1), "T2-DEPMAP-01": (3.6, 0.48),
    "T2-P4": (2.0, 1.44), "PRE-REG-B": (10.3, 1.68), "T2-POWER-01": (0.4, 0.1), "M-EVO2-CAL-01-CONTROLS": (11.8, 0.13),
    "M-EVO2-CAL-01": (0.7, 0.1), "M-PROT-CAL-02-BUILD": (1.4, 0.1), "M-PROT-CAL-02": (0.3, 0.1),
    "S0.1": (0.1, 0.02), "H01": (0.1, 0.04), "H-BATCH": (12.4, 0.42), "H08": (62.5, 0.04), "DETECT-LIMIT": (208.9, 0.04),
    "CNV-V1": (135.7, 0.04),
    "PRE-REG-SPIKEIN-G1": (8.5, 0.19), "PRE-REG-SPIKEIN-TRIALS": (30.5, 1.93), "PRE-REG-SPIKEIN": (2.0, 0.15),
}
for _s in STEPS:
    if _s.id in MEASURED:
        _wall, _rss = MEASURED[_s.id]
        _s.ram_gb = max(0.5, math.ceil(_rss * 1.5 * 2) / 2)
        _s.runtime = f"measured: {_wall} s wall, peak RSS {_rss} GB (analysis machine, 2026-10-20)"

BY_ID = {s.id: s for s in STEPS}
PROVIDER = {k: s.id for s in STEPS for k in s.provides}

# How to obtain each output of a full-tier step when it is missing. None of the child-derived ones is in this
# repository (data terms); the authors can hand them to the organisers if the organisers approve.
ROUTES = {
    "gnomad_parts": "regenerate with BLIND-01B (network: byte ranges of the public gnomAD v4.1 exome files; about "
                    "3.5 h; --tier full with allow_network true), or, if the organisers approve, ask the authors for "
                    "their copy (child-derived, not in this repository) and give it under 'intermediates'",
    "evo2_control_scores": "regenerate with M-EVO2-CAL-01-SCORE (GPU, 16 GB VRAM, Evo 2 7B weights), or use the "
                           "public-derived copy shipped in the repository folder 'intermediates' (ClinVar controls only)",
    "protein_scores": "regenerate with M-PROT-CAL-02-SCORE (GPU; it needs the candidate, so BLIND-01B first), or, if "
                      "the organisers approve, ask the authors for their copy (it holds the candidate's row; not in "
                      "this repository) and give it under 'intermediates'",
}


def root_missing(key, have):
    """The full-tier outputs that artifact `key` depends on and that are not in `have` (key -> path)."""
    if key in have:
        return set()
    step = BY_ID[PROVIDER[key]]
    if step.tier == "full" or not step.needs:
        return {key}
    return set().union(*(root_missing(k, have) for k in step.needs)) or {key}


def route(key):
    return ROUTES.get(key, f"run {PROVIDER[key]}" if key in PROVIDER else "not produced by any step")
