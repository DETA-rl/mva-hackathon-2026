# Ranking rule v3 (hierarchical). See RANKING_RULE_v3.md. Reads box-side tables; writes a derived summary to the project folder.
import collections, gzip, os, random, re
D = os.environ["REPL_OUT"] + "/"
seen = {}
for l in open(D + "child_exonic_consequence.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] == "chrom": continue
    seen.setdefault((f[0], f[1], f[2], f[3]), f)
CAND = {"nonsense", "frameshift", "stop_lost", "missense", "inframe_indel", "splice_region"}
W = {"nonsense": 3, "frameshift": 3, "stop_lost": 2, "splice_region": 2, "inframe_indel": 2, "missense": 1}
PARA = re.compile(r"^(HLA-|TAS2R|MUC|LILRA|LILRB|OR\d|ZNF|PRDM9|NBPF|SERPINA)")
PAR = [(10001, 2781479), (155701383, 156030895)]
def in_par(p): return any(a <= p <= b for a, b in PAR)
def hom(f): return f[4] in ("1/1", "1|1")
cands = [f for f in seen.values() if f[12] in CAND and f[9] in ("rare", "unobserved")]
cands = [f for f in cands if not (f[0] == "X" and not in_par(int(f[1])) and not hom(f))]
bg = collections.defaultdict(list)
for f in cands: bg[f[11]].append(f)
clustered = set()
for g, calls in bg.items():
    ps = sorted(int(c[1]) for c in calls)
    for p in ps:
        w = [c for c in calls if p <= int(c[1]) <= p + 1000]
        if len(w) >= 5 and all(hom(c) for c in w): clustered.add(g); break
cands = [f for f in cands if f[11] not in clustered and not PARA.match(f[11])]
# ClinVar match on exact chrom, pos, ref, alt (any alt in the record)
keys = {(f[0], f[1], f[2], f[3]) for f in cands}
clin = {}
for l in gzip.open(D + "clinvar.vcf.gz", "rt"):
    if l[0] == "#": continue
    c = l.split("\t", 8)
    ch = c[0].replace("chr", "")
    alts = c[4].split(",")
    if not any((ch, c[1], c[3], a) in keys for a in alts): continue
    sig = c[7].split("CLNSIG=")[1].split(";")[0] if "CLNSIG=" in c[7] else "NA"
    for a in alts:
        if (ch, c[1], c[3], a) in keys: clin[(ch, c[1], c[3], a)] = sig
def is_plp(sig): return sig in ("Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic")
genes = collections.defaultdict(list)
for f in cands: genes[f[11]].append(f)
def v2score(calls): return sum(W[c[12]] * (1.5 if hom(c) else 1) for c in calls)
tierA = {g for g, calls in genes.items() if any(is_plp(clin.get((c[0], c[1], c[2], c[3]), "")) for c in calls)}
def compound(calls):
    lof = any(c[12] in ("nonsense", "frameshift", "splice_region") for c in calls)
    mis = any(c[12] == "missense" for c in calls)
    return lof and mis and len(calls) >= 2
tierB = {g for g, calls in genes.items() if g not in tierA and compound(calls)}
tierC = {g for g, calls in genes.items() if g not in tierA | tierB and (v2score(calls) >= 3 or any(hom(c) for c in calls))}
def order(tiered_A, tiered_B, tiered_C, gene_calls):
    def key(g):
        t = 0 if g in tiered_A else (1 if g in tiered_B else 2)
        return (t, -v2score(gene_calls[g]), g)
    return sorted(tiered_A | tiered_B | tiered_C, key=key)
rankV3 = order(tierA, tierB, tierC, genes)
rankA0 = sorted({g for g, c in genes.items() if v2score(c) >= 3 or any(hom(x) for x in c)}, key=lambda g: (-v2score(genes[g]), g))
print("candidate calls after filters:", len(cands), "| ClinVar P/LP matched calls:", sum(1 for f in cands if is_plp(clin.get((f[0], f[1], f[2], f[3]), ""))))
print("tier A (ClinVar P/LP):", sorted(tierA), flush=True)
print("tier B (compound pattern, not A):", len(tierB), flush=True)
print("v3 rank top 15:")
for i, g in enumerate(rankV3[:15], 1):
    t = "A" if g in tierA else ("B" if g in tierB else "C")
    print(f"  {i:2d} {g:14s} tier={t} v2score={v2score(genes[g]):.1f} calls={len(genes[g])}")
print("BUB1B rank v3:", rankV3.index("BUB1B") + 1 if "BUB1B" in rankV3 else "not ranked", "| A0 (v2 only):", rankA0.index("BUB1B") + 1 if "BUB1B" in rankA0 else "not ranked")
# shuffled baseline: permute ClinVar labels across calls
rng = random.Random(1)
cl_items = list(clin.items()); vals = [v for _, v in cl_items]; rng.shuffle(vals)
clin_sh = {k: v for (k, _), v in zip(cl_items, vals)}
tierA_sh = {g for g, calls in genes.items() if any(is_plp(clin_sh.get((c[0], c[1], c[2], c[3]), "")) for c in calls)}
rankSh = order(tierA_sh, tierB, tierC, genes)
print("shuffled-ClinVar baseline: tier A genes", sorted(tierA_sh), "| BUB1B rank", rankSh.index("BUB1B") + 1 if "BUB1B" in rankSh else "not ranked")
out = D + "ranking_v3_summary.tsv"
with open(out, "w") as fh:
    fh.write("gene\ttier\tv2score\tcalls\trank_v3\n")
    for i, g in enumerate(rankV3, 1):
        t = "A" if g in tierA else ("B" if g in tierB else "C")
        fh.write(f"{g}\t{t}\t{v2score(genes[g])}\t{len(genes[g])}\t{i}\n")
print("summary written:", out)
