# ROW-MAP test under PRE_REG_ROWMAP.md (sha256 9f7a440d...). Box only; no network. Writes only into the rowmap work dir.
import collections, datetime, gzip, hashlib, importlib.util, itertools, json, os, random, re, subprocess, sys
sys.dont_write_bytecode = True
SP = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/spikein/")
R = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/rowmap/")
T1 = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/track1/")
sys.path.insert(0, SP)
import spikelib as L
D = L.D
PY = os.path.expanduser("~/.venv-hackaton-h01/bin/python")
VCF = os.path.expanduser("~/Documents/HACKATON/data/WGS_EX2312012_HGWCNDSX7.vcf.gz")
AMF = os.path.expanduser("~/Documents/HACKATON/_private/models/protein/alphamissense/AlphaMissense_hg38.tsv.gz")
EVF = T1 + "scorer_check/evaluation.py"
BUB = [("15", "40209701", "T", "G"), ("15", "40220612", "T", "G")]
SET18 = ["RNU4ATAC", "RNU6ATAC", "ZRSR2", "SNRNP48", "ESCO2", "PCNT", "CENPF", "BUB1B", "TRIP13", "CEP57", "SMC5",
         "MAD1L1", "CEP192", "TRIM37", "CDC20", "MAD2L1BP", "CENATAC", "SLF2"]
AUTO = {str(i) for i in range(1, 23)}
NONPLP = {"Uncertain_significance", "Conflicting_classifications_of_pathogenicity", "Conflicting_interpretations_of_pathogenicity",
          "Likely_benign", "Benign", "Benign/Likely_benign"}
EPCR = [0.533223, 0.413611, 0.001641, 0.001631, 0.001621, 0.001611, 0.001601, 0.001591, 0.001581, 0.001571]
RULES = ["R0", "P1", "P2", "P3", "P4", "P5"]
CONS = ["C1", "C2", "C3"]
log = open(R + "run_rowmap.log", "a")
def say(*a):
    s = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + " " + " ".join(str(x) for x in a)
    print(s, flush=True); log.write(s + "\n"); log.flush()
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def kstr(k): return f"{k[0]}:{k[1]}:{k[2]}:{k[3]}"
def kparse(s): return tuple(s.split(":"))
def skey(k): return (k[0], int(k[1]), k[2], k[3])
san = {}

say("start; pre-reg sha256", sha(R + "PRE_REG_ROWMAP.md"))
vcf_before = sha(VCF); say("child VCF sha256 before", vcf_before)

# ---------- S-R4: input hashes ----------
EXP = {SP + "spikelib.py": "c64c87cf", SP + "calls_param.py": "33cc8270", SP + "consequence_param.py": "5c1d37d1",
       SP + "bg_consequence.tsv": "ffbb969d", SP + "spike_cons_visible.tsv": "d31406ec", SP + "spike_cons_hidden.tsv": "81edfe45",
       SP + "trials.tsv": "9b669a72", SP + "pools.tsv": "90e82fb9", EVF: "6d18b581",
       T1 + "TRACK1_SUBMISSION_FINAL_PROPOSED.csv": "a6527da7", D + "clinvar.vcf.gz": "05d9481d", VCF: "bec64c68"}
hashes = {p: sha(p) for p in EXP}
san["S_R4_hashes_ok"] = all(hashes[p].startswith(v) for p, v in EXP.items())
blob = subprocess.run(["git", "hash-object", EVF], capture_output=True, text=True).stdout.strip()
san["S_R4_scorer_git_blob"] = blob
san["S_R4_scorer_blob_ok"] = blob.startswith("2aed4922")
san["alphamissense_sha256"] = sha(AMF)
say("S-R4 hashes", san["S_R4_hashes_ok"], "blob", blob, "AM sha256", san["alphamissense_sha256"])
if not (san["S_R4_hashes_ok"] and san["S_R4_scorer_blob_ok"]): sys.exit("S-R4 failed")
spec = importlib.util.spec_from_file_location("ev", EVF); EV = importlib.util.module_from_spec(spec)
sys.modules["ev"] = EV; spec.loader.exec_module(EV)

# ---------- base data ----------
bg_rows = L.read_consequence(SP + "bg_consequence.tsv")
bg_seen = L.seen_from_rows(bg_rows)
orig_rows = L.read_consequence(D + "child_exonic_consequence_fixed.tsv")
spike_rows = {m: collections.defaultdict(list) for m in ("visible", "hidden")}
for m in spike_rows:
    for f in L.read_consequence(SP + f"spike_cons_{m}.tsv"): spike_rows[m][L.key(f)].append(f)
