#!/usr/bin/env bash
# ALIGN-01: align the organisers' eight FASTQs (4 lanes x R1/R2) to GRCh38 with Parabricks 4.7.1 fq2bam, as we did.
# Parameterised copy of our launcher (held back: it has our local paths). Same container, same reference, same read
# groups (ID and PU = flowcell.lane, LB lib1, PL ILLUMINA) and the same fq2bam options. This copy has only been
# checked with `bash -n`; it has never been run. Full procedure: replicate/EXTERNAL_STEPS.md (ALIGN-01).
#
# Usage: tools/fq2bam.sh DATA_DIR REF_FASTA OUT_DIR [SAMPLE_LABEL] [GPU_INDEX]
#   DATA_DIR      folder with the dataset's FASTQs (*_L00{1..4}_R{1,2}_001.fastq.gz), e.g. $MVA_DATA
#   REF_FASTA     GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna, with its index files next to it, as we
#                 ran it: from the NCBI folder seqs_for_alignment_pipelines.ucsc_ids/ the .fna.gz (decompressed), the
#                 .fna.fai, and the prebuilt BWA index <fasta>.bwa_index.tar.gz extracted in place (.amb/.ann/.bwt/
#                 .pac/.sa); we did not build the BWA index ourselves
#   OUT_DIR       output folder: OUT_DIR/<SAMPLE_LABEL>.bam (+ .bai), OUT_DIR/dup_metrics.txt, OUT_DIR/tmp
#   SAMPLE_LABEL  read-group SM tag (default: sample). Ours was PROBAND01; pass it to get our read groups.
#   GPU_INDEX     one GPU (default 0). Our run used 13.7 to 14.0 GB of GPU memory (--low-memory) and took 82 min 6 s on
#                 one RTX 3090; its peak host RAM and temporary disk were not recorded.
# Needs Docker with the NVIDIA container toolkit (we ran `sudo docker`; set DOCKER="sudo docker" for that).
# A fresh alignment is not byte-identical to ours (the header records paths and the command line); the harness then
# reports BAM-derived counts as NOT COMPARABLE rather than PASS or FAIL. Then give OUT_DIR/<SAMPLE_LABEL>.bam as
# input 'bam' in config.yaml.
set -euo pipefail
DATA=$(cd "${1:?DATA_DIR}" && pwd); FASTA=$(readlink -f "${2:?REF_FASTA}"); OUT=$(mkdir -p "${3:?OUT_DIR}" && cd "$3" && pwd)
SAMPLE=${4:-sample}; GPU=${5:-0}; DOCKER=${DOCKER:-docker}
IMAGE=nvcr.io/nvidia/clara/clara-parabricks:4.7.1-1      # digest in env/containers.txt
REFDIR=$(dirname "$FASTA")
FQ=()
for L in 1 2 3 4; do
  R1=$(ls "$DATA"/*_L00${L}_R1_001.fastq.gz); R2=$(ls "$DATA"/*_L00${L}_R2_001.fastq.gz)
  [ "$(echo "$R1" | wc -l)" = 1 ] && [ "$(echo "$R2" | wc -l)" = 1 ] || { echo "expected one R1 and one R2 FASTQ for lane $L" >&2; exit 1; }
  FC=$(basename "$R1" | sed -E 's/^WGS_[^_]+_([^_]+)_.*$/\1/')   # flowcell, from the dataset's file names
  FQ+=(--in-fq "$R1" "$R2" "@RG\tID:${FC}.${L}\tLB:lib1\tPL:ILLUMINA\tSM:${SAMPLE}\tPU:${FC}.${L}")
done
mkdir -p "$OUT/tmp"
$DOCKER run --rm --gpus device="$GPU" -u "$(id -u):$(id -g)" -v "$DATA:$DATA:ro" -v "$REFDIR:$REFDIR:ro" -v "$OUT:$OUT" \
  -w "$OUT" "$IMAGE" \
  pbrun fq2bam --ref "$FASTA" "${FQ[@]}" --out-bam "$OUT/$SAMPLE.bam" \
  --out-duplicate-metrics "$OUT/dup_metrics.txt" --gpusort --gpuwrite --tmp-dir "$OUT/tmp" --num-gpus 1 --low-memory
echo "FQ2BAM_EXIT=$?"
