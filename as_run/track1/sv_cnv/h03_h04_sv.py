# H03 (BUB1B SV/MEI at locus) and H04 (SV hitting ClinGen haploinsufficiency or triplosensitivity genes). Read-only on inputs; derived outputs to project folder.
import gzip, os, re, collections
P = os.path.expanduser("~/Documents/HACKATON/_private/sv_manta/")
VCF = P + "run/results/variants/diploidSV.vcf.gz"
CG = P + "ClinGen_gene_curation_list_GRCh38.tsv"
GTF = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/gencode.v44.basic.annotation.gtf.gz")
# gene spans (protein coding and all) from GENCODE
spans = {}
with gzip.open(GTF, "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.split("\t", 8)
        if c[2] != "gene": continue
        g = re.search('gene_name "([^"]+)"', c[8]).group(1)
        spans[g] = (c[0].replace("chr", ""), int(c[3]), int(c[4]))
# ClinGen scores
hi, ts = {}, {}
for line in open(CG):
    if line.startswith("#") or line.startswith("Gene Symbol"): continue
    x = line.rstrip("\n").split("\t")
    if len(x) < 13: continue
    if x[4].strip() in ("3", "3.0"): hi[x[0]] = 3
    if x[12].strip() in ("3", "3.0"): ts[x[0]] = 3
svs = []
with gzip.open(VCF, "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.rstrip("\n").split("\t")
        info = dict(kv.split("=", 1) if "=" in kv else (kv, "") for kv in c[7].split(";"))
        chrom, pos = c[0].replace("chr", ""), int(c[1])
        svtype = info.get("SVTYPE", "")
        end = int(info.get("END", pos)) if "END" in info else pos
        if svtype == "BND":
            end = pos
        gt = c[9].split(":")[0]
        svlen = int(info.get("SVLEN", 0)) if info.get("SVLEN", "0").lstrip("-").isdigit() else 0
        svs.append((chrom, pos, end, svtype, gt, svlen, c[6]))
print("SV records:", len(svs))
def overlap(ch, s, e, sv):
    return sv[0] == ch and not (sv[2] < s or sv[1] > e)
# H03: BUB1B locus (gene +/- 50 kb) and its intron
ch, gs, ge = spans["BUB1B"]
loc = [sv for sv in svs if overlap(ch, gs - 50000, ge + 50000, sv)]
print(f"H03 BUB1B gene +/-50 kb: {len(loc)} SV calls")
for sv in loc: print("   ", sv)
# H04: SVs (any type) overlapping ClinGen HI=3 or TS=3 gene spans, counted per gene
hits = collections.defaultdict(list)
for g in set(hi) | set(ts):
    if g not in spans: continue
    ch, s, e = spans[g]
    for sv in svs:
        if overlap(ch, s, e, sv):
            hits[g].append(sv)
print("H04 genes with HI3 or TS3 overlapping an SV call:", len(hits))
for g in sorted(hits, key=lambda g: -len(hits[g]))[:40]:
    types = collections.Counter(sv[3] for sv in hits[g])
    tag = ("HI3" if g in hi else "") + (" TS3" if g in ts else "")
    print(f"  {g:12s} {tag:7s} n={len(hits[g])} {dict(types)} gts={dict(collections.Counter(sv[4] for sv in hits[g]))}")
