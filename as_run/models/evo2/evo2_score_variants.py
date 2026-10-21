#!/usr/bin/env python3
"""Zero-shot Evo 2 likelihood scoring of SNVs on a GRCh38 window.

For each variant, takes a window centred on the position, builds the reference
and alternate sequences from the FASTA, and returns the summed per-nucleotide
log-likelihood of each. delta = ll_alt - ll_ref (negative = alt less likely
under the model than ref).

Input TSV columns (header required): id, chrom, pos, ref, alt, label
  pos is 1-based GRCh38. chrom as in the FASTA (e.g. chr11 or 11).
Output TSV: one row per variant with ll_ref, ll_alt, delta, ref check status.
"""
import argparse
import csv
import os
import time

import torch

from evo2 import Evo2


def load_fai(fai_path):
    idx = {}
    with open(fai_path) as fh:
        for line in fh:
            name, length, offset, linebases, linewidth = line.rstrip("\n").split("\t")[:5]
            idx[name] = (int(length), int(offset), int(linebases), int(linewidth))
    return idx


def fetch(fasta_fh, idx, chrom, start0, end0):
    """Return uppercase sequence for [start0, end0) (0-based, half-open)."""
    length, offset, linebases, linewidth = idx[chrom]
    if start0 < 0 or end0 > length:
        raise ValueError(f"window {chrom}:{start0}-{end0} outside contig length {length}")
    byte_start = offset + (start0 // linebases) * linewidth + (start0 % linebases)
    n_bases = end0 - start0
    n_lines = (start0 % linebases + n_bases - 1) // linebases + 1
    fasta_fh.seek(byte_start)
    raw = fasta_fh.read(n_bases + n_lines * (linewidth - linebases) + 2 * n_lines)
    seq = raw.replace("\n", "").replace("\r", "")[:n_bases]
    return seq.upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--fasta", required=True)
    ap.add_argument("--fai", default=None)
    ap.add_argument("--weights", required=True, help="path to evo2_7b.pt")
    ap.add_argument("--model-name", default="evo2_7b")
    ap.add_argument("--half-window", type=int, default=1024)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rc-average", action="store_true",
                    help="also score reverse complements and average (2x cost)")
    args = ap.parse_args()

    fai_path = args.fai or args.fasta + ".fai"
    idx = load_fai(fai_path)

    with open(args.variants) as fh:
        variants = list(csv.DictReader(fh, delimiter="\t"))

    t0 = time.time()
    model = Evo2(args.model_name, local_path=args.weights)
    load_s = time.time() - t0
    print(f"model loaded in {load_s:.1f}s; "
          f"peak alloc {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB", flush=True)

    rows = []
    with open(args.fasta, "r") as fasta_fh:
        for v in variants:
            chrom = v["chrom"]
            pos = int(v["pos"])
            hw = args.half_window
            start0 = pos - 1 - hw
            end0 = pos - 1 + hw + 1
            ref_seq = fetch(fasta_fh, idx, chrom, start0, end0)
            centre = hw
            ref_base = ref_seq[centre]
            status = "ok" if ref_base == v["ref"].upper() else f"REF_MISMATCH(genome={ref_base})"
            if status != "ok":
                print(f"WARNING {v['id']}: {status}", flush=True)
            alt_seq = ref_seq[:centre] + v["alt"].upper() + ref_seq[centre + 1:]

            seqs = [ref_seq, alt_seq]
            if args.rc_average:
                seqs += [rc(ref_seq), rc(alt_seq)]
            t1 = time.time()
            ll = model.score_sequences(seqs, batch_size=len(seqs), reduce_method="sum")
            if args.rc_average:
                ll_ref = (ll[0] + ll[2]) / 2
                ll_alt = (ll[1] + ll[3]) / 2
            else:
                ll_ref, ll_alt = ll[0], ll[1]
            rows.append({
                "id": v["id"], "label": v.get("label", ""), "chrom": chrom, "pos": pos,
                "ref": v["ref"], "alt": v["alt"], "ref_check": status,
                "window_bp": len(ref_seq), "ll_ref": round(ll_ref, 4),
                "ll_alt": round(ll_alt, 4), "delta": round(ll_alt - ll_ref, 4),
                "score_s": round(time.time() - t1, 2),
            })
            print(f"{v['id']} {v.get('label','')}: delta={rows[-1]['delta']}", flush=True)

    peak = torch.cuda.max_memory_allocated() / 2**30
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"peak GPU alloc {peak:.2f} GiB; wrote {args.out}", flush=True)


_COMP = str.maketrans("ACGTN", "TGCAN")


def rc(s):
    return s.translate(_COMP)[::-1]


if __name__ == "__main__":
    main()
