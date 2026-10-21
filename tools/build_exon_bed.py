"""Build the protein-coding exon BED that BLIND-01A reads (input 'exon_bed'), from the public GENCODE v44 GTF.

Usage:
  python tools/build_exon_bed.py --gtf gencode.v44.basic.annotation.gtf.gz --out protein_coding_exons_hg38.bed

Source: GENCODE release 44, gencode.v44.basic.annotation.gtf.gz (sha256 3e52f82c...; URL in
replicate/expected.yaml, input 'gtf'). One output line per GTF line with feature 'exon' whose attribute field
contains gene_type "protein_coding", in GTF order, duplicates kept:
  chrom without the 'chr' prefix (the organiser VCF has no prefix), start - 1, end, gene_name   (tab-separated)
The command that built the file used in the analysis was not recorded. This script was written afterwards
(2026-10-20) and its output is byte-identical to that file (710,377 lines, sha256 ebf3cbfc14232f34...), so
`./replicate.sh check` reports the input as matching. Equivalent one-liner:
  zcat GTF | awk -F'\\t' '$3=="exon" && $9 ~ /gene_type "protein_coding"/ {match($9,/gene_name "[^"]+"/);
    g=substr($9,RSTART+11,RLENGTH-12); c=$1; sub(/^chr/,"",c); print c"\\t"$4-1"\\t"$5"\\t"g}' > BED
"""
import argparse
import gzip
import hashlib
import re

EXPECTED_SHA256 = "ebf3cbfc14232f34e79940a7eb5f019e4f56c54d899b44229e748398dc1e0415"
GENE_NAME = re.compile(r'gene_name "([^"]+)"')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--gtf", required=True, help="gencode.v44.basic.annotation.gtf.gz")
    ap.add_argument("--out", required=True, help="output BED (for example $MVA_REF/protein_coding_exons_hg38.bed)")
    a = ap.parse_args()
    h = hashlib.sha256()
    n = 0
    with gzip.open(a.gtf, "rt") as fh, open(a.out, "w") as out:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) < 9 or f[2] != "exon" or 'gene_type "protein_coding"' not in f[8]:
                continue
            m = GENE_NAME.search(f[8])
            chrom = f[0][3:] if f[0].startswith("chr") else f[0]
            row = f"{chrom}\t{int(f[3]) - 1}\t{f[4]}\t{m.group(1) if m else ''}\n"
            out.write(row)
            h.update(row.encode())
            n += 1
    got = h.hexdigest()
    print(f"{n} exon lines written to {a.out}; sha256 {got}")
    print("matches the file used in the analysis" if got == EXPECTED_SHA256 else
          f"DIFFERS from the file used in the analysis ({EXPECTED_SHA256}): check the GTF release")


if __name__ == "__main__":
    main()
