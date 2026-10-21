#!/usr/bin/env bash
# Fallback for primary chromosomes that have no done marker after the main run.
# Splits ONLY those chromosomes into fixed windows (--interval), checkpoints each window,
# then concatenates the window VCFs into one VCF per chromosome. Never used for chromosomes that already fit.
set -uo pipefail
B=/media/[redacted]/[redacted]/hackaton_offload
S=$B/slices
O=$B/dv_primary
PT=$HOME/Documents/HACKATON/rental/pretest
REF=GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna
IMG=nvcr.io/nvidia/clara/clara-parabricks:4.7.1-1
WIN=30000000
mkdir -p $O/parts $O/logs_split
for c in "$@"; do
  [ -f $O/done/$c.done ] && { echo "skip $c" >> $O/logs_split/summary.txt; continue; }
  len=$(awk -F"\t" -v c="$c" '$1==c{print $2}' $PT/ref/$REF.fai)
  parts=""
  for ((s=1; s<=len; s+=WIN)); do
    e=$((s+WIN-1)); [ $e -gt $len ] && e=$len
    p=$O/parts/$c.$s-$e
    parts="$parts $p.vcf.gz"
    if [ -f $p.done ]; then continue; fi
    sudo docker run --rm --gpus device=1 -u $(id -u):$(id -g) -v $PT:$PT -v $B:$B -w $O $IMG \
      pbrun deepvariant --ref $PT/ref/$REF --in-bam $S/$c.bam --interval $c:$s-$e \
      --out-variants $p.vcf.gz --num-gpus 1 --tmp-dir $O/parts > $p.log 2>&1
    rc=$?
    echo "$c:$s-$e exit=$rc" >> $O/logs_split/summary.txt
    if [ $rc -eq 0 ] && [ -s $p.vcf.gz ]; then touch $p.done; else echo "FAILED $c:$s-$e" >> $O/logs_split/summary.txt; continue 2; fi
  done
  # Concatenate parts in coordinate order: header from the first part, records from all parts.
  out=$O/out/$c.vcf.gz
  sudo docker run --rm -u $(id -u):$(id -g) -v $B:$B -w $O $IMG \
    bcftools concat -a -Oz -o $out.tmp $parts && mv $out.tmp $out
  sudo docker run --rm -u $(id -u):$(id -g) -v $B:$B -w $O $IMG \
    bcftools index -t -f $out
  if [ -s $out ]; then touch $O/done/$c.done; echo "merged $c" >> $O/logs_split/summary.txt; fi
done
echo SPLIT_ALL_DONE >> $O/logs_split/summary.txt
