# Spike-in run under PRE_REG_SPIKEIN_EPCR.md (sha256 6d40e58f...). Box only; no network. Writes into the work dir only.
import collections, datetime, glob, gzip, hashlib, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spikelib as L
import pysam
D, W = L.D, L.W
PY = os.path.expanduser("~/.venv-hackaton-h01/bin/python")
VCF = os.path.expanduser("~/Documents/HACKATON/data/WGS_EX2312012_HGWCNDSX7.vcf.gz")
FA = "/media/[redacted]/[redacted]/hackaton_offload/full_wgs/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"
GTF = D + "gencode.v44.basic.annotation.gtf.gz"
BUB = [("15", "40209701", "T", "G"), ("15", "40220612", "T", "G")]
SET18 = ["RNU4ATAC", "RNU6ATAC", "ZRSR2", "SNRNP48", "ESCO2", "PCNT", "CENPF", "BUB1B", "TRIP13", "CEP57", "SMC5",
         "MAD1L1", "CEP192", "TRIM37", "CDC20", "MAD2L1BP", "CENATAC", "SLF2"]
PLP = ("Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic")
AUTO = {str(i) for i in range(1, 23)}
log = open(W + "run.log", "a")
def say(*a):
    s = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + " " + " ".join(str(x) for x in a)
    print(s, flush=True); log.write(s + "\n"); log.flush()
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def kstr(k): return f"{k[0]}:{k[1]}:{k[2]}:{k[3]}"

say("start; pre-reg sha256", sha(W + "PRE_REG_SPIKEIN_EPCR.md"))
vcf_sha_before = sha(VCF); say("child VCF sha256 before", vcf_sha_before)

# ---------- 1. masked background ----------
parts = sorted(glob.glob(D + "child_exonic_gnomad_exomes.part*.tsv"))
removed = []
for i, p in enumerate(parts):
    lines = open(p).readlines()
    keep = [lines[0]]
    for l in lines[1:]:
        f = l.rstrip("\n").split("\t")
        if (f[0], f[1], f[2], f[3]) in BUB: removed.append(l)
        else: keep.append(l)
    open(W + f"masked_part{i}.tsv", "w").writelines(keep)
say("masked rows removed:", len(removed))
subprocess.run([PY, W + "consequence_param.py", W + "masked_part*.tsv", W + "bg_consequence.tsv"], check=True, stdout=log)
orig = open(D + "child_exonic_consequence_fixed.tsv").readlines()
bg_lines = open(W + "bg_consequence.tsv").readlines()
exp = [l for l in orig if tuple(l.split("\t")[:4]) not in BUB]
san = {"removed_rows": len(removed), "S2_masked_equals_original_minus_bub1b": bg_lines == exp,
       "original_rows_dropped": len(orig) - len(exp)}
bg_rows = L.read_consequence(W + "bg_consequence.tsv")
orig_rows = L.read_consequence(D + "child_exonic_consequence_fixed.tsv")
bub_rows = [f for f in orig_rows if L.key(f) in BUB]

