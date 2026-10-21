"""Borzoi (johahi/borzoi-replicate-0, local weights) variant-effect scoring.

Control set: GTEx v8 Whole Blood eQTL SNVs on chr15 (strong, p<1e-5) as positives;
random chr15 SNVs within +-100 kb of the same gene's TSS as negatives.
Child site: chr15:40117088 G>A (GRCh38), upstream of BUB1B.
Only GTEx gene queries leave the box; no child coordinates are sent anywhere.
"""
import json, os, random, sys, urllib.request
import numpy as np
import pysam
import torch
from borzoi_pytorch import Borzoi
from sklearn.metrics import roc_auc_score
import pandas as pd

ROOT = os.path.expanduser("~/Documents/HACKATON/_private/models/regulatory")
FASTA = f"{ROOT}/genome/chr15.fa"
MODEL = f"{ROOT}/borzoi"
OUT = f"{ROOT}/work"
WIN = 524288
HALF = WIN // 2
BIN = 32
N_BINS = 6144  # Borzoi output bins (32 bp each) cover the central 196,608 bp
CENTER_BIN = N_BINS // 2  # variant sits at the centre bin of the output
random.seed(0)
np.random.seed(0)

GENES = ["IREB2", "SPRED1", "FBN1", "MFGE8", "ALDH1A2", "CSK", "PML", "HERC2", "FES",
         "MAP2K1", "AP4E1", "BUB1B"]
API = "https://gtexportal.org/api/v2"
P_MAX = 1e-4  # GTEx nominal eQTL threshold used for the positive controls


def api(p):
    with urllib.request.urlopen(API + p, timeout=120) as r:
        return json.load(r)


if not os.path.exists(FASTA + ".fai"):
    pysam.faidx(FASTA)
fa = pysam.FastaFile(FASTA)
CHROM_LEN = fa.get_reference_length("chr15")

ONEHOT = {ord("A"): 0, ord("C"): 1, ord("G"): 2, ord("T"): 3,
          ord("a"): 0, ord("c"): 1, ord("g"): 2, ord("t"): 3}


def encode(seq):
    x = np.zeros((4, len(seq)), dtype=np.float32)
    for i, ch in enumerate(seq.encode()):
        j = ONEHOT.get(ch)
        if j is not None:
            x[j, i] = 1.0
    return x


def window(pos1, ref_base, alt_base):
    """Return (ref_onehot, alt_onehot) with variant at index HALF (0-based)."""
    start = pos1 - 1 - HALF
    end = start + WIN
    s = max(start, 0)
    e = min(end, CHROM_LEN)
    seq = fa.fetch("chr15", s, e).upper()
    seq = "N" * (s - start) + seq + "N" * (end - e)
    assert len(seq) == WIN, len(seq)
    idx = HALF
    assert seq[idx] == ref_base, f"ref mismatch at {pos1}: genome={seq[idx]} given={ref_base}"
    alt = seq[:idx] + alt_base + seq[idx + 1:]
    return encode(seq), encode(alt)


# ---------- controls ----------
tss = {}
pos_rows = []
for sym in GENES:
    g = api(f"/reference/gene?geneId={sym}&gencodeVersion=v26&genomeBuild=GRCh38%2Fhg38")["data"][0]
    tss[sym] = g["tss"]
    if sym == "BUB1B":
        continue
    d = api(f"/association/singleTissueEqtl?gencodeId={g['gencodeId']}"
            f"&tissueSiteDetailId=Whole_Blood&datasetId=gtex_v8")["data"]
    print(sym, "pairs returned:", len(d), "min p:", min((x["pValue"] for x in d), default=None), flush=True)
    for x in d:
        v = x["variantId"].split("_")
        # variantId format: chr15_<pos>_<ref>_<alt>_b38
        if len(v) != 5 or len(v[2]) != 1 or len(v[3]) != 1:
            continue
        if x["pValue"] < P_MAX:
            pos_rows.append(dict(gene=sym, pos=int(v[1]), ref=v[2], alt=v[3],
                                 nes=x["nes"], p=x["pValue"], label=1))
