"""Build a public ClinVar missense control set (GRCh38) for BUB1B + 20 unrelated genes.

Inputs (on the box, under controls/):
  variant_summary.txt.gz  - ClinVar tab-delimited summary (NCBI FTP)
  <GENE>.fasta            - UniProt reviewed canonical sequence, gene-name query only
Output:
  controls.tsv            - gene, pos, ref, alt, label (1=P/LP, 0=B/LB), chrom, vcf_pos, vcf_ref, vcf_alt
"""
import csv
import gzip
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

CTRL = Path(sys.argv[1])
MAX_PER_CLASS = 40
GENES = ["BUB1B", "BRCA1", "TP53", "PTEN", "MLH1", "MSH2", "ATM", "CHEK2", "RB1", "APC",
         "NF1", "SCN5A", "KCNQ1", "LDLR", "MYH7", "PAH", "CFTR", "F8", "PALB2", "BRCA2", "GJB2"]
assert len(GENES) == 21  # BUB1B + 20 others

THREE = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E",
         "Gly": "G", "His": "H", "Ile": "I", "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F",
         "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"}
PCHG = re.compile(r"\(p\.([A-Za-z]{3})(\d+)([A-Za-z]{3})\)")


def read_fasta(path):
    seq = "".join(l.strip() for l in open(path) if not l.startswith(">"))
    return seq


seqs = {g: read_fasta(CTRL / f"{g}.fasta") for g in GENES}
for g in GENES:
    assert len(seqs[g]) > 0, g

rows = defaultdict(lambda: {"P": {}, "B": {}})
with gzip.open(CTRL / "variant_summary.txt.gz", "rt") as fh:
    reader = csv.DictReader(fh, delimiter="\t")
    for r in reader:
        if r["Assembly"] != "GRCh38" or r["Type"] != "single nucleotide variant":
            continue
        g = r["GeneSymbol"]
        if g not in seqs:
            continue
        m = PCHG.search(r["Name"])
        if not m:
            continue
        ref3, pos, alt3 = m.groups()
        if ref3 not in THREE or alt3 not in THREE:  # drops Ter, synonymous, indels
            continue
        pos = int(pos)
        ref, alt = THREE[ref3], THREE[alt3]
        if ref == alt:
            continue
        # isoform check: ClinVar numbering must match UniProt canonical residue
        if pos - 1 >= len(seqs[g]) or seqs[g][pos - 1] != ref:
            continue
        sig = r["ClinSigSimple"]
        if sig == "1":
            cls = "P"
        elif sig == "0":
            cls = "B"
        else:
            continue
        if "no assertion" in r["ReviewStatus"]:
            continue
        key = (pos, alt)
        rec = dict(gene=g, pos=pos, ref=ref, alt=alt, chrom=r["Chromosome"],
                   vcf_pos=r["PositionVCF"], vcf_ref=r["ReferenceAlleleVCF"],
                   vcf_alt=r["AlternateAlleleVCF"], review=r["ReviewStatus"])
        rows[g][cls].setdefault(key, rec)

random.seed(20260919)
out = []
for g in GENES:
    for cls, lab in (("P", 1), ("B", 0)):
        pool = list(rows[g][cls].values())
        random.shuffle(pool)
        for rec in pool[:MAX_PER_CLASS]:
            rec["label"] = lab
            out.append(rec)

cols = ["gene", "pos", "ref", "alt", "label", "chrom", "vcf_pos", "vcf_ref", "vcf_alt", "review"]
with open(CTRL / "controls.tsv", "w") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
    w.writeheader()
    w.writerows(out)

n_p = sum(r["label"] for r in out)
print(f"controls total={len(out)} pathogenic={n_p} benign={len(out) - n_p}")
for g in GENES:
    print(g, "P_avail", len(rows[g]["P"]), "B_avail", len(rows[g]["B"]))
print("BUB1B seq[1001] =", seqs["BUB1B"][1001], "len", len(seqs["BUB1B"]))
