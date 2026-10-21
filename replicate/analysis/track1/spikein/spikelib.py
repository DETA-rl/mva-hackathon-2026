# Spike-in library: ranking v3 / v4 logic copied from ranking_v3_fixed.py and ranking_v4_fixed.py (+ Amendment 1 as in
# ranking_v4b.py), ClinVar lookup with the same matching semantics, ROW-MAP, and a scorer re-implemented from
# SPACE_RULES_T1.md (description of the Space evaluation.py; the code itself was not run here).
import collections, gzip, os, re
D = os.environ["REPL_OUT"] + "/"
W = os.environ["REPL_OUT"] + "/"
CHILD = ["HP:0000121", "HP:0001508", "HP:0001518", "HP:0001622", "HP:0002859", "HP:0003202", "HP:0004322", "HP:0200067"]

# ---------- v3 (verbatim logic from ranking_v3_fixed.py) ----------
CAND = {"nonsense", "frameshift", "stop_lost", "missense", "inframe_indel", "splice_region"}
WT = {"nonsense": 3, "frameshift": 3, "stop_lost": 2, "splice_region": 2, "inframe_indel": 2, "missense": 1}
PARA = re.compile(r"^(HLA-|TAS2R|MUC|LILRA|LILRB|OR\d|ZNF|PRDM9|NBPF|SERPINA)")
PAR = [(10001, 2781479), (155701383, 156030895)]
def in_par(p): return any(a <= p <= b for a, b in PAR)
def hom(f): return f[4] in ("1/1", "1|1")
def is_plp(sig): return sig in ("Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic")
def key(f): return (f[0], f[1], f[2], f[3])

def read_consequence(path):
    rows = []
    for l in open(path):
        f = l.rstrip("\n").split("\t")
        if f[0] == "chrom": continue
        rows.append(f)
    return rows

def seen_from_rows(rows, seen=None):
    seen = {} if seen is None else seen
    for f in rows:
        seen.setdefault(key(f), f)
    return seen

def v3_candidates(seen_values):
    cands = [f for f in seen_values if f[12] in CAND and f[9] in ("rare", "unobserved")]
    cands = [f for f in cands if not (f[0] == "X" and not in_par(int(f[1])) and not hom(f))]
    bg = collections.defaultdict(list)
    for f in cands: bg[f[11]].append(f)
    clustered = set()
    for g, calls in bg.items():
        ps = sorted(int(c[1]) for c in calls)
        for p in ps:
            w = [c for c in calls if p <= int(c[1]) <= p + 1000]
            if len(w) >= 5 and all(hom(c) for c in w): clustered.add(g); break
    return [f for f in cands if f[11] not in clustered and not PARA.match(f[11])]

def clinvar_lookup(keys):
    """Same semantics as ranking_v3_fixed.py: exact chrom/pos/ref/alt, any alt of the record, last record wins."""
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
    return clin

def v2score(calls): return sum(WT[c[12]] * (1.5 if hom(c) else 1) for c in calls)
def compound(calls):
    lof = any(c[12] in ("nonsense", "frameshift", "splice_region") for c in calls)
    mis = any(c[12] == "missense" for c in calls)
    return lof and mis and len(calls) >= 2

def rank_v3(cands, clin):
    genes = collections.defaultdict(list)
    for f in cands: genes[f[11]].append(f)
    tierA = {g for g, calls in genes.items() if any(is_plp(clin.get(key(c), "")) for c in calls)}
    tierB = {g for g, calls in genes.items() if g not in tierA and compound(calls)}
    tierC = {g for g, calls in genes.items() if g not in tierA | tierB and (v2score(calls) >= 3 or any(hom(c) for c in calls))}
    def k(g):
        t = 0 if g in tierA else (1 if g in tierB else 2)
        return (t, -v2score(genes[g]), g)
    order = sorted(tierA | tierB | tierC, key=k)
    tier = {g: ("A" if g in tierA else ("B" if g in tierB else "C")) for g in order}
    return order, tier, genes

def v3_summary_lines(order, tier, genes):
    out = ["gene\ttier\tv2score\tcalls\trank_v3\n"]
    for i, g in enumerate(order, 1):
        out.append(f"{g}\t{tier[g]}\t{v2score(genes[g])}\t{len(genes[g])}\t{i}\n")
    return out

# ---------- v4 phenotype layer (verbatim logic from ranking_v4_fixed.py) ----------
_parents = collections.defaultdict(set); _cur = None
for _l in open(D + "hp.obo"):
    _l = _l.rstrip("\n")
    if _l == "[Term]": _cur = None
    elif _l.startswith("id: HP:"): _cur = _l[4:]
    elif _l.startswith("is_a: HP:") and _cur: _parents[_cur].add(_l[6:16])
