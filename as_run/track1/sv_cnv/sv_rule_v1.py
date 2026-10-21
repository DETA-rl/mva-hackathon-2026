# SV rule v1 (see SV_RULE_v1.md). Reads Manta output and ClinGen list on the box; writes a derived summary.
import gzip, os, re, collections
P = os.path.expanduser("~/Documents/HACKATON/_private/sv_manta/")
VCF = P + "run/results/variants/diploidSV.vcf.gz"
CG = P + "ClinGen_gene_curation_list_GRCh38.tsv"
GTF = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/gencode.v44.basic.annotation.gtf.gz")
OUT = P + "sv_rule_v1_summary.tsv"
spans = {}
with gzip.open(GTF, "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.split("\t", 8)
        if c[2] != "gene": continue
        g = re.search('gene_name "([^"]+)"', c[8]).group(1)
        spans[g] = (c[0].replace("chr", ""), int(c[3]), int(c[4]))
hi, ts = set(), set()
for line in open(CG):
    if line.startswith("#") or line.startswith("Gene Symbol"): continue
    x = line.rstrip("\n").split("\t")
    if len(x) < 13: continue
    if x[4].strip() in ("3", "3.0"): hi.add(x[0])
    if x[12].strip() in ("3", "3.0"): ts.add(x[0])
dos = {g: spans[g] for g in (hi | ts) if g in spans}
calls = []
with gzip.open(VCF, "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.rstrip("\n").split("\t")
        if c[6] != "PASS": continue
        info = dict(kv.split("=", 1) if "=" in kv else (kv, "") for kv in c[7].split(";"))
        svt = info.get("SVTYPE", "")
        if svt not in ("DEL", "DUP", "INS", "BND"): continue
        svlen = abs(int(info.get("SVLEN", "0") or 0)) if info.get("SVLEN", "0").lstrip("-").isdigit() else 0
        if svt != "BND" and svlen < 50: continue
        fmt = c[8].split(":"); smp = c[9].split(":")
        d = dict(zip(fmt, smp))
        gt = d.get("GT", "")
        try:
            pr = int(d.get("PR", "0,0").split(",")[1]); sr = int(d.get("SR", "0,0").split(",")[1])
        except (ValueError, IndexError):
            continue
        if pr + sr < 4: continue
        calls.append((c[0].replace("chr", ""), int(c[1]), int(info.get("END", c[1])), svt, gt, svlen, pr + sr))
print("SV calls passing rule filters 1-3:", len(calls))
def hit(g, sv):
    ch, s, e = dos[g]
    return sv[0] == ch and not (sv[2] < s or sv[1] > e)
genes = collections.defaultdict(list)
for g in dos:
    for sv in calls:
        if hit(g, sv): genes[g].append(sv)
rank = sorted(genes, key=lambda g: (-len(genes[g]), g))
print("dosage-sensitive genes hit (rule filters 1-4):", len(rank))
for g in rank[:30]:
    tag = ("HI3" if g in hi else "") + (" TS3" if g in ts else "")
    print(f"  {g:12s} {tag:7s} n={len(genes[g])} types={dict(collections.Counter(sv[3] for sv in genes[g]))} gts={dict(collections.Counter(sv[4] for sv in genes[g]))}")
with open(OUT, "w") as fh:
    fh.write("gene\ttag\tcalls\ttypes\tgts\n")
    for g in rank:
        tag = ("HI3" if g in hi else "") + (" TS3" if g in ts else "")
        fh.write(f"{g}\t{tag}\t{len(genes[g])}\t{dict(collections.Counter(sv[3] for sv in genes[g]))}\t{dict(collections.Counter(sv[4] for sv in genes[g]))}\n")
# H03: BUB1B +/-50 kb under the same filters
ch, s, e = spans["BUB1B"]
bub = [sv for sv in calls if sv[0] == ch and not (sv[2] < s - 50000 or sv[1] > e + 50000)]
print("H03 BUB1B +/-50 kb under rule filters:", len(bub), bub)