base = collections.OrderedDict()  # stratum -> list of dicts
for l in open(SP + "trials.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] == "stratum" or f[2] != "v4" or f[0] not in ("A", "A-BUB", "E"): continue
    base.setdefault(f[0], []).append({"stratum": f[0], "tid": f[1], "gene": f[3], "gtype": f[4],
        "alleles": [kparse(x) for x in f[5].split(";")], "hit_rank": f[6], "hit_gene": f[7]})
say("base trials", {s: len(v) for s, v in base.items()})

# ---------- S-R1: regenerate base trials from pools.tsv and the spike-in seeds ----------
pool = collections.defaultdict(list)
for l in open(SP + "pools.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] == "key": continue
    for g in f[1].split(","): pool[g].append(kparse(f[0]))
for g in pool: pool[g].sort(key=skey)
def is_auto_gene(g): return all(k[0] in AUTO for k in pool[g])
regen = {"A": [], "A-BUB": [], "E": []}
A_ch = sorted(g for g in SET18 if len(pool.get(g, [])) >= 2 and is_auto_gene(g))
A_hom = sorted(g for g in SET18 if len(pool.get(g, [])) >= 1)
r = random.Random(101)
for _ in range(200):
    g = r.choice(A_ch); a1, a2 = r.sample(pool[g], 2); regen["A"].append((g, "CH", {a1, a2}))
r = random.Random(102)
for _ in range(100):
    g = r.choice(A_hom); a = r.choice(pool[g]); regen["A"].append((g, "HOM", {a}))
r = random.Random(103)
for _ in range(100):
    a1, a2 = r.sample(pool["BUB1B"], 2); regen["A-BUB"].append(("BUB1B", "CH", {a1, a2}))
gs = sorted(g for g in pool if g in L.AR_GENES and g not in SET18 and is_auto_gene(g) and L.pheno(g) >= 1)
gch = [g for g in gs if len(pool[g]) >= 2]
r = random.Random(501)
for _ in range(200):
    g = r.choice(gch); a1, a2 = r.sample(pool[g], 2); regen["E"].append((g, "CH", {a1, a2}))
r = random.Random(502)
for _ in range(100):
    g = r.choice(gs); a = r.choice(pool[g]); regen["E"].append((g, "HOM", {a}))
san["S_R1_regen_equal"] = {s: [(t["gene"], t["gtype"], set(t["alleles"])) for t in base[s]] == regen[s] for s in regen}
say("S-R1", san["S_R1_regen_equal"])
if not all(san["S_R1_regen_equal"].values()): sys.exit("S-R1 failed")

# ---------- decoy pool (public ClinVar non-P/LP) through extraction and consequence ----------
need_genes = {t["gene"] for s in base for t in base[s]}
child_keys = set()
for l in open(D + "child_exonic_calls.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] != "chrom": child_keys.add((f[0], f[1], f[2], f[3]))
last_sig, rec = {}, {}
for l in gzip.open(D + "clinvar.vcf.gz", "rt"):
    if l[0] == "#": continue
    c = l.rstrip("\n").split("\t")
    ch = c[0].replace("chr", ""); alts = c[4].split(",")
    sig = c[7].split("CLNSIG=")[1].split(";")[0] if "CLNSIG=" in c[7] else "NA"
    for a in alts: last_sig[(ch, c[1], c[3], a)] = sig
    if len(alts) != 1 or ch not in AUTO: continue
    if not re.fullmatch("[ACGT]{1,50}", c[3]) or not re.fullmatch("[ACGT]{1,50}", alts[0]): continue
    info = dict(kv.split("=", 1) for kv in c[7].split(";") if "=" in kv)
    if not info.get("GENEINFO"): continue
    genes = {x.split(":")[0] for x in info["GENEINFO"].split("|")}
    if not genes & need_genes: continue
    rec[(ch, c[1], c[3], alts[0])] = info.get("AF_EXAC") or info.get("AF_ESP") or info.get("AF_TGP")
dec_all = sorted((k for k in rec if last_sig[k] in NONPLP and k not in child_keys and k not in BUB), key=skey)
say("decoy-eligible ClinVar records in base-trial genes:", len(dec_all))
with gzip.open(R + "decoy_alleles.vcf.gz", "wt") as fh:
    fh.write("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSPIKE\n")
    for k in dec_all: fh.write(f"{k[0]}\t{k[1]}\t.\t{k[2]}\t{k[3]}\t.\tPASS\t.\tGT\t0/1\n")
subprocess.run([PY, SP + "calls_param.py", R + "decoy_alleles.vcf.gz", R + "decoy_calls.tsv"], check=True, stdout=log)
with open(R + "decoy_part_visible.tsv", "w") as fh:
    fh.write("chrom\tpos\tref\talt\tgt\tfilter\tgenes\tgnomad_status\tgnomad_af\tgnomad_ac\tgnomad_an\tgnomad_filter\n")
    for l in open(R + "decoy_calls.tsv"):
        f = l.rstrip("\n").split("\t")
        if f[0] == "chrom": continue
        af = rec[(f[0], f[1], f[2], f[3])]
        st, afv = ("found", af) if af is not None else ("absent_site", "NA")
        fh.write("\t".join(f[:7] + [st, str(afv), "NA", "NA", "NA"]) + "\n")
subprocess.run([PY, SP + "consequence_param.py", R + "decoy_part_visible.tsv", R + "decoy_cons.tsv"], check=True, stdout=log)
dec_rows = collections.defaultdict(list)
for f in L.read_consequence(R + "decoy_cons.tsv"): dec_rows[L.key(f)].append(f)
DP = collections.defaultdict(list)
for k, fs in dec_rows.items():
    f = fs[0]
    if f[12] in L.CAND and f[9] in ("rare", "unobserved"): DP[f[11]].append(k)
for g in DP: DP[g].sort(key=skey)
with open(R + "decoy_pool.tsv", "w") as fh:
    fh.write("gene\tn\n")
    for g in sorted(need_genes): fh.write(f"{g}\t{len(DP.get(g, []))}\n")
san["decoy_pool_set18"] = {g: len(DP.get(g, [])) for g in SET18}
say("decoy pools (SET18):", san["decoy_pool_set18"])

# ---------- ClinVar lookup and AlphaMissense ----------
bg_pre = {L.key(f) for f in bg_seen.values() if f[12] in L.CAND and f[9] in ("rare", "unobserved")}
causal_keys = {k for s in base for t in base[s] for k in t["alleles"]}
dec_keys = {k for g in DP for k in DP[g]}
clin = L.clinvar_lookup(bg_pre | causal_keys | dec_keys | set(BUB))
mis_keys = set()
for rows in (bg_rows, orig_rows, [f for m in spike_rows for fs in spike_rows[m].values() for f in fs],
             [f for fs in dec_rows.values() for f in fs]):
    for f in rows:
        if f[12] == "missense": mis_keys.add(L.key(f))
posset = {("chr" + k[0], k[1]) for k in mis_keys}
AM, AMRES = {}, {}
with gzip.open(AMF, "rt") as fh:
    for l in fh:
        if l[0] == "#": continue
        c = l.split("\t", 10)
        if (c[0], c[1]) not in posset: continue
        k = (c[0][3:], c[1], c[2], c[3])
        if k not in mis_keys: continue
        v = float(c[8])
        if v > AM.get(k, -1.0): AM[k] = v
        if c[5] == "O60566":
            m = re.match(r"[A-Z](\d+)[A-Z]", c[7])
            if m: AMRES[k] = int(m.group(1))
san["am_missense_keys"] = len(mis_keys); san["am_found"] = len(AM); san["am_bub1b_residues"] = len(AMRES)
say("AlphaMissense: missense keys", len(mis_keys), "with a value", len(AM), "BUB1B residues", len(AMRES))

# ---------- rules ----------
TRUNC = {"nonsense", "frameshift"}
HIGH = {"nonsense", "frameshift", "splice_region", "stop_lost"}
def sv(f):
    if f[12] in TRUNC: return 1.0
    if f[12] == "missense": return AM.get(L.key(f), 0.5)
    return 0.5
def pk(f): return (int(f[1]), f[2], f[3])
def K(f): return (-(1 if f[12] in TRUNC else 0), -sv(f), pk(f))
key = L.key; hom = L.hom
def rule_R0(g, calls, cl): return L.row_map(calls)
def rule_P1(g, calls, cl):
    het = [c for c in calls if not hom(c)]
    if het: return [key(c) for c in sorted(het, key=lambda c: (0 if c[12] in HIGH else 1, pk(c)))[:2]]
    return [key(min(calls, key=pk))]
def rule_P2(g, calls, cl):
    homs = [c for c in calls if hom(c)]
    if homs: return [key(min(homs, key=K))]
    return [key(c) for c in sorted(calls, key=K)[:2]]
def rule_P3(g, calls, cl):
    het = [c for c in calls if not hom(c)]; homs = [c for c in calls if hom(c)]
    hyps = list(itertools.combinations(het, 2)) + [(h,) for h in homs]
    if not hyps: return [key(het[0])]
    best = min(hyps, key=lambda H: (-min(sv(x) for x in H), -max(sv(x) for x in H), tuple(sorted(pk(x) for x in H))))
    return [key(x) for x in best]
def rule_P4(g, calls, cl):
    if g == "BUB1B":
        het = [c for c in calls if not hom(c)]
        tr = [c for c in het if c[12] in TRUNC]
        dm = [c for c in het if c[12] == "missense" and AMRES.get(key(c)) is not None and 766 <= AMRES[key(c)] <= 1050]
        if tr and dm: return [key(min(tr, key=K)), key(min(dm, key=K))]
    return rule_P3(g, calls, cl)
def rule_P5(g, calls, cl):
    anchors = [c for c in calls if L.is_plp(cl.get(key(c), ""))]
    if not anchors: return rule_P2(g, calls, cl)
    a = min(anchors, key=K)
    if hom(a): return [key(a)]
    others = [c for c in calls if key(c) != key(a) and not hom(c)]
    if not others: return [key(a)]
    return [key(a), key(min(others, key=K))]
RULEF = {"R0": rule_R0, "P1": rule_P1, "P2": rule_P2, "P3": rule_P3, "P4": rule_P4, "P5": rule_P5}

def build(order, g3, rname, cl, cons):
    rows = [(RULEF[rname](g, g3[g], cl), g) for g in order[:10]]
    if cons == "C1": return rows
    lead = next((i for i, (rw, g) in enumerate(rows) if len(rw) == 2), None)
    if lead is None: return rows
    rw, g = rows[lead]
    byk = {key(c): c for c in g3[g]}
    ab = sorted(rw, key=lambda k: K(byk[k]))
    if cons == "C2":
        ins = [([ab[0]], g), ([ab[1]], g)]
    else:
        hets = [c for c in g3[g] if not hom(c)]
        if len(hets) < 3: return rows
        c3 = min((c for c in hets if key(c) not in rw), key=K)
        ins = [([ab[0], key(c3)], g), ([ab[1], key(c3)], g)]
    return (rows[:lead + 1] + ins + rows[lead + 1:])[:10]

TMP = R + "_score_tmp.csv"
def write_csv(path, rows, notes=None):
    with open(path, "w") as fh:
        fh.write("proband_id,chrom_1,pos_1,ref_1,alt_1,chrom_2,pos_2,ref_2,alt_2,epcr,finding_type,notes\n")
        for i, (rw, g) in enumerate(rows):
            v1 = rw[0]; v2 = rw[1] if len(rw) > 1 else None
            second = f"chr{v2[0]},{v2[1]},{v2[2]},{v2[3]}" if v2 else ",,,"
            fh.write(f"PROBAND01,chr{v1[0]},{v1[1]},{v1[2]},{v1[3]},{second},{EPCR[i]},primary,{notes[i] if notes else ''}\n")
def score(rows, truth):
    write_csv(TMP, rows)
    sub = EV.load_submission(TMP)["PROBAND01"]
    res = EV.score_proband("PROBAND01", sub, frozenset(("chr" + k[0], int(k[1]), k[2], k[3]) for k in truth))
    return res

def run_rank(extra_rows, hidden):
    seen = dict(bg_seen)
    for f in extra_rows: seen.setdefault(key(f), f)
    cands = L.v3_candidates(seen.values())
    cl = {k: v for k, v in clin.items() if k not in hidden} if hidden else clin
    o3, t3, g3 = L.rank_v3(cands, cl)
    o4, _, _ = L.rank_v4(o3, t3, g3, amendment1=True)
    return o4, g3, cl

# ---------- S-R3: real data ----------
seen_o = L.seen_from_rows(orig_rows)
ro3, rt3, rg3 = L.rank_v3(L.v3_candidates(seen_o.values()), clin)
ro4, _, _ = L.rank_v4(ro3, rt3, rg3, amendment1=True)
csv_rows = [l.rstrip("\n").split(",") for l in open(T1 + "TRACK1_SUBMISSION_FINAL_PROPOSED.csv")][1:]
csv_sets = [frozenset(x for x in [(c[1].replace("chr", ""), c[2], c[3], c[4]), (c[5].replace("chr", ""), c[6], c[7], c[8])] if x[0]) for c in csv_rows]
csv_genes = [c[11].split(";")[0] for c in csv_rows]
real = {}
for rn in RULES:
    for cn in CONS:
        real[(rn, cn)] = build(ro4, rg3, rn, clin, cn)
r0 = real[("R0", "C1")]
san["S_R3_top10_equals_csv_genes"] = ro4[:10] == csv_genes
san["S_R3_R0C1_rows_equal_csv"] = [frozenset(rw) for rw, g in r0] == csv_sets
k1 = score(r0, set(r0[0][0]))
san["S_R3_key_row1_points_fmax"] = [k1.rank_points, k1.f_max]
say("S-R3", san["S_R3_top10_equals_csv_genes"], san["S_R3_R0C1_rows_equal_csv"], san["S_R3_key_row1_points_fmax"])
if not (san["S_R3_top10_equals_csv_genes"] and san["S_R3_R0C1_rows_equal_csv"] and k1.rank_points == 100 and k1.f_max == 1.0):
    sys.exit("S-R3 failed")
with open(R + "real_rows.tsv", "w") as fh:
    fh.write("rule\tconstruction\trow\tgene\tvariants\tsame_as_R0C1_row\n")
    for (rn, cn), rows in real.items():
        for i, (rw, g) in enumerate(rows):
            same = i < len(r0) and frozenset(rw) == frozenset(r0[i][0])
            fh.write(f"{rn}\t{cn}\t{i + 1}\t{g}\t{';'.join(kstr(k) for k in sorted(rw, key=skey))}\t{same}\n")
real_diff = {}
for (rn, cn), rows in real.items():
    real_diff[f"{rn}x{cn}"] = {"row1_same": frozenset(rows[0][0]) == frozenset(r0[0][0]) and rows[0][1] == r0[0][1],
        "changed_rows": [i + 1 for i in range(10) if i >= len(rows) or frozenset(rows[i][0]) != frozenset(r0[i][0])],
        "genes": [g for _, g in rows], "row_sizes": [len(rw) for rw, _ in rows]}
san["real_diff"] = real_diff

# ---------- trials ----------
def trial_rows(t, mode, decoys):
    gt = "0/1" if t["gtype"] == "CH" else "1/1"
    extra = []
    for k in t["alleles"]:
        for f in spike_rows[mode].get(k, []):
            g2 = list(f); g2[4] = gt; extra.append(g2)
    for k in decoys:
        for f in dec_rows[k]:
            g2 = list(f); g2[4] = "0/1"; extra.append(g2)
    return extra

OUT = open(R + "trials_rowmap.tsv", "w")
OUT.write("stratum\ttid\tgene\tgtype\td\tmode\thit_rank\thit_gene\tn_causal_gene_calls\tdecoys_candidate\trule\tconstruction\t"
          "points\tfmax\tfull_rank\tpartial_rank\trow1_exact\tcausal_row_exact\tnrows\n")
def run_trial(stratum, t, d, decoys, mode):
    hidden = set(t["alleles"]) if mode == "hidden" else set()
    o4, g3, cl = run_rank(trial_rows(t, mode, decoys), hidden)
    truth = set(t["alleles"])
    hit = next(((i, g) for i, g in enumerate(o4, 1) if {key(c) for c in g3[g]} & truth), None)
    hg = hit[1] if hit else ""
    ncalls = len(g3[hg]) if hit else 0
    dc = sum(1 for k in decoys if t["gene"] in g3 and k in {key(c) for c in g3[t["gene"]]})
    out = {}
    for rn in RULES:
        crow = frozenset(RULEF[rn](hg, g3[hg], cl)) == frozenset(truth) if hit else False
        for cn in CONS:
            rows = build(o4, g3, rn, cl, cn)
            res = score(rows, truth)
            r1 = frozenset(rows[0][0]) == frozenset(truth)
            out[(rn, cn)] = (res.rank_points, res.f_max, crow)
            OUT.write(f"{stratum}\t{t['tid']}-d{d}{'h' if mode == 'hidden' else ''}\t{t['gene']}\t{t['gtype']}\t{d}\t{mode}\t"
                      f"{hit[0] if hit else 'none'}\t{hg}\t{ncalls}\t{dc}\t{rn}\t{cn}\t{res.rank_points}\t{res.f_max:.6f}\t"
                      f"{res.full_match_rank}\t{res.partial_match_rank}\t{r1}\t{crow}\t{len(rows)}\n")
    return hit, g3, hg, out

say("FIRST TRIAL RANKING (d0 controls) starts now")
sr2_bad, sr5_bad, n_d0 = [], [], 0
for s in ("A", "A-BUB", "E"):
    for t in base[s]:
        hit, g3, hg, out = run_trial(s + "-d0", t, 0, [], "visible")
        n_d0 += 1
        exp = (t["hit_rank"], t["hit_gene"])
        got = (str(hit[0]) if hit else "none", hg)
        if exp != got: sr2_bad.append((t["tid"], exp, got))
        if hit:
            calls = g3[hg]
            if len(calls) == 1 or (len(calls) == 2 and not any(hom(c) for c in calls)):
                rs = {frozenset(RULEF[rn](hg, calls, clin)) for rn in RULES}
                if len(rs) != 1: sr5_bad.append(t["tid"])
san["S_R2_d0_trials"] = n_d0; san["S_R2_mismatches"] = sr2_bad[:20]; san["S_R2_ok"] = not sr2_bad
san["S_R5_mismatches"] = sr5_bad[:20]; san["S_R5_ok"] = not sr5_bad
say("S-R2", san["S_R2_ok"], len(sr2_bad), "S-R5", san["S_R5_ok"], len(sr5_bad))
if not (san["S_R2_ok"] and san["S_R5_ok"]):
    OUT.close(); json.dump(san, open(R + "sanity_rowmap.json", "w"), indent=1, default=str); sys.exit("S-R2/S-R5 failed")

say("decoy strata start")
draws = {}
for s, seed in (("A", 601), ("E", 602), ("A-BUB", 603)):
    r = random.Random(seed)
    for t in base[s]:
        g = t["gene"]
        if not all(k[0] in AUTO for k in t["alleles"]) or len(DP.get(g, [])) < 1: continue
        P = DP[g]
        dd = r.sample(P, 2) if len(P) >= 2 else [P[0]]
        draws[(s, t["tid"])] = dd
with open(R + "decoy_draws.tsv", "w") as fh:
    fh.write("stratum\ttid\tgene\tdecoys\n")
    for (s, tid), dd in draws.items():
        g = next(t["gene"] for t in base[s] if t["tid"] == tid)
        fh.write(f"{s}\t{tid}\t{g}\t{';'.join(kstr(k) for k in dd)}\n")
ndec = collections.Counter()
dec_cand = collections.Counter()
for s in ("A", "E", "A-BUB"):
    for t in base[s]:
        dd = draws.get((s, t["tid"]))
        if not dd: continue
        lab = {"A": "A", "E": "E", "A-BUB": "A-BUB"}[s]
        for d in (1, 2):
            if d > len(dd): continue
            st = f"{lab}-{t['gtype']}-dec" if s != "A-BUB" else "A-BUB-dec"
            hit, g3, hg, out = run_trial(st, t, d, dd[:d], "visible")
            ndec[st] += 1
            dec_cand[st] += sum(1 for k in dd[:d] if t["gene"] in g3 and k in {key(c) for c in g3[t["gene"]]})
            dec_cand[st + "_drawn"] += d
            if s == "A":
                run_trial("A-hid-dec", t, d, dd[:d], "hidden"); ndec["A-hid-dec"] += 1
san["n_decoy_trials"] = dict(ndec)
san["decoys_candidate_fraction"] = {k: dec_cand[k] / dec_cand[k + "_drawn"] for k in ndec if k + "_drawn" in dec_cand}
OUT.close()
say("trials done:", dict(ndec))
vcf_after = sha(VCF); san["vcf_unchanged"] = vcf_after == vcf_before
say("child VCF sha256 after", vcf_after, "unchanged:", vcf_after == vcf_before)
json.dump(san, open(R + "sanity_rowmap.json", "w"), indent=1, default=str)
os.remove(TMP)
