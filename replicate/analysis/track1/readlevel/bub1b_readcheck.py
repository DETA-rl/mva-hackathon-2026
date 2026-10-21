# Read-level check of the two BUB1B calls on the child's alignment. Read-only; derived output to project folder.
import pysam, collections, json, os
BAM = os.environ["REPL_BAM"]
OUT = os.environ["REPL_OUT"] + "/bub1b_readcheck.json"
sites = [tuple(s) for s in json.loads(os.environ["REPL_CANDIDATE_SITES"])]
f = pysam.AlignmentFile(BAM, "rb")
out = {}
for chrom, pos, ref, alt, label in sites:
    c = collections.Counter(); mq = []; strands = collections.Counter(); depth_all = 0
    for col in f.pileup(chrom, pos - 1, pos, truncate=True, min_base_quality=20, min_mapping_quality=0, stepper="nofilter"):
        for r in col.pileups:
            if r.is_del or r.is_refskip or r.alignment.is_duplicate or r.alignment.is_secondary:
                continue
            depth_all += 1
            b = r.alignment.query_sequence[r.query_position]
            c[b] += 1
            if b == alt:
                mq.append(r.alignment.mapping_quality)
                strands["rev" if r.alignment.is_reverse else "fwd"] += 1
    n = depth_all
    alt_n = c.get(alt, 0)
    out[label] = {"pos": pos, "depth": n, "ref_reads": c.get(ref, 0), "alt_reads": alt_n,
                  "alt_fraction": round(alt_n / n, 3) if n else None,
                  "alt_mapq_median": sorted(mq)[len(mq)//2] if mq else None,
                  "alt_strand": dict(strands)}
    print(label, out[label], flush=True)
json.dump(out, open(OUT, "w"), indent=1)
