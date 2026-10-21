# Child non-reference calls inside protein-coding exons (+/-3 bp). Derived table written to the project folder.
import gzip, bisect, collections
VCF = __import__("os").environ["REPL_VCF"]
D = __import__("os").environ["REPL_OUT"] + "/"
by = collections.defaultdict(list)
for line in open(D + "protein_coding_exons_hg38.bed"):
    c, s, e, g = line.rstrip("\n").split("\t")
    by[c].append((int(s) - 3, int(e) + 3, g))
idx = {}
for c, v in by.items():
    v.sort()
    idx[c] = ([a for a, _, _ in v], v)
out = open(D + "child_exonic_calls.tsv", "w")
out.write("chrom\tpos\tref\talt\tgt\tfilter\tgenes\n")
n = 0
with gzip.open(VCF, "rt") as fh:
    for line in fh:
        if line[0] == "#":
            continue
        c = line.rstrip("\n").split("\t")
        chrom, pos = c[0], int(c[1])
        if chrom not in idx:
            continue
        sample = c[9].split(":")
        gt = dict(zip(c[8].split(":"), sample)).get("GT", "")
        if gt in ("0/0", "0|0", "./.", ""):
            continue
        starts, v = idx[chrom]
        i = bisect.bisect_right(starts, pos)
        genes = set()
        for j in range(max(0, i - 200), i):
            s, e, g = v[j]
            if s <= pos <= e:
                genes.add(g)
        if not genes:
            continue
        out.write(f"{chrom}\t{pos}\t{c[3]}\t{c[4].split(',')[0]}\t{gt}\t{c[6]}\t{','.join(sorted(genes))}\n")
        n += 1
out.close()
print("child exonic non-reference calls:", n)
