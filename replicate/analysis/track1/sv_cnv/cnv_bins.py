# CNV rule v1 (amended). Per-chromosome 1 Mb bin counts and GC. Read-only. One chromosome per process.
import pysam, sys, os
BAM = os.environ["REPL_BAM"]
FA = os.environ["REPL_FASTA"]
OUTD = os.environ["REPL_OUT"] + "/"
os.makedirs(OUTD, exist_ok=True)
chroms = sys.argv[1:]
f = pysam.AlignmentFile(BAM, "rb")
fa = pysam.FastaFile(FA)
lens = dict(zip(f.references, f.lengths))
for c in chroms:
    L = lens[c]
    with open(OUTD + c + ".tsv", "w") as out:
        out.write("chrom\tstart\tend\tcount\tgc\tn_frac\n")
        for s in range(0, L, 1_000_000):
            e = min(L, s + 1_000_000)
            seq = fa.fetch(c, s, e).upper()
            n = seq.count("N"); ln = len(seq)
            gc = (seq.count("G") + seq.count("C")) / max(ln - n, 1)
            cnt = f.count(c, s, e)
            out.write(f"{c}\t{s}\t{e}\t{cnt}\t{gc:.4f}\t{n/ln:.4f}\n")
    print("done", c, flush=True)
