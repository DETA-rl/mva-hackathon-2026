# D-RM-3: real rows under the adopted combination -> TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv (box only; current CSV untouched).
# Also POST HOC (not pre-registered): paired PRIM differences between near-tied combinations, same bootstrap as section 8.
import collections, csv, hashlib, importlib.util, json, os, sys
import numpy as np, pysam
R = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/rowmap/")
T1 = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/track1/")
VCF = os.path.expanduser("~/Documents/HACKATON/data/WGS_EX2312012_HGWCNDSX7.vcf.gz")
S = json.load(open(R + "summary_rowmap.json")); W = S["D_RM_1"]["winner"]; rn, cn = W.split("x")
assert S["D_RM_1"]["verdict"].startswith("adopt")
EPCR = [0.533223, 0.413611, 0.001641, 0.001631, 0.001621, 0.001611, 0.001601, 0.001591, 0.001581, 0.001571]
rows = [l.rstrip("\n").split("\t") for l in open(R + "real_rows.tsv")][1:]
rows = [r for r in rows if r[0] == rn and r[1] == cn]
cur = list(csv.DictReader(open(T1 + "TRACK1_SUBMISSION_FINAL_PROPOSED.csv")))
CLS = {}
for l in open(os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/child_exonic_consequence_fixed.tsv")):
    f = l.rstrip("\n").split("\t"); CLS.setdefault(":".join(f[:4]), f[12])
P = R + "TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv"
out = open(P, "w", newline="")
w = csv.writer(out, lineterminator="\n")
w.writerow(["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1", "chrom_2", "pos_2", "ref_2", "alt_2", "epcr", "finding_type", "notes"])
for i, r in enumerate(rows):
    vs = [v.split(":") for v in r[4].split(";")]
    if r[5] == "True":
        c = cur[i]
        w.writerow([c[k] for k in ("proband_id", "chrom_1", "pos_1", "ref_1", "alt_1", "chrom_2", "pos_2", "ref_2", "alt_2")]
                   + [EPCR[i], c["finding_type"], c["notes"]])
        continue
    cls = " + ".join(CLS[":".join(v)] for v in vs)
    tier = cur[i]["notes"].split("tier ")[1].split(";")[0]
    note = f"{r[3]}; rule v4 rank {i + 1}; tier {tier}; {cls} pair (ROW-MAP {rn})"
    v2 = ["chr" + vs[1][0], vs[1][1], vs[1][2], vs[1][3]] if len(vs) > 1 else ["", "", "", ""]
    w.writerow(["PROBAND01", "chr" + vs[0][0], vs[0][1], vs[0][2], vs[0][3]] + v2 + [EPCR[i], "primary", note])
out.close()
spec = importlib.util.spec_from_file_location("ev", T1 + "scorer_check/evaluation.py")
ev = importlib.util.module_from_spec(spec); sys.modules["ev"] = ev; spec.loader.exec_module(ev)
sub = ev.load_submission(P)["PROBAND01"]
vf = pysam.VariantFile(VCF); ok = []
for s in sub:
    for c, p, ref, alt in s.variants:
        ok.append(sum(1 for rec in vf.fetch(c.replace("chr", ""), p - 1, p)
                      if rec.pos == p and rec.ref == ref and alt in (rec.alts or ())) == 1)
r1 = ev.score_proband("PROBAND01", sub, sub[0].variants)
curs = ev.load_submission(T1 + "TRACK1_SUBMISSION_FINAL_PROPOSED.csv")["PROBAND01"]
diff = [i + 1 for i, (a, b) in enumerate(zip(sub, curs)) if a.variants != b.variants]
print("proposed sha256", hashlib.sha256(open(P, "rb").read()).hexdigest(), "rows", len(sub), "all_in_vcf", all(ok), len(ok),
      "epcr_strict", all(a.epcr > b.epcr for a, b in zip(sub, sub[1:])), "rows_differing_from_current", diff,
      "key=row1 points/fmax", r1.rank_points, r1.f_max, "row1_same", sub[0].variants == curs[0].variants)
prows = list(csv.DictReader(open(P)))
for i in diff: print("row", i, "notes:", prows[i - 1]["notes"])
# POST HOC near-tie comparisons, same stratified gene-cluster bootstrap (B = 10,000, default_rng(1))
tr = collections.defaultdict(dict); gene = {}
for l in open(R + "trials_rowmap.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] in ("A-CH-dec", "E-CH-dec", "A-hid-dec"):
        tr[(f[0], f[1])][f[10] + "x" + f[11]] = float(f[12]); gene[(f[0], f[1])] = f[2]
def pb(strata, a, b):
    rng = np.random.default_rng(1); parts = []
    for s in strata:
        ks = [k for k in tr if k[0] == s]; gs = sorted({gene[k] for k in ks}); gi = {g: i for i, g in enumerate(gs)}
        sm = np.zeros(len(gs)); ct = np.zeros(len(gs))
        for k in ks: sm[gi[gene[k]]] += tr[k][a] - tr[k][b]; ct[gi[gene[k]]] += 1
        parts.append((len(gs), sm, ct))
    est = sum(p[1].sum() for p in parts) / sum(p[2].sum() for p in parts); bs = []
    for _ in range(10000):
        t = n = 0.0
        for G, sm, ct in parts:
            wv = np.bincount(rng.integers(0, G, G), minlength=G); t += wv @ sm; n += wv @ ct
        bs.append(t / n)
    return round(est, 3), [round(x, 3) for x in np.percentile(bs, [2.5, 97.5])]
for a, b in (("P5xC3", "P2xC3"), ("P5xC3", "P3xC3"), ("P5xC3", "P1xC3"), ("P5xC3", "P5xC1"), ("P2xC1", "P1xC1")):
    print("POST HOC PRIM", a, "-", b, pb(["A-CH-dec", "E-CH-dec"], a, b))
print("POST HOC A-hid-dec P5xC3 - P5xC1", pb(["A-hid-dec"], "P5xC3", "P5xC1"))
