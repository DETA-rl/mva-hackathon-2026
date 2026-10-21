#!/usr/bin/env bash
# Per-slice check inside the Parabricks image: index present and mapped-read count equals the input idxstats count.
set -uo pipefail
S=$SLICES
printf "contig\tindexed\texpected_mapped\tslice_mapped\tstatus\n" > $S/verify.tsv
while read c; do
  exp=$(awk -F"\t" -v c="$c" "\$1==c{print \$3}" $S/idxstats.tsv)
  if [ -f $S/$c.bam.bai ] || [ -f $S/$c.bai ]; then ix=yes; else ix=no; fi
  got=$(samtools idxstats $S/$c.bam 2>/dev/null | awk -F"\t" -v c="$c" "\$1==c{print \$3}")
  st=OK; [ "$ix" = yes ] && [ "$exp" = "$got" ] || st=FAIL
  printf "%s\t%s\t%s\t%s\t%s\n" "$c" "$ix" "$exp" "${got:-NA}" "$st" >> $S/verify.tsv
done < $S/contigs.txt
echo VERIFY_DONE
