# Feasibility counts for the spike-in design. PUBLIC DATA ONLY (ClinVar, GENCODE, HPO). No child data read, no ranking run.
import collections, gzip, os, re, json
D = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/")
W = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/spikein/")
SET18 = ["RNU4ATAC", "RNU6ATAC", "ZRSR2", "SNRNP48", "ESCO2", "PCNT", "CENPF",
         "BUB1B", "TRIP13", "CEP57", "SMC5", "MAD1L1", "CEP192", "TRIM37", "CDC20",
         "MAD2L1BP", "CENATAC", "SLF2"]
PLP = ("Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic")
CHILD = ["HP:0000121", "HP:0001508", "HP:0001518", "HP:0001622", "HP:0002859", "HP:0003202", "HP:0004322", "HP:0200067"]
# HPO, same code as ranking_v4_fixed.py
parents = collections.defaultdict(set); cur = None
for l in open(D + "hp.obo"):
    l = l.rstrip("\n")
    if l == "[Term]": cur = None
    elif l.startswith("id: HP:"): cur = l[4:]
    elif l.startswith("is_a: HP:") and cur: parents[cur].add(l[6:16])
anc_c = {}
def ancestors(t):
    if t in anc_c: return anc_c[t]
    out = {t}; st = [t]
    while st:
        x = st.pop()
        for p in parents.get(x, ()):
            if p not in out: out.add(p); st.append(p)
    anc_c[t] = out; return out
gene_terms = collections.defaultdict(set)
for l in open(D + "genes_to_phenotype.txt"):
    if l.startswith("ncbi_gene_id"): continue
    f = l.rstrip("\n").split("\t")
    if len(f) >= 3: gene_terms[f[1]].add(f[2])
def pheno(g):
    a = set()
    for t in gene_terms.get(g, ()): a |= ancestors(t)
    return sum(1 for c in CHILD if c in a)
AR = {g for g, ts in gene_terms.items() if "HP:0000007" in ts}
# ClinVar scan: last record per key wins (as ranking_v3_fixed.py)
last = {}
recs = []
for l in gzip.open(D + "clinvar.vcf.gz", "rt"):
    if l[0] == "#": continue
    c = l.rstrip("\n").split("\t")
    ch = c[0].replace("chr", "")
    alts = c[4].split(",")
    sig = c[7].split("CLNSIG=")[1].split(";")[0] if "CLNSIG=" in c[7] else "NA"
    for a in alts: last[(ch, c[1], c[3], a)] = sig
    if sig not in PLP or len(alts) != 1: continue
    if not re.fullmatch("[ACGT]{1,50}", c[3]) or not re.fullmatch("[ACGT]{1,50}", alts[0]): continue
    if ch not in [str(i) for i in range(1, 23)] + ["X"]: continue
    info = dict(kv.split("=", 1) for kv in c[7].split(";") if "=" in kv)
    gi = info.get("GENEINFO", "")
    if not gi or "|" in gi: continue
    recs.append((ch, c[1], c[3], alts[0], gi.split(":")[0], info.get("MC", ""), info.get("AF_EXAC"), info.get("AF_ESP"), info.get("AF_TGP")))
recs = [r for r in recs if last[(r[0], r[1], r[2], r[3])] in PLP]
by_gene = collections.defaultdict(list)
for r in recs: by_gene[r[4]].append(r)
out = {"eligible_plp_records": len(recs)}
out["set18"] = {g: {"n": len(by_gene.get(g, [])), "pheno": pheno(g), "AR": g in AR,
                    "snv": sum(1 for r in by_gene.get(g, []) if len(r[2]) == 1 and len(r[3]) == 1),
                    "chrom": sorted({r[0] for r in by_gene.get(g, [])})} for g in SET18}
sl = [r for r in recs if "stop_lost" in r[5] and len(r[2]) == 1 and len(r[3]) == 1]
out["stop_lost_snv"] = len(sl)
out["stop_lost_genes"] = len({r[4] for r in sl})
ctrl = [g for g in by_gene if g in AR and pheno(g) == 0 and g not in SET18 and all(r[0] != "X" for r in by_gene[g])]
out["control_genes_ge1"] = len(ctrl)
out["control_genes_ge2"] = sum(1 for g in ctrl if len(by_gene[g]) >= 2)
af = collections.Counter("exac" if r[6] else ("esp" if r[7] else ("tgp" if r[8] else "none")) for r in recs)
out["af_source_counts"] = dict(af)
out["af_ge_0.001_by_exac_first"] = sum(1 for r in recs if (r[6] or r[7] or r[8]) and float(r[6] or r[7] or r[8]) >= 0.001)
print(json.dumps(out, indent=1))
