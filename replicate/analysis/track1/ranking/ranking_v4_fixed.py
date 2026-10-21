# Ranking rule v4 (see RANKING_RULE_v4.md). Box-side; derived output only.
import collections, os, random, re
D = os.environ["REPL_OUT"] + "/"
CHILD = ["HP:0000121", "HP:0001508", "HP:0001518", "HP:0001622", "HP:0002859", "HP:0003202", "HP:0004322", "HP:0200067"]
# ontology: parents (is_a) per term
parents = collections.defaultdict(set)
cur = None
for l in open(D + "hp.obo"):
    l = l.rstrip("\n")
    if l == "[Term]": cur = None
    elif l.startswith("id: HP:"): cur = l[4:]
    elif l.startswith("is_a: HP:") and cur: parents[cur].add(l[6:16])
ancestors_cache = {}
def ancestors(t):
    if t in ancestors_cache: return ancestors_cache[t]
    out = {t}; stack = [t]
    while stack:
        x = stack.pop()
        for p in parents.get(x, ()):
            if p not in out: out.add(p); stack.append(p)
    ancestors_cache[t] = out
    return out
# gene -> set of HPO terms
gene_terms = collections.defaultdict(set)
for l in open(D + "genes_to_phenotype.txt"):
    if l.startswith("ncbi_gene_id"): continue
    f = l.rstrip("\n").split("\t")
    if len(f) >= 3: gene_terms[f[1]].add(f[2])
def pheno_score(gene, child=CHILD):
    anc_all = set()
    for t in gene_terms.get(gene, ()): anc_all |= ancestors(t)
    return sum(1 for c in child if c in anc_all)
matched = collections.defaultdict(set)
for gene, terms in gene_terms.items():
    anc_all = set()
    for t in terms: anc_all |= ancestors(t)
    for c in CHILD:
        if c in anc_all: matched[gene].add(c)
# candidate genes from v3 run inputs
cand_genes = set()
for l in open(D + "ranking_v3_summary_fixed.tsv"):
    if l.startswith("gene"): continue
    cand_genes.add(l.split("\t")[0])
tiers = {}
for l in open(D + "ranking_v3_summary_fixed.tsv"):
    if l.startswith("gene"): continue
    g, t, v2, n, r = l.rstrip("\n").split("\t")
    tiers[g] = (t, float(v2))
print("candidate genes (v3):", len(tiers))
ph = {g: len(matched.get(g, set())) for g in tiers}
print("genes with phenotype score >= 1:", sum(1 for g in ph if ph[g] >= 1))
print("BUB1B phenotype score:", ph.get("BUB1B"), "matched terms:", sorted(matched.get("BUB1B", set())))
def order(labels, phs):
    return sorted(labels, key=lambda g: ({"A": 0, "B": 1, "C": 2}[labels[g][0]], -phs.get(g, 0), -labels[g][1], g))
v4 = order(tiers, ph)
p0 = sorted(tiers, key=lambda g: ({"A": 0, "B": 1, "C": 2}[tiers[g][0]], -tiers[g][1], g))
ponly = sorted(tiers, key=lambda g: (-ph.get(g, 0), -tiers[g][1], g))
rng = random.Random(1)
vals = list(ph.values()); rng.shuffle(vals)
ph_sh = dict(zip(tiers.keys(), vals))
shuf = order(tiers, ph_sh)
def rk(lst, g): return lst.index(g) + 1 if g in lst else "NA"
print("BUB1B rank: v4", rk(v4, "BUB1B"), "| P0 (no phenotype)", rk(p0, "BUB1B"), "| P-only", rk(ponly, "BUB1B"), "| shuffled", rk(shuf, "BUB1B"))
print("v4 top 15:")
for i, g in enumerate(v4[:15], 1):
    print(f"  {i:2d} {g:14s} tier={tiers[g][0]} pheno={ph.get(g,0)} v2={tiers[g][1]}")
print("P-only top 10:", ponly[:10])
out = D + "ranking_v4_summary_fixed.tsv"
with open(out, "w") as fh:
    fh.write("gene\ttier\tpheno_score\tv2score\trank_v4\trank_P0\trank_Ponly\n")
    for g in v4:
        fh.write(f"{g}\t{tiers[g][0]}\t{ph.get(g,0)}\t{tiers[g][1]}\t{rk(v4,g)}\t{rk(p0,g)}\t{rk(ponly,g)}\n")
print("written", out)
