# Consequence of child exonic calls on GENCODE canonical protein-coding transcripts, from the reference FASTA. Read-only inputs, derived output only.
import gzip, bisect, collections, pysam, os
HERE = os.environ["REPL_OUT"] + "/"
FA = os.environ["REPL_FASTA"]
GTF = HERE + "gencode.v44.basic.annotation.gtf.gz"
CODON = {}
bases = "TCAG"; aas = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
i = 0
for a in bases:
    for b in bases:
        for c in bases:
            CODON[a + b + c] = aas[i]; i += 1
COMP = {"A": "T", "C": "G", "G": "C", "T": "A", "N": "N"}
# 1. canonical protein-coding transcripts
tx = {}
with gzip.open(GTF, "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.rstrip("\n").split("\t", 8)
        if c[2] not in ("exon", "CDS"): continue
        at = c[8]
        if 'transcript_type "protein_coding"' not in at or 'tag "Ensembl_canonical"' not in at: continue
        tid = at.split('transcript_id "')[1].split('"')[0]
        gname = at.split('gene_name "')[1].split('"')[0]
        t = tx.setdefault(tid, {"gene": gname, "chrom": c[0].replace("chr", ""), "strand": c[6], "exons": [], "cds": []})
        if c[2] == "exon": t["exons"].append((int(c[3]), int(c[4])))
        else: t["cds"].append((int(c[3]), int(c[4])))
print("canonical protein-coding transcripts:", len(tx), flush=True)
# 2. interval index of canonical exons
ex_idx = collections.defaultdict(list)
for tid, t in tx.items():
    for s, e in t["exons"]:
        ex_idx[t["chrom"]].append((s, e, tid))
starts = {}
for ch in ex_idx:
    ex_idx[ch].sort()
    starts[ch] = [s for s, _, _ in ex_idx[ch]]
fa = pysam.FastaFile(FA)
chr_prefix = "chr" if any(r.startswith("chr") for r in fa.references) else ""
def ref(ch, s, e):
    return fa.fetch(chr_prefix + ch, s - 1, e).upper()
cds_cache = {}
def cds_seq(tid):
    if tid in cds_cache: return cds_cache[tid]
    t = tx[tid]
    segs = sorted(t["cds"])
    if t["strand"] == "-": segs = segs[::-1]
    seq = ""; cum = []
    for s, e in segs:
        cum.append((s, e, len(seq)))
        seq += ref(t["chrom"], s, e)
    if t["strand"] == "-":
        seq = "".join(COMP.get(b, "N") for b in reversed(seq))
        L = len(seq)
        cum = [(s, e, L - off - (e - s + 1)) for s, e, off in cum]
    cds_cache[tid] = (seq, cum)
    return cds_cache[tid]
def cds_offset(tid, pos):
    seq, cum = cds_seq(tid)
    t = tx[tid]
    for s, e, off in cum:
        if s <= pos <= e:
            return off + (pos - s) if t["strand"] == "+" else off + (e - pos)
    return None
def classify(tid, pos, ref_a, alt_a):
    t = tx[tid]
    seq, _ = cds_seq(tid)
    off = cds_offset(tid, pos)
    if off is None:
        in_exon = any(s <= pos <= e for s, e in t["exons"])
        return "UTR_noncoding_exon" if in_exon else "splice_region"
    ref_s = ref_a.upper(); alt_s = alt_a.upper()
    if len(ref_s) == 1 and len(alt_s) == 1:
        if t["strand"] == "-":
            ref_s, alt_s = COMP.get(ref_s, "N"), COMP.get(alt_s, "N")
        codon0 = (off // 3) * 3
        if codon0 + 3 > len(seq): return "unclassified"
        cod = seq[codon0:codon0 + 3]
        k = off - codon0
        mut = cod[:k] + alt_s + cod[k + 1:]
        a0, a1 = CODON.get(cod, "X"), CODON.get(mut, "X")
        if a0 == "*" and a1 != "*": return "stop_lost"
        if a1 == "*" and a0 != "*": return "nonsense"
        if a0 == a1: return "synonymous"
        return "missense"
    diff = len(alt_s) - len(ref_s)
    if diff % 3 != 0: return "frameshift"
    return "inframe_indel"
rows = []
for fn in sorted(__import__("glob").glob(HERE + "child_exonic_gnomad_exomes.part*.tsv")):
    for i, line in enumerate(open(fn)):
        if i == 0: continue
        f = line.rstrip("\n").split("\t")
        rows.append(f)
print("calls:", len(rows), flush=True)
out = open(HERE + "child_exonic_consequence.tsv", "w")
out.write("chrom\tpos\tref\talt\tgt\tfilter\tgene_listed\tgnomad_status\tgnomad_af\tclass\ttranscript\tgene\tconsequence\n")
for f in rows:
    c, p, r, a, gt = f[0], int(f[1]), f[2], f[3], f[4]
    st, af = f[7], f[8]
    if st in ("absent_site", "site_present_alt_absent", "not_in_exome_release") or (st == "found" and (af == "NA" or float(af) == 0.0)):
        cls = "unobserved"
    elif float(af) < 0.001:
        cls = "rare"
    else:
        cls = "common_or_low"
    cand = [tid for tid in []]
    if c in starts:
        hi = bisect.bisect_right(starts[c], p + 2)
        hits = set()
        k = hi - 1
        while k >= 0 and starts[c][k] >= p - 50000:
            s, e, tid = ex_idx[c][k]
            if s - 2 <= p <= e + 2: hits.add(tid)
            k -= 1
        for tid in sorted(hits):
            cons = classify(tid, p, r, a)
            out.write(f"{c}\t{p}\t{r}\t{a}\t{gt}\t{f[5]}\t{f[6]}\t{st}\t{af}\t{cls}\t{tid}\t{tx[tid]['gene']}\t{cons}\n")
out.close()
print("done", flush=True)
