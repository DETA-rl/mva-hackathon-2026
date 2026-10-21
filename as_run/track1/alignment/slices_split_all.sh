#!/usr/bin/env bash
# Split the full-genome BAM into one BAM per contig that has mapped reads. Runs inside the Parabricks image.
set -euo pipefail
S=$SLICES; BAM=$BAM_IN
samtools idxstats $BAM > $S/idxstats.tsv
awk '$1!="*" && $3>0 {print $1}' $S/idxstats.tsv > $S/contigs.txt
while read c; do
  samtools view -b -o $S/$c.bam $BAM $c
  samtools index $S/$c.bam
done < $S/contigs.txt
echo SPLIT_DONE
