"""Build the Track 1 calibration control pool exactly as models/CALIBRATION_RULE.md section 1 states.

Eligibility: SNV; CLNREVSTAT in the four allowed values; CLNSIG exactly P (Pathogenic, Likely_pathogenic)
or B (Benign, Likely_benign); MC contains missense_variant or nonsense/stop_gained; BUB1B excluded.
Selection: per cell (P/B x missense/nonsense) take the 5 genes with most eligible records (ties alphabetical);
per gene take the 10 records with the lowest SHA-256 of VariationID (all if fewer than 10).
Writes controls_rule.tsv (id, label, chrom, pos, ref, alt; label 1 = P, 0 = B) and selection_summary.tsv.
"""
import collections
import gzip
import hashlib
import sys

VCF = sys.argv[1]
OUT_DIR = sys.argv[2]

P_SIG = {"Pathogenic", "Likely_pathogenic"}
B_SIG = {"Benign", "Likely_benign"}
REV_OK = {
    "criteria_provided,_single_submitter",
    "criteria_provided,_multiple_submitters,_no_conflicts",
    "reviewed_by_expert_panel",
    "practice_guideline",
}

cells = collections.defaultdict(list)
with gzip.open(VCF, "rt") as fh:
    for line in fh:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        chrom, pos, vid, ref, alt, info = c[0], c[1], c[2], c[3], c[4], c[7]
        if len(ref) != 1 or len(alt) != 1:
            continue
        d = dict(kv.split("=", 1) for kv in info.split(";") if "=" in kv)
        if d.get("CLNVC") != "single_nucleotide_variant":
            continue
        if d.get("CLNREVSTAT") not in REV_OK:
            continue
        sig = d.get("CLNSIG", "")
        if sig in P_SIG:
            cls = "P"
        elif sig in B_SIG:
            cls = "B"
        else:
            continue
        mc = d.get("MC", "")
        if "missense_variant" in mc:
            csq = "missense"
        elif "nonsense" in mc or "stop_gained" in mc:
            csq = "nonsense"
        else:
            continue
        gene = d.get("GENEINFO", "").split("|")[0].split(":")[0]
        if not gene or gene == "BUB1B":
            continue
        cells[(cls, csq)].append({
            "gene": gene, "vid": vid,
            "chrom": chrom if chrom.startswith("chr") else "chr" + chrom,
            "pos": pos, "ref": ref, "alt": alt,
        })

rows, summary = [], []
for cls in ["P", "B"]:
    for csq in ["missense", "nonsense"]:
        recs = cells[(cls, csq)]
        cnt = collections.Counter(r["gene"] for r in recs)
        genes = sorted(cnt, key=lambda g: (-cnt[g], g))[:5]
        summary.append((cls, csq, len(recs), ";".join(genes)))
        for g in genes:
            rs = [r for r in recs if r["gene"] == g]
            rs.sort(key=lambda r: hashlib.sha256(r["vid"].encode()).hexdigest())
            for r in rs[:10]:
                rows.append((f"{g}_{r['vid']}", 1 if cls == "P" else 0,
                             r["chrom"], r["pos"], r["ref"], r["alt"], csq, cls))

with open(f"{OUT_DIR}/controls_rule.tsv", "w") as out:
    out.write("id\tlabel\tchrom\tpos\tref\talt\tcsq\tclass\n")
    for r in rows:
        out.write("\t".join(str(x) for x in r) + "\n")
with open(f"{OUT_DIR}/selection_summary.tsv", "w") as out:
    out.write("class\tconsequence\teligible_records\tselected_genes\n")
    for s in summary:
        out.write("\t".join(str(x) for x in s) + "\n")
print("controls:", len(rows), "P:", sum(r[1] for r in rows), "B:", sum(1 - r[1] for r in rows))
for s in summary:
    print(s)
