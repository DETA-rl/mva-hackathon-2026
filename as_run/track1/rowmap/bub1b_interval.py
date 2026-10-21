# Read-only listing of child VCF calls in the BUB1B gene interval (GENCODE v44), with distance to the nearest
# protein-coding exon/CDS of BUB1B. Prints to stdout only (box). No writes to inputs.
import gzip, os, pysam
D = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/")
VCF = os.path.expanduser("~/Documents/HACKATON/data/WGS_EX2312012_HGWCNDSX7.vcf.gz")
gene = None; exons = []; cds = []
for line in gzip.open(D + "gencode.v44.basic.annotation.gtf.gz", "rt"):
    if line[0] == "#": continue
    c = line.split("\t", 8)
    if "gene_name \"BUB1B\";" not in c[8]: continue
    if c[2] == "gene": gene = (c[0], int(c[3]), int(c[4]), c[6])
    if "transcript_type \"protein_coding\"" in c[8]:
        if c[2] == "exon": exons.append((int(c[3]), int(c[4])))
        if c[2] == "CDS": cds.append((int(c[3]), int(c[4])))
print("gene", gene, "n_exon_feats", len(exons), "n_cds_feats", len(cds))
def dist(p, feats):
    return min(0 if a <= p <= b else min(abs(p - a), abs(p - b)) for a, b in feats)
vf = pysam.VariantFile(VCF)
ch = gene[0].replace("chr", "") if gene[0].replace("chr", "") in vf.header.contigs else gene[0]
for rec in vf.fetch(ch, gene[1] - 1, gene[2]):
    s = rec.samples[0]
    gt = "/".join("." if a is None else str(a) for a in s["GT"])
    print(rec.pos, rec.ref, ",".join(rec.alts or ()), "FILTER", ";".join(rec.filter.keys()) or ".", "GT", gt,
          "len_ref", len(rec.ref), "d_exon", dist(rec.pos, exons), "d_cds", dist(rec.pos, cds))
