# H01: excess of ~11 bp insertion / junction signal in CEP57 exons vs background. Read-only. Run on box with ~/.venv-hackaton-h01/bin/python.
import pysam, collections
bam = __import__("os").environ["REPL_BAM"]
def scan(chrom, start, end):
    tot = ins11 = clip11 = 0
    with pysam.AlignmentFile(bam, "rb") as f:
        for r in f.fetch(chrom, start, end):
            if r.is_unmapped or r.is_secondary or r.is_supplementary or r.is_duplicate or r.mapping_quality < 20:
                continue
            tot += 1
            if any(op == 1 and 9 <= ln <= 13 for op, ln in (r.cigartuples or [])):
                ins11 += 1; continue
            cig = r.cigartuples or []
            if cig and ((cig[0][0] == 4 and 9 <= cig[0][1] <= 13) or (cig[-1][0] == 4 and 9 <= cig[-1][1] <= 13)):
                clip11 += 1
    return tot, ins11, clip11
for name, (c, s, e) in {"CEP57": ("chr11", 95790000, 95833000), "background": ("chr11", 60000000, 60043000)}.items():
    t, i, k = scan(c, s, e)
    print(name, "reads", t, "ins9-13", i, "softclip9-13", k, "per1000", round(1000 * (i + k) / max(t, 1), 3))