# ---------- 2. pools (public ClinVar) ----------
child_keys = set()
for l in open(D + "child_exonic_calls.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] != "chrom": child_keys.add((f[0], f[1], f[2], f[3]))
last_sig, elig = {}, {}
for l in gzip.open(D + "clinvar.vcf.gz", "rt"):
    if l[0] == "#": continue
    c = l.rstrip("\n").split("\t")
    ch = c[0].replace("chr", "")
    alts = c[4].split(",")
    sig = c[7].split("CLNSIG=")[1].split(";")[0] if "CLNSIG=" in c[7] else "NA"
    for a in alts: last_sig[(ch, c[1], c[3], a)] = sig
    if sig not in PLP or len(alts) != 1: continue
    if not re.fullmatch("[ACGT]{1,50}", c[3]) or not re.fullmatch("[ACGT]{1,50}", alts[0]): continue
    if ch not in AUTO and ch != "X": continue
    info = dict(kv.split("=", 1) for kv in c[7].split(";") if "=" in kv)
    if not info.get("GENEINFO"): continue
    genes = [x.split(":")[0] for x in info["GENEINFO"].split("|")]
    elig[(ch, c[1], c[3], alts[0])] = {"genes": genes, "mc": info.get("MC", ""),
        "af": info.get("AF_EXAC") or info.get("AF_ESP") or info.get("AF_TGP"),
        "af_src": "EXAC" if info.get("AF_EXAC") else ("ESP" if info.get("AF_ESP") else ("TGP" if info.get("AF_TGP") else "none"))}
pool_all = {k: v for k, v in elig.items() if last_sig[k] in PLP and k not in child_keys and k not in BUB}
pool = collections.defaultdict(list)
for k, v in pool_all.items():
    for g in v["genes"]: pool[g].append(k)
def skey(k): return (k[0], int(k[1]), k[2], k[3])
for g in pool: pool[g].sort(key=skey)
with open(W + "pools.tsv", "w") as fh:
    fh.write("key\tgenes\tmc\taf\taf_src\n")
    for k in sorted(pool_all, key=skey):
        v = pool_all[k]; fh.write(f"{kstr(k)}\t{','.join(v['genes'])}\t{v['mc']}\t{v['af']}\t{v['af_src']}\n")
say("eligible pool alleles:", len(pool_all), "excluded as child keys:", sum(1 for k in elig if k in child_keys))
san["pool_size_set18"] = {g: len(pool.get(g, [])) for g in SET18}
san["child_bub1b_nonsense_in_pool"] = BUB[0] in pool_all

# ---------- 3. synthetic stop-loss alleles (C2) ----------
canon = {}
stops = collections.defaultdict(list)
with gzip.open(GTF, "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.rstrip("\n").split("\t", 8)
        if c[2] != "stop_codon": continue
        at = c[8]
        if 'transcript_type "protein_coding"' not in at or 'tag "Ensembl_canonical"' not in at: continue
        gname = at.split('gene_name "')[1].split('"')[0]
        if gname not in SET18: continue
        tid = at.split('transcript_id "')[1].split('"')[0]
        canon[gname] = (tid, c[0].replace("chr", ""), c[6])
        stops[gname].append((int(c[3]), int(c[4])))
fa = pysam.FastaFile(FA)
pre = "chr" if any(r.startswith("chr") for r in fa.references) else ""
COMP = {"A": "T", "C": "G", "G": "C", "T": "A"}
STOPC = {"TAA", "TAG", "TGA"}
synth, synth_gene, synth_log = [], {}, {}
for g in sorted(canon):
    tid, ch, strand = canon[g]
    pos = sorted(p for s, e in stops[g] for p in range(s, e + 1))
    if strand == "-": pos = pos[::-1]
    gref = [fa.fetch(pre + ch, p - 1, p).upper() for p in pos]
    codon = "".join(gref) if strand == "+" else "".join(COMP[b] for b in gref)
    synth_log[g] = {"transcript": tid, "strand": strand, "positions": pos, "codon": codon}
    if len(pos) != 3 or codon not in STOPC: continue
    for j in range(3):
        for b in "ACGT":
            if b == codon[j]: continue
            mut = codon[:j] + b + codon[j + 1:]
            if mut in STOPC: continue
            alt = b if strand == "+" else COMP[b]
            k = (ch, str(pos[j]), gref[j], alt)
            if k in child_keys: continue
            synth.append(k); synth_gene[k] = g
san["synthetic_stop_codons"] = synth_log
say("synthetic stop-loss alleles:", len(synth))

# ---------- 4. trials ----------
trials = []  # dict: stratum, tid, genes, gtype, alleles [(key, gt, mode)]
def add(stratum, gene, gtype, alleles):
    trials.append({"stratum": stratum, "tid": f"{stratum}-{sum(1 for t in trials if t['stratum'] == stratum) + 1:03d}",
                   "gene": gene, "gtype": gtype, "alleles": alleles})
def is_auto_gene(g): return all(k[0] in AUTO for k in pool[g])
A_ch = sorted(g for g in SET18 if len(pool.get(g, [])) >= 2 and is_auto_gene(g))
A_hom = sorted(g for g in SET18 if len(pool.get(g, [])) >= 1)
def hom_gt(k): return "1/1"
r = random.Random(101)
A_trials = []
for _ in range(200):
    g = r.choice(A_ch); a1, a2 = r.sample(pool[g], 2)
    A_trials.append((g, "CH", [(a1, "0/1"), (a2, "0/1")]))
r = random.Random(102)
for _ in range(100):
    g = r.choice(A_hom); a = r.choice(pool[g])
    A_trials.append((g, "HOM", [(a, "1/1")]))
for g, gt_, al in A_trials: add("A", g, gt_, [(k, gt, "visible") for k, gt in al])
r = random.Random(103)
for _ in range(100):
    a1, a2 = r.sample(pool["BUB1B"], 2); add("A-BUB", "BUB1B", "CH", [(a1, "0/1", "visible"), (a2, "0/1", "visible")])
for g, gt_, al in A_trials: add("B", g, gt_, [(k, gt, "hidden") for k, gt in al])
c1pool = sorted((k for k in pool_all if "stop_lost" in pool_all[k]["mc"] and len(k[2]) == 1 and len(k[3]) == 1), key=skey)
r = random.Random(301)
for k in r.sample(c1pool, min(100, len(c1pool))):
    add("C1", ",".join(pool_all[k]["genes"]), "HOM", [(k, "1/1", "visible")])
for k in synth:
    add("C2-HOM", synth_gene[k], "HOM", [(k, "1/1", "hidden")])
r = random.Random(302)
for k in synth:
    g = synth_gene[k]
    if k[0] in AUTO and pool.get(g):
        add("C2-CH", g, "CH", [(k, "0/1", "hidden"), (r.choice(pool[g]), "0/1", "visible")])
def ctrl_genes(cond):
    gs = sorted(g for g in pool if g in L.AR_GENES and g not in SET18 and is_auto_gene(g) and cond(L.pheno(g)))
    return [g for g in gs if len(pool[g]) >= 2], gs
for name, cond, s1, s2 in (("D", lambda p: p == 0, 401, 402), ("E", lambda p: p >= 1, 501, 502)):
    gch, ghom = ctrl_genes(cond)
    san[f"{name}_genes_ch"], san[f"{name}_genes_hom"] = len(gch), len(ghom)
    r = random.Random(s1)
    for _ in range(200):
        g = r.choice(gch); a1, a2 = r.sample(pool[g], 2); add(name, g, "CH", [(a1, "0/1", "visible"), (a2, "0/1", "visible")])
    r = random.Random(s2)
    for _ in range(100):
        g = r.choice(ghom); a = r.choice(pool[g]); add(name, g, "HOM", [(a, "1/1", "visible")])
san["A_genes_ch"], san["A_genes_hom"] = A_ch, A_hom
san["n_trials"] = dict(collections.Counter(t["stratum"] for t in trials))
say("trials:", san["n_trials"])

# ---------- 5. spiked alleles through extraction, frequency, consequence ----------
allk = sorted({k for t in trials for k, _, _ in t["alleles"]}, key=skey)
with gzip.open(W + "spike_alleles.vcf.gz", "wt") as fh:
    fh.write("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSPIKE\n")
    for k in allk: fh.write(f"{k[0]}\t{k[1]}\t.\t{k[2]}\t{k[3]}\t.\tPASS\t.\tGT\t0/1\n")
subprocess.run([PY, W + "calls_param.py", W + "spike_alleles.vcf.gz", W + "spike_calls.tsv"], check=True, stdout=log)
extracted = {}
for l in open(W + "spike_calls.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] != "chrom": extracted[(f[0], f[1], f[2], f[3])] = f
synth_set = set(synth)
for mode in ("visible", "hidden"):
    with open(W + f"spike_part_{mode}.tsv", "w") as fh:
        fh.write("chrom\tpos\tref\talt\tgt\tfilter\tgenes\tgnomad_status\tgnomad_af\tgnomad_ac\tgnomad_an\tgnomad_filter\n")
        for k in allk:
            if k not in extracted: continue
            f = extracted[k]
            af = pool_all[k]["af"] if (mode == "visible" and k not in synth_set and k in pool_all) else None
            st, afv = ("found", af) if af is not None else ("absent_site", "NA")
            fh.write("\t".join(f[:7] + [st, str(afv), "NA", "NA", "NA"]) + "\n")
    subprocess.run([PY, W + "consequence_param.py", W + f"spike_part_{mode}.tsv", W + f"spike_cons_{mode}.tsv"], check=True, stdout=log)
spike_rows = {m: collections.defaultdict(list) for m in ("visible", "hidden")}
for m in spike_rows:
    for f in L.read_consequence(W + f"spike_cons_{m}.tsv"): spike_rows[m][L.key(f)].append(f)

# ---------- 6. ClinVar lookup (v3 semantics) over background candidates + all spiked keys ----------
bg_seen = L.seen_from_rows(bg_rows)
bg_pre = [f for f in bg_seen.values() if f[12] in L.CAND and f[9] in ("rare", "unobserved")]
clin = L.clinvar_lookup({L.key(f) for f in bg_pre} | set(allk) | set(BUB))

def run_rank(extra_rows, hidden):
    seen = dict(bg_seen)
    for f in extra_rows: seen.setdefault(L.key(f), f)
    cands = L.v3_candidates(seen.values())
    cl = {k: v for k, v in clin.items() if k not in hidden} if hidden else clin
    o3, t3, g3 = L.rank_v3(cands, cl)
    o4, tiers4, ph4 = L.rank_v4(o3, t3, g3, amendment1=True)
    return o3, t3, g3, o4, tiers4, ph4, cands, seen, cl

# ---------- 7. sanity S1, S3 (no spike in S1; S3 adds back the real pair) ----------
o3, t3, g3, o4, _, _, cands, seen, _ = run_rank([], set())
san["S1_bub_keys_absent"] = all(k not in seen for k in BUB)
san["S1_no_bub1b_candidate"] = not any(f[11] == "BUB1B" for f in cands)
san["S1_bub1b_not_ranked"] = "BUB1B" not in o3 and "BUB1B" not in o4
san["masked_v4_top10"] = o4[:10]
oo3, ot3, og3 = L.rank_v3(L.v3_candidates(L.seen_from_rows(orig_rows).values()), clin)
oo4, _, _ = L.rank_v4(oo3, ot3, og3, amendment1=True)
u3, _, _, u4, _, _, _, _, _ = run_rank(bub_rows, set())
san["S3_bub1b_v4_rank"] = u4.index("BUB1B") + 1 if "BUB1B" in u4 else None
san["S3_bub1b_v3_rank"] = u3.index("BUB1B") + 1 if "BUB1B" in u3 else None
san["S3_v4_order_equals_unspiked"] = u4 == oo4
san["S3_v3_order_equals_unspiked"] = u3 == oo3
json.dump(san, open(W + "sanity.json", "w"), indent=1)
gate = san["S2_masked_equals_original_minus_bub1b"] and san["S1_bub_keys_absent"] and san["S1_no_bub1b_candidate"] \
    and san["S1_bub1b_not_ranked"] and san["S3_bub1b_v4_rank"] == 1 and san["S3_bub1b_v3_rank"] == 1 and san["S3_v4_order_equals_unspiked"]
say("sanity gate S1-S3:", gate)
if not gate: sys.exit("sanity gate failed; see sanity.json")

# ---------- 8. trials ----------
say("FIRST SPIKED RANKING RUN starts now")
T = open(W + "trials.tsv", "w")
T.write("stratum\ttid\tversion\tgene\tgtype\talleles\thit_rank\thit_gene\thit_tier\thit_pheno\tfull_row\thalf_row\trows10\n")
A_ = open(W + "alleles.tsv", "w")
A_.write("stratum\ttid\tallele\tgt\tmode\tsource\textracted\tconsequence\tfreq_class\tcandidate\tclinvar_plp_visible\taf_src\n")
for t in trials:
    extra, hidden = [], set()
    for k, gt, mode in t["alleles"]:
        for f in spike_rows[mode].get(k, []):
            g2 = list(f); g2[4] = gt; extra.append(g2)
        if mode == "hidden": hidden.add(k)
    o3, t3, g3, o4, tiers4, ph4, cands, seen, cl = run_rank(extra, hidden)
    ks = {k for k, _, _ in t["alleles"]}
    ckeys = {L.key(f) for f in cands}
    for k, gt, mode in t["alleles"]:
        f = seen.get(k)
        src = "synthetic" if k in synth_set else "clinvar"
        A_.write(f"{t['stratum']}\t{t['tid']}\t{kstr(k)}\t{gt}\t{mode}\t{src}\t{k in extracted}\t{f[12] if f else 'NA'}\t"
                 f"{f[9] if f else 'NA'}\t{k in ckeys}\t{L.is_plp(cl.get(k, ''))}\t{pool_all[k]['af_src'] if k in pool_all else 'none'}\n")
    for ver, order, tier in (("v4", o4, {g: tiers4[g][0] for g in o4}), ("v3", o3, t3)):
        hit = None
        for i, g in enumerate(order, 1):
            if {L.key(c) for c in g3[g]} & ks: hit = (i, g); break
        sig = []
        for g in order[:10]:
            row = set(L.row_map(g3[g])); sig.append(f"{len(row)}:{len(row & ks)}")
        full = half = False
        if hit:
            row = set(L.row_map(g3[hit[1]])); full = row == ks; half = bool(row & ks) and not full
        T.write(f"{t['stratum']}\t{t['tid']}\t{ver}\t{t['gene']}\t{t['gtype']}\t{';'.join(kstr(k) for k in sorted(ks, key=skey))}\t"
                f"{hit[0] if hit else 'none'}\t{hit[1] if hit else ''}\t{tier[hit[1]] if hit else ''}\t{L.pheno(hit[1]) if hit else ''}\t"
                f"{full}\t{half}\t{'|'.join(sig)}\n")
T.close(); A_.close()
say("trials done:", len(trials))
vcf_sha_after = sha(VCF); say("child VCF sha256 after", vcf_sha_after, "unchanged:", vcf_sha_after == vcf_sha_before)
