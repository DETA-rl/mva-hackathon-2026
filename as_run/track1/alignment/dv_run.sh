#!/usr/bin/env bash
# DeepVariant (standard, Parabricks 4.7.1-1) on each primary chromosome slice, GPU1 only.
# Checkpointed: a chromosome with a done marker is skipped. Watchdog kills only this run's container if system RAM passes RAM_KILL.
set -uo pipefail
B=/media/[redacted]/[redacted]/hackaton_offload
S=$B/slices
O=$B/dv_primary
PT=$HOME/Documents/HACKATON/rental/pretest
REF=GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna
IMG=nvcr.io/nvidia/clara/clara-parabricks:4.7.1-1
RAM_KILL=42000
mkdir -p $O/done $O/logs $O/out
CHRS="chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22 chrX chrY chrM"

for c in $CHRS; do
  if [ -f $O/done/$c.done ]; then echo "skip $c (done)" >> $O/logs/summary.txt; continue; fi
  L=$O/logs/$c; mkdir -p $L
  (
    echo "t,gpu_util,gpu_mem_mib,gpu_power_w,cpu_busy_pct,ram_used_mib"
    prev=$(awk '/^cpu /{print $2+$3+$4+$5+$6+$7+$8, $5+$6}' /proc/stat)
    while true; do
      sleep 2
      g=$(nvidia-smi -i 1 --query-gpu=utilization.gpu,memory.used,power.draw --format=csv,noheader,nounits | tr -d ' ')
      cur=$(awk '/^cpu /{print $2+$3+$4+$5+$6+$7+$8, $5+$6}' /proc/stat)
      busy=$(echo "$prev $cur" | awk '{t=$3-$1; i=$4-$2; printf "%.1f", (t>0)?100*(t-i)/t:0}')
      prev=$cur
      ram=$(free -m | awk '/^Mem:/{print $3}')
      echo "$(date +%s),$g,$busy,$ram"
      if [ "$ram" -gt "$RAM_KILL" ]; then
        echo "$(date +%s) WATCHDOG ram=$ram > $RAM_KILL, killing dvp_$c" >> $L/watchdog.txt
        sudo docker kill dvp_$c >/dev/null 2>&1
      fi
    done
  ) > $L/samples.csv &
  SPID=$!
  T0=$(date +%s)
  sudo docker run --rm --name dvp_$c --gpus device=1 -u $(id -u):$(id -g) \
    -v $PT:$PT -v $B:$B -w $O $IMG \
    pbrun deepvariant --ref $PT/ref/$REF --in-bam $S/$c.bam \
    --out-variants $O/out/$c.vcf.gz --num-gpus 1 --tmp-dir $O/out > $L/pbrun.log 2>&1
  RC=$?
  T1=$(date +%s)
  kill $SPID 2>/dev/null; wait $SPID 2>/dev/null
  echo "$c exit=$RC wall_s=$((T1-T0))" >> $O/logs/summary.txt
  if [ $RC -eq 0 ] && [ -s $O/out/$c.vcf.gz ]; then touch $O/done/$c.done; fi
done
echo ALL_DONE >> $O/logs/summary.txt
