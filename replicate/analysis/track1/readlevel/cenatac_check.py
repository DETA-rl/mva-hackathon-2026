"""PRE-REG-2026-10-20-C: CENATAC canonical transcript mapping and exact-allele check (local only)."""
import gzip
import sys

import pysam

GTF = __import__("os").environ["REPL_GTF"]
FA = __import__("os").environ["REPL_FASTA"]
VCF = __import__("os").environ["REPL_VCF"]
BAM = __import__("os").environ["REPL_BAM"]
COMP = {"A": "T", "C": "G", "G": "C", "T": "A", "N": "N"}

tx = {}
with gzip.open(GTF, "rt") as f:
    for line in f:
        if line[0] == "#":
            continue
        c = line.rstrip("\n").split("\t", 8)
        if c[2] not in ("exon", "CDS"):
            continue
        at = c[8]
        if 'gene_name "CENATAC"' not in at or 'transcript_type "protein_coding"' not in at:
            continue
        if 'tag "Ensembl_canonical"' not in at:
            continue
        tid = at.split('transcript_id "')[1].split('"')[0]
        t = tx.setdefault(tid, {"chrom": c[0].replace("chr", ""), "strand": c[6], "exons": [], "cds": []})
        (t["exons"] if c[2] == "exon" else t["cds"]).append((int(c[3]), int(c[4])))
assert len(tx) == 1, tx.keys()
tid, t = next(iter(tx.items()))
print("transcript", tid, "strand", t["strand"], "CDS segments", len(t["cds"]), "exons", len(t["exons"]))

fa = pysam.FastaFile(FA)
ch = "chr" + t["chrom"]

# CDS in transcript orientation: list of (genomic_pos_1based) in order, with bases
cds_positions = []
for s, e in sorted(t["cds"]):
    cds_positions.extend(range(s, e + 1))
if t["strand"] == "-":
    cds_positions = cds_positions[::-1]

def c_to_genomic(n):
    """n is 1-based CDS position (c.N)."""
    return cds_positions[n - 1]

def tx_base(genomic):
    b = fa.fetch(ch, genomic - 1, genomic).upper()
    return b if t["strand"] == "+" else COMP.get(b, "N")

p803 = c_to_genomic(803)
p805 = c_to_genomic(805)
print(f"c.803 genomic {ch}:{p803} reference (transcript orientation) = {tx_base(p803)} (expected A)")
print(f"c.805 genomic {ch}:{p805} reference = {tx_base(p805)}")

# Intronic bases after c.805 in transcript orientation: step outward from the exon end
def step(pos, k):
    return pos + k if t["strand"] == "+" else pos - k

del_start = step(p805, 2)
del_end = step(p805, 19)
print(f"deletion c.805+2_805+19 genomic span (transcript orientation): {ch}:{min(del_start,del_end)}-{max(del_start,del_end)}")
print("is c.805 the last base of its exon?", any(
    (t["strand"] == "+" and e == p805) or (t["strand"] == "-" and s == p805) for s, e in t["exons"]))

# Evidence in VCF at c.803
vcf = pysam.VariantFile(VCF)
for rec in vcf.fetch(t["chrom"], p803 - 1, p803):
    print("VCF at c.803 position:", rec.pos, rec.ref, rec.alts, rec.samples[0].get("GT"))

# Alt-read count at c.803 from BAM
bam = pysam.AlignmentFile(BAM, "rb")
bchrom = ("chr" + t["chrom"]) if ("chr" + t["chrom"]) in bam.references else t["chrom"]
alt_base_tx = "G" if False else None
counts = {}
for col in bam.pileup(bchrom, p803 - 1, p803, truncate=True, min_mapping_quality=30, min_base_quality=20, stepper="samtools"):
    if col.reference_pos != p803 - 1:
        continue
    for pr in col.pileups:
        if pr.is_del or pr.is_refskip:
            continue
        b = pr.alignment.query_sequence[pr.query_position]
        counts[b] = counts.get(b, 0) + 1
print("BAM bases at c.803 genomic position (genome orientation, MAPQ>=30, BQ>=20):", counts)

# Split reads across the deletion span (any alignment with a gap of 18 bp spanning the junction)
span_lo, span_hi = min(del_start, del_end), max(del_start, del_end)
split = 0
for r in bam.fetch(bchrom, span_lo - 150, span_hi + 150):
    if r.is_unmapped or r.is_secondary or r.is_supplementary or r.mapping_quality < 30:
        continue
    if not r.cigartuples:
        continue
    pos = r.reference_start
    for op, ln in r.cigartuples:
        if op in (0, 2, 3, 7, 8):
            if op == 2 and pos < span_hi and pos + ln > span_lo and ln >= 15:
                split += 1
                break
            pos += ln
        else:
            pass
print("reads with a >=15 bp deletion in the CENATAC junction window (MAPQ>=30):", split)
