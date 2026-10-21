"""Validate consequence.py (original and fixed) against ClinVar's own molecular-consequence (MC) annotation.
Public data only: ClinVar SNVs in canonical GENCODE v44 protein-coding transcripts. No child coordinates leave the box.
Compares the classify() output from each version with the MC term, split by transcript strand.
Usage: validate_consequence.py <consequence.py> <consequence_fixed.py> <clinvar.vcf.gz>
"""
import collections
import gzip
import sys

SRC_OLD, SRC_FIXED, CLINVAR = sys.argv[1], sys.argv[2], sys.argv[3]


def load_ns(path):
    text = open(path).read().split("\nrows = []")[0]  # tables and classify() only, not the child loop
    ns = {"__name__": "x"}
    exec(compile(text, path, "exec"), ns)
    return ns


old = load_ns(SRC_OLD)
fixed = load_ns(SRC_FIXED)
gene_tid = {}
for tid, t in old["tx"].items():
    gene_tid.setdefault(t["gene"], tid)

tally = collections.Counter()
checked = 0
with gzip.open(CLINVAR, "rt") as fh:
    for line in fh:
        if line[0] == "#":
            continue
        c = line.rstrip("\n").split("\t")
        chrom, pos, ref, alt, info = c[0], int(c[1]), c[3], c[4], c[7]
        if len(ref) != 1 or len(alt) != 1:
            continue
        d = dict(kv.split("=", 1) for kv in info.split(";") if "=" in kv)
        mc = d.get("MC", "").split("|")[-1] if "MC" in d else ""
        if mc not in ("missense_variant", "nonsense", "synonymous_variant"):
            continue
        gene = d.get("GENEINFO", "").split("|")[0].split(":")[0]
        tid = gene_tid.get(gene)
        if tid is None:
            continue
        strand = old["tx"][tid]["strand"]
        ch = chrom.replace("chr", "")
        if old["tx"][tid]["chrom"] != ch:
            continue
        o = old["classify"](tid, pos, ref, alt)
        f = fixed["classify"](tid, pos, ref, alt)
        mc_norm = {"missense_variant": "missense", "nonsense": "nonsense", "synonymous_variant": "synonymous"}[mc]
        checked += 1
        tally[(strand, "orig_match" if o == mc_norm else "orig_miss")] += 1
        tally[(strand, "fixed_match" if f == mc_norm else "fixed_miss")] += 1
        if checked >= 6000:
            break

print("ClinVar SNVs checked (canonical transcript, same chromosome):", checked)
for strand in ["+", "-"]:
    om, fm = tally[(strand, "orig_match")], tally[(strand, "fixed_match")]
    ot, ft = om + tally[(strand, "orig_miss")], fm + tally[(strand, "fixed_miss")]
    print(f"strand {strand}: original {om}/{ot} = {om / max(ot, 1):.3f}; fixed {fm}/{ft} = {fm / max(ft, 1):.3f}")
