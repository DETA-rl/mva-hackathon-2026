"""PRE-REG-D: place BUB1B I909T, L1012P and the candidate missense (from T1-CANDIDATE) among the calibration controls (ESM-1v, ESM-2, AlphaMissense).
Run inside protein_rule/ (uses controls/, the ESM model folders, alphamissense/, scores.tsv for the control scores).
"""
import csv
import gzip
import sys

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

BASE = __import__("os").environ["REPL_OUT"] + "/"
MODELS = {"esm1v": BASE + "esm1v_t33_650M_UR90S_1", "esm2": BASE + "esm2_t33_650M_UR50D"}
WIN = 1022
DEV = "cuda"

seq = "".join(l.strip() for l in open(BASE + "controls/BUB1B.fasta") if not l.startswith(">"))
ALLELES = [("I909T", 909, "I", "T"), ("L1012P", 1012, "L", "P")] + [tuple(a) for a in __import__("json").loads(__import__("os").environ["REPL_CANDIDATE_ALLELES"])]
for name, pos, ref, alt in ALLELES:
    assert seq[pos - 1] == ref, (name, seq[pos - 1])
print("residue checks passed:", [a[0] for a in ALLELES])


def llr(tok, model, pos, ref, alt):
    i = pos - 1
    start = max(0, min(i - WIN // 2, len(seq) - WIN))
    win = seq[start:start + WIN]
    chars = list(win)
    chars[i - start] = tok.mask_token
    enc = tok("".join(chars), return_tensors="pt")
    idx = (enc["input_ids"][0] == tok.mask_token_id).nonzero().item()
    with torch.no_grad():
        logits = model(**{k: v.to(DEV) for k, v in enc.items()}).logits[0, idx]
    lp = torch.log_softmax(logits.float(), dim=-1)
    return (lp[tok.convert_tokens_to_ids(alt)] - lp[tok.convert_tokens_to_ids(ref)]).item()


# control scores from the pre-registered calibration run
ctrl = {"esm1v": [], "esm2": [], "am": []}
for r in csv.DictReader(open(BASE + "scores.tsv"), delimiter="\t"):
    if r["label"] not in ("0", "1"):
        continue
    if r["esm1v_llr"] not in ("", "None"):
        ctrl["esm1v"].append(-float(r["esm1v_llr"]))
    if r["esm2_llr"] not in ("", "None"):
        ctrl["esm2"].append(-float(r["esm2_llr"]))
    if r["am"] not in ("", "None"):
        ctrl["am"].append(float(r["am"]))

# AlphaMissense: lookup by UniProt protein_variant string
am_scores = {}
with gzip.open(BASE + "alphamissense/AlphaMissense_hg38.tsv.gz", "rt") as fh:
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) < 9 or p[5] != "O60566":
            continue
        if p[7] in tuple(a[0] for a in ALLELES):
            am_scores[p[7]] = float(p[8])
print("AlphaMissense matches:", am_scores)

results = {a[0]: {} for a in ALLELES}
for name, model_path in MODELS.items():
    tok = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForMaskedLM.from_pretrained(model_path).to(DEV).eval()
    for an, pos, ref, alt in ALLELES:
        results[an][name] = llr(tok, model, pos, ref, alt)
    del model
    torch.cuda.empty_cache()

for an, pos, ref, alt in ALLELES:
    row = [f"{an}"]
    for name in ["esm1v", "esm2"]:
        damage = -results[an][name]
        pct = sum(1 for v in ctrl[name] if v <= damage) / len(ctrl[name]) * 100
        row.append(f"{name} damage={damage:+.3f} pct={pct:.1f}")
    if an in am_scores:
        pct = sum(1 for v in ctrl["am"] if v <= am_scores[an]) / len(ctrl["am"]) * 100
        row.append(f"am={am_scores[an]:.3f} pct={pct:.1f}")
    else:
        row.append("am=not_matched")
    print(" | ".join(row))
print("control counts:", {k: len(v) for k, v in ctrl.items()})