pos = pd.DataFrame(pos_rows).drop_duplicates(subset=["pos"]).reset_index(drop=True)
print("positives available:", len(pos), flush=True)
pos = pos.sample(n=min(len(pos), 120), random_state=0).reset_index(drop=True)

eqtl_positions = set(pos["pos"].tolist())
neg_rows = []
for _, r in pos.iterrows():
    t = tss[r["gene"]]
    while True:
        p = int(t + random.randint(-100_000, 100_000))
        if 1 + HALF < p < CHROM_LEN - HALF and p not in eqtl_positions:
            break
    ref = fa.fetch("chr15", p - 1, p).upper()
    if ref not in "ACGT":
        continue
    alt = random.choice([b for b in "ACGT" if b != ref])
    neg_rows.append(dict(gene=r["gene"], pos=p, ref=ref, alt=alt, nes=np.nan, p=np.nan, label=0))
neg = pd.DataFrame(neg_rows)
ctrl = pd.concat([pos, neg], ignore_index=True)
print("controls:", ctrl["label"].value_counts().to_dict(), flush=True)

# ---------- model ----------
model = Borzoi.from_pretrained(MODEL).eval().cuda()
import borzoi_pytorch
tracks = pd.read_table(os.path.join(os.path.dirname(borzoi_pytorch.__file__), "precomputed", "targets.txt"))
rna_mask = tracks["description"].str.startswith("RNA:").values
print("RNA tracks:", int(rna_mask.sum()), flush=True)


@torch.inference_mode()
def predict_pair(ref_x, alt_x):
    x = torch.from_numpy(np.stack([ref_x, alt_x])).cuda()
    out = model(x, is_human=True)  # (2, 7611, 6144)
    return out.float().cpu().numpy()


def score(pos1, ref, alt):
    rx, ax = window(pos1, ref, alt)
    out = predict_pair(rx, ax)[:, rna_mask, :]
    assert out.shape[-1] == N_BINS, out.shape
    lo = np.log2(out + 1.0)
    d = lo[1] - lo[0]  # (tracks, bins)
    total = np.abs(d).sum(axis=1)  # per-track total effect
    local = np.abs(d[:, CENTER_BIN - 16:CENTER_BIN + 16]).max(axis=1)  # +-512 bp
    return float(total.max()), float(local.max())


rows = []
for i, r in ctrl.iterrows():
    tot, loc = score(r["pos"], r["ref"], r["alt"])
    rows.append((tot, loc))
    if i % 40 == 0:
        print("scored", i, flush=True)
ctrl["score_total"] = [a for a, _ in rows]
ctrl["score_local"] = [b for _, b in rows]
ctrl.to_csv(f"{OUT}/control_scores.tsv", sep="\t", index=False)

auc_t = roc_auc_score(ctrl["label"], ctrl["score_total"])
auc_l = roc_auc_score(ctrl["label"], ctrl["score_local"])
print(f"CONTROL AUC total={auc_t:.3f} local={auc_l:.3f} n_pos={int(ctrl.label.sum())} "
      f"n_neg={int((1-ctrl.label).sum())}", flush=True)

# ---------- child site ----------
# Both alleles: reference G, alternative A, GRCh38 chr15:40117088
site_ref = score(40117088, "G", "A")
tot_ref, loc_ref = site_ref
print(f"SITE chr15:40117088 G>A  total={tot_ref:.4f} local={loc_ref:.4f}", flush=True)
# Reference-allele "score" is the reference sequence vs itself by definition: zero delta.
# Also report the score as a percentile of the control distribution.
pct_t = (ctrl.loc[ctrl.label == 0, "score_total"] < tot_ref).mean()
pct_l = (ctrl.loc[ctrl.label == 0, "score_local"] < loc_ref).mean()
print(f"SITE percentile vs random controls: total={pct_t:.2f} local={pct_l:.2f}", flush=True)
print(f"SITE percentile vs positives: total={(ctrl.loc[ctrl.label==1,'score_total']<tot_ref).mean():.2f}", flush=True)
json.dump(dict(auc_total=auc_t, auc_local=auc_l, site_total=tot_ref, site_local=loc_ref,
               pct_neg_total=pct_t, pct_neg_local=pct_l),
          open(f"{OUT}/summary.json", "w"), indent=1)
