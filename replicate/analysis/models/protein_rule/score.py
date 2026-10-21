"""Score ClinVar controls + the candidate missense (from T1-CANDIDATE) with local protein LMs and AlphaMissense lookup.

Masked-marginal LLR: score = log p(alt | context) - log p(ref | context) at the mutated
position, context = the wild-type sequence with that one position masked. Lower LLR
(more negative) = predicted more damaging. AUC is computed with pathogenicity = -LLR.
Runs only on local weights. No network calls.
Usage: CUDA_VISIBLE_DEVICES=1 python score.py <protein_dir>
"""
import csv
import gzip
import math
import sys
from pathlib import Path

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

BASE = Path(sys.argv[1])
CTRL = BASE / "controls"
WIN = 1022  # ESM max residues per pass
DEV = "cuda"

MODELS = {
    "esm1v": BASE / "esm1v_t33_650M_UR90S_1",
    "esm2": BASE / "esm2_t33_650M_UR50D",
}

GENE_FASTA = {}


def read_fasta(path):
    return "".join(l.strip() for l in open(path) if not l.startswith(">"))


# child variant (local input, never sent anywhere)
CHILD = dict(__import__("json").loads(__import__("os").environ["REPL_CHILD_PROTEIN_VARIANT"]),
             review="child")

rows = list(csv.DictReader(open(CTRL / "controls.tsv"), delimiter="\t"))
rows.append(CHILD)

for r in rows:
    if r["gene"] not in GENE_FASTA:
        GENE_FASTA[r["gene"]] = read_fasta(CTRL / f"{r['gene']}.fasta")
    r["pos"] = int(r["pos"])
    r["label"] = r["label"]
    assert GENE_FASTA[r["gene"]][r["pos"] - 1] == r["ref"], (r["gene"], r["pos"], r["ref"])


def llr_for_model(tok, model, seq, pos, ref, alt):
    """Masked-marginal LLR, residue window of up to 1022 centred on pos (1-based)."""
    i = pos - 1
    start = max(0, min(i - WIN // 2, len(seq) - WIN))
    win = seq[start:start + WIN]
    j = i - start
    chars = list(win)
    chars[j] = tok.mask_token
    enc = tok("".join(chars), return_tensors="pt")
    # tokenizer may split mask token; find position of the mask token id
    mask_id = tok.mask_token_id
    idx = (enc["input_ids"][0] == mask_id).nonzero().item()
    with torch.no_grad():
        logits = model(**{k: v.to(DEV) for k, v in enc.items()}).logits[0, idx]
    lp = torch.log_softmax(logits.float(), dim=-1)
    return (lp[tok.convert_tokens_to_ids(alt)] - lp[tok.convert_tokens_to_ids(ref)]).item()


scores = {r["gene"] + str(r["pos"]) + r["alt"] + r["vcf_pos"]: {} for r in rows}
for name, path in MODELS.items():
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForMaskedLM.from_pretrained(path).to(DEV).eval()
    for r in rows:
        key = r["gene"] + str(r["pos"]) + r["alt"] + r["vcf_pos"]
        seq = GENE_FASTA[r["gene"]]
        scores[key][name] = llr_for_model(tok, model, seq, r["pos"], r["ref"], r["alt"])
    print("done", name, flush=True)
    del model
    torch.cuda.empty_cache()

# AlphaMissense precomputed table (local file, CC BY 4.0). Lookup only.
def norm_chrom(c):
    return c[3:] if c.startswith("chr") else c


want = {(r["chrom"], r["vcf_pos"], r["vcf_ref"], r["vcf_alt"]): None for r in rows}
with gzip.open(BASE / "alphamissense" / "AlphaMissense_hg38.tsv.gz", "rt") as fh:
    # no header line in this file; documented columns: CHROM POS REF ALT genome uniprot_id
    # transcript_id protein_variant am_pathogenicity am_class
    ci = 8
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) < 9:
            continue
        k = (norm_chrom(p[0]), p[1], p[2], p[3])
        if k in want:
            want[k] = float(p[ci])
for r in rows:
    key = r["gene"] + str(r["pos"]) + r["alt"] + r["vcf_pos"]
    scores[key]["am"] = want[(norm_chrom(r["chrom"]), r["vcf_pos"], r["vcf_ref"], r["vcf_alt"])]
print("AM matched", sum(1 for r in rows if scores[r["gene"] + str(r["pos"]) + r["alt"] + r["vcf_pos"]]["am"] is not None), "of", len(rows))

# write table
with open(BASE / "scores.tsv", "w") as fh:
    fh.write("gene\tpos\tref\talt\tlabel\tvcf_pos\tesm1v_llr\tesm2_llr\tam\n")
    for r in rows:
        key = r["gene"] + str(r["pos"]) + r["alt"] + r["vcf_pos"]
        s = scores[key]
        fh.write(f"{r['gene']}\t{r['pos']}\t{r['ref']}\t{r['alt']}\t{r['label']}\t{r['vcf_pos']}\t"
                 f"{s['esm1v']:.4f}\t{s['esm2']:.4f}\t{s['am'] if s['am'] is None else round(s['am'], 4)}\n")


def auc(pos_scores, neg_scores):
    """Mann-Whitney AUC, higher score = more pathogenic."""
    wins = 0.0
    for p in pos_scores:
        for n in neg_scores:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos_scores) * len(neg_scores))


def key_of(r):
    return r["gene"] + str(r["pos"]) + r["alt"] + r["vcf_pos"]


# damage score: higher = more pathogenic. ESM LLR is negated; AlphaMissense is already damage-oriented.
def damage(name, r):
    v = scores[key_of(r)][name]
    if v is None:
        return None
    return v if name == "am" else -v


ctrl = [r for r in rows if r["label"] != "NA"]
child = [r for r in rows if r["label"] == "NA"][0]
for name in ["esm1v", "esm2", "am"]:
    pos = [damage(name, r) for r in ctrl if r["label"] == "1"]
    neg = [damage(name, r) for r in ctrl if r["label"] == "0"]
    pos = [v for v in pos if v is not None]
    neg = [v for v in neg if v is not None]
    print(f"{name}: AUC={auc(pos, neg):.3f} n_P={len(pos)} n_B={len(neg)}")

    cv = damage(name, child)
    if cv is None:
        print(f"candidate_missense {name}: not in table")
        continue
    allv = [damage(name, r) for r in ctrl]
    allv = [v for v in allv if v is not None]
    pct = sum(1 for v in allv if v <= cv) / len(allv)
    print(f"candidate_missense {name}: damage={cv:.4f} percentile_among_controls={pct:.3f} n_controls={len(allv)}")