_anc = {}
def ancestors(t):
    if t in _anc: return _anc[t]
    out = {t}; stack = [t]
    while stack:
        x = stack.pop()
        for p in _parents.get(x, ()):
            if p not in out: out.add(p); stack.append(p)
    _anc[t] = out
    return out
gene_terms = collections.defaultdict(set)
for _l in open(D + "genes_to_phenotype.txt"):
    if _l.startswith("ncbi_gene_id"): continue
    _f = _l.rstrip("\n").split("\t")
    if len(_f) >= 3: gene_terms[_f[1]].add(_f[2])
matched = collections.defaultdict(set)
for _g, _terms in gene_terms.items():
    _a = set()
    for _t in _terms: _a |= ancestors(_t)
    for _c in CHILD:
        if _c in _a: matched[_g].add(_c)
def pheno(g): return len(matched.get(g, set()))
AR_GENES = {g for g, ts in gene_terms.items() if "HP:0000007" in ts}

def rank_v4(order3, tier3, genes3, amendment1=True):
    """v4 reads (gene, tier, float(v2)) from the v3 summary; Amendment 1 skips MT- genes (as ranking_v4b.py)."""
    tiers = {}
    for g in order3:
        if amendment1 and g.startswith("MT-"): continue
        tiers[g] = (tier3[g], float(f"{v2score(genes3[g])}"))
    ph = {g: pheno(g) for g in tiers}
    v4 = sorted(tiers, key=lambda g: ({"A": 0, "B": 1, "C": 2}[tiers[g][0]], -ph.get(g, 0), -tiers[g][1], g))
    return v4, tiers, ph

def v4_summary_lines(tiers, ph):
    v4 = sorted(tiers, key=lambda g: ({"A": 0, "B": 1, "C": 2}[tiers[g][0]], -ph.get(g, 0), -tiers[g][1], g))
    p0 = sorted(tiers, key=lambda g: ({"A": 0, "B": 1, "C": 2}[tiers[g][0]], -tiers[g][1], g))
    ponly = sorted(tiers, key=lambda g: (-ph.get(g, 0), -tiers[g][1], g))
    def rk(lst, g): return lst.index(g) + 1 if g in lst else "NA"
    out = ["gene\ttier\tpheno_score\tv2score\trank_v4\trank_P0\trank_Ponly\n"]
    for g in v4:
        out.append(f"{g}\t{tiers[g][0]}\t{ph.get(g,0)}\t{tiers[g][1]}\t{rk(v4,g)}\t{rk(p0,g)}\t{rk(ponly,g)}\n")
    return out

# ---------- ROW-MAP (draft rule, TRACK1_METHODS_ADDITIONS.md section 7) ----------
LOFW = {"nonsense": 3, "frameshift": 3, "splice_region": 2}
def row_map(calls):
    """1 call -> single; 2 -> pair; >2 -> highest-weight LoF-type call (ties lowest position) + lowest-position missense.
    Fill-in for cases the draft does not cover (>2 calls with no LoF-type or no missense call): the first two calls by
    (-v2 weight, position). Logged in the pre-registration."""
    if len(calls) <= 2: return [key(c) for c in calls]
    lof = sorted([c for c in calls if c[12] in LOFW], key=lambda c: (-LOFW[c[12]], int(c[1])))
    mis = sorted([c for c in calls if c[12] == "missense"], key=lambda c: int(c[1]))
    if lof and mis: return [key(lof[0]), key(mis[0])]
    s = sorted(calls, key=lambda c: (-WT[c[12]], int(c[1])))
    return [key(s[0]), key(s[1])]

# ---------- scorer (re-implemented from SPACE_RULES_T1.md; unverified against evaluation.py) ----------
def rank_points(r):
    return 100 if r == 1 else 50 if r <= 3 else 25 if r <= 5 else 10 if r <= 10 else 0
def score(rows, epcr, truth):
    """rows: list of variant-key lists in file order; epcr: values; truth: set of keys.
    Sort by EPCR descending, ties keep file order (stable). Rank points: max over rows of full points (row set == truth)
    or half points (row shares >=1 variant with truth). F-max over every distinct EPCR threshold, variant level."""
    idx = sorted(range(len(rows)), key=lambda i: -epcr[i])
    pts = 0.0
    for r, i in enumerate(idx, 1):
        s = set(rows[i])
        if s == truth: pts = max(pts, rank_points(r))
        elif s & truth: pts = max(pts, rank_points(r) / 2)
    fmax = 0.0
    for t in sorted(set(epcr), reverse=True):
        pred = set()
        for i in range(len(rows)):
            if epcr[i] >= t: pred |= set(rows[i])
        tp = len(pred & truth)
        if tp == 0: continue
        p, rc = tp / len(pred), tp / len(truth)
        fmax = max(fmax, 2 * p * rc / (p + rc))
    return pts, fmax
