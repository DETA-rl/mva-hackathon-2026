import csv, glob, subprocess, re
GENES = "RNU4ATAC RNU6ATAC ZRSR2 SNRNP48 ESCO2 PCNT CENPF BUB1B TRIP13 CEP57 SMC5 MAD1L1 CEP192 TRIM37 CDC20 MAD2L1BP CENATAC SLF2".split()
gn = {}
for fn in glob.glob("child_exonic_gnomad_exomes.part*.tsv"):
    for r in csv.DictReader(open(fn), delimiter="\t"):
        gn[(r["chrom"], r["pos"], r["ref"], r["alt"])] = (r["gnomad_status"], r["gnomad_af"], r["gnomad_ac"], r["gnomad_an"])
gtf = {}
import gzip
with gzip.open("gencode.v44.basic.annotation.gtf.gz", "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.split("\t", 8)
        if c[2] != "gene": continue
        g = c[8].split("gene_name \"")[1].split("\"")[0]
        if g in GENES: gtf[g] = (c[0].replace("chr",""), int(c[3]), int(c[4]))
for g in GENES:
    if g not in gtf: print(g, "no coordinates"); continue
    ch, s, e = gtf[g]
    out = subprocess.run(["tabix", __import__("os").environ["REPL_VCF"], f"{ch}:{s}-{e}"], capture_output=True, text=True).stdout
    calls = []
    for l in out.splitlines():
        p = l.split("\t"); gt = p[9].split(":")[0]
        if gt in ("0/0","0|0","./.","."): continue
        calls.append((p[0], p[1], p[3], p[4], gt))
    ann = []
    for c_ in calls:
        k = c_[:4]
        st = gn.get(k)
        ann.append((c_[1], c_[2]+">"+c_[3], c_[4], st[0] if st else "not_in_exonic_table", st[1] if st else "NA", st[2] + "/" + st[3] if st else ""))
    exonic = sum(1 for a in ann if a[3] != "not_in_exonic_table")
    print(f"{g}: {len(calls)} non-ref calls; {exonic} in exonic table")
    for a in ann[:12]: print("   ", a)
