# External steps: how to run them without the harness

`./replicate.sh plan --tier full` lists six steps as external: the harness does not run them, and they have no
expected values in `replicate/expected.yaml`. This file gives, for each one, the procedure as we ran it: the tool and
version, the command or request, every input and where to get it, the expected outcome and how to tell the run
worked, what our record does not hold, and the failure modes we hit. Every procedure is taken from our own record
(the launchers and scripts as run, the hypothesis register and the session transcripts); none was re-run in the form
written here unless this file says so. Where our script is held back, the procedure is written out in full, so the
missing file costs only convenience.

## Reproducing this work: what counts as agreement

Two kinds of step need two standards.

The scripted steps are deterministic: fixed seeds, pinned versions, hashed weights. The harness compares each metric
against the value we recorded and prints both. A difference there is a difference, and the table says so.

The remaining steps apply written criteria to published sources. Rerunning them, with our model or another, can yield
different wording and, at a threshold, a different verdict. Agreement is therefore not textual. Each of these steps
ships the criterion, hashed before the sources were opened, and the quotation it was applied to. The test is whether
the criterion was applied to that evidence, not whether the sentences match.

A different verdict from the same criterion and the same quotation is evidence about the criterion. Report it.

## The six steps

Paths use the variables of the main README (`$MVA_DATA`, `$MVA_REF`, `$MVA_WORK`). Expected outcomes are given at the
level of the decision and as file hashes. Counts measured on the child's data are not repeated here, for the same
reason the register is not shipped.

| step | what it decides | tool | needs | verdict |
|---|---|---|---|---|
| [ALIGN-01](#align-01-alignment-of-the-organisers-fastqs) | produces the BAM that 11 harness steps read | Parabricks 4.7.1-1 fq2bam | one NVIDIA GPU, Docker, the FASTQs | RECOVERABLE |
| [SV-MANTA](#sv-manta-structural-variants-h03-h04-and-the-dicer1-depth-check) | H03 and H04 (structural variants), Step 4 DICER1 depth check | Manta 1.6.0, Python | Docker, the BAM, the ClinGen list of 16 Oct 2026 (shipped) | PARTLY RECOVERABLE: the DICER1 depth script is held back, one output exists only in a transcript, the step has no expected metrics, and rerun determinism was never tested |
| [H13-SMN](#h13-smn-homozygous-smn1-loss) | homozygous SMN1 loss | Ensembl REST, pysam | network, the BAM | RECOVERABLE. The comparison is at the level of the decision |
| [M-REG-BORZOI](#m-reg-borzoi-regulatory-model-calibration) | whether the Borzoi regulatory model is usable here | borzoi-pytorch 0.5.1 | one NVIDIA GPU, network (GTEx API) | PARTLY RECOVERABLE: the GPU memory, a confidence interval and which weight file was loaded are not recorded |
| [T2-CLASS-01](#t2-class-01-niacin-and-nicotinamide-one-candidate-or-two) | niacin and nicotinamide: one candidate or two, and their regulatory class | openFDA, PubMed, ChEMBL | network | PARTLY RECOVERABLE: the responses were not saved, and 43 of the 113 label records were not read |
| [PRE-REG-ROWMAP](#pre-reg-rowmap-which-two-variants-go-in-a-submitted-row) | which two variants go in a submitted row (rows 4 and 5 changed) | Python, the organisers' evaluation.py, AlphaMissense | the spike-in step folder, ClinVar, AlphaMissense, the organisers' scorer | PARTLY RECOVERABLE: the organisers' scorer is not ours to ship, and two gates cannot pass against the ported copies and the shipped files |

## ALIGN-01: alignment of the organisers' FASTQs

What it produces: the GRCh38 BAM (config input `bam`) read by S0.1, H01, H-BATCH, H08, DETECT-LIMIT, CNV-V1,
READCHECK, P1, P3, SV-MANTA and H13-SMN.

Tool: NVIDIA Parabricks 4.7.1-1, `pbrun fq2bam` (GPU BWA-MEM, coordinate sort, duplicate marking), container
`nvcr.io/nvidia/clara/clara-parabricks:4.7.1-1`, digest
`sha256:191f3e113631493888c9a54534f6484614f645f6767cb0078c4f1b8ac116a34b` (`env/containers.txt`). To pull the exact
image: `docker pull nvcr.io/nvidia/clara/clara-parabricks@sha256:191f3e113631493888c9a54534f6484614f645f6767cb0078c4f1b8ac116a34b`.

Inputs:

- The eight FASTQs of the organisers' dataset (Hugging Face `SageBio/mva-hackathon-2026-data`, commit
  `59e322d27f399006b398d366d33e703e48a29914`): `WGS_EX2312012_HGWCNDSX7_S16_L00{1,2,3,4}_R{1,2}_001.fastq.gz`, about
  85 GB in total. `tools/dl.py --local-dir $MVA_DATA` (without `--vcf-only`) downloads them; their sha256 are in
  `replicate/expected.yaml` (`fastq_l1_r1` to `fastq_l4_r2`, taken from the Hugging Face LFS metadata).
- The reference, three files from the NCBI folder
  `https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/`,
  put in one folder:
  - `GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz`, decompressed to `.fna` (sha256 of the `.fna`:
    `592502666381c995059a6b4a5dda11e6b1f6b8efeea04e7dacfffe1e0d2f0d25`);
  - `GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.fai` (NCBI's index, used as downloaded);
  - `GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.bwa_index.tar.gz` (NCBI's prebuilt BWA index,
    3,451,512,197 bytes), extracted in the same folder (`tar xzf`), which gives the `.amb`, `.ann`, `.bwt`, `.pac`
    and `.sa` files.
  We did not build the BWA index ourselves. Our reference folder also held a sequence dictionary, made with
  `samtools dict <fna> -o <fna>.dict` inside the Parabricks container and copied to the same name without `.fna`.

Command as we ran it (our launcher, with our folders replaced by `<work>` and `<data>`; the read-group values are
the ones we used):

```
for L in 1 2 3 4: RG_L = "@RG\tID:HGWCNDSX7.L\tLB:lib1\tPL:ILLUMINA\tSM:PROBAND01\tPU:HGWCNDSX7.L"

sudo docker run --rm --gpus device=1 -u $(id -u):$(id -g) -v <work>:<work> -v <data>:<data> -w <work> \
  nvcr.io/nvidia/clara/clara-parabricks:4.7.1-1 \
  pbrun fq2bam --ref ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna \
    --in-fq <data>/WGS_EX2312012_HGWCNDSX7_S16_L001_R1_001.fastq.gz <data>/WGS_EX2312012_HGWCNDSX7_S16_L001_R2_001.fastq.gz "<RG_1>" \
    --in-fq ... L002 ... "<RG_2>" --in-fq ... L003 ... "<RG_3>" --in-fq ... L004 ... "<RG_4>" \
    --out-bam out/PROBAND01.bam --out-duplicate-metrics results/dup_metrics.txt \
    --gpusort --gpuwrite --tmp-dir tmp --num-gpus 1 --low-memory
```

No known-sites file, no base-quality recalibration and no `--bwa-options` were passed. `tools/fq2bam.sh` builds the
same command from arguments: `tools/fq2bam.sh $MVA_DATA <folder>/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna
$MVA_WORK/align PROBAND01 0` (the fourth argument is the read-group sample label, `PROBAND01` in ours; the fifth is
the GPU). It differs from our launcher only in that: it finds the FASTQs and the flowcell from the file names, the
data and reference folders are mounted read-only, Docker is called without `sudo` unless `DOCKER="sudo docker"` is
set, and every output goes under the output folder. It has only been checked with `bash -n`; it has never been run.

Resources and time, as recorded: one RTX 3090 (24 GB); GPU memory in use 13.7 to 14.0 GB at 99 to 100% utilisation;
82 min 6 s (78 min 20 s, 2 min 15 s and 1 min 31 s for the three phases in the tool log). Peak host RAM and peak
temporary disk were not recorded. The output BAM is about 110 GB.

How to tell it worked: the container exits 0 (`tools/fq2bam.sh` prints `FQ2BAM_EXIT=0`), and the output folder holds
the BAM, its `.bai` and `dup_metrics.txt`. Our BAM's sha256 is
`9b92f9db6aebf383ce76063884d5e5ab4d3a0e8354847bf5e189d12217adc85b` (`replicate/expected.yaml`, input `bam`). Whether
a rerun with the same inputs and options is byte-identical was never tested; the BAM header records the command line
and paths, so a rerun from other folders will differ. Give the BAM as input `bam` (with the `.bai` next to it);
`./replicate.sh check` hashes it, and BAM-derived counts are then reported as NOT COMPARABLE while the pre-registered
decisions are compared (each metric's `tol_alt`).

Not in our record: peak host RAM, peak temporary disk, a flagstat of the full BAM, and the sha256 of the `.fai`, the
BWA index files and the `.dict`.

Failure modes we hit:

- Docker needed `sudo` on our machine.
- `samtools dict` failed with "Cannot open file for writing" when the reference folder was not writable by the
  container user.
- The system disk was 87% full, so the work folder went to a second disk; plan for the 110 GB BAM plus temporary
  files (their peak was not recorded).

Verdict: RECOVERABLE. The record holds the container, the command with every option, the inputs and their sources,
and the output hash.

## SV-MANTA: structural variants (H03, H04) and the DICER1 depth check

What it decides: H03 (a structural variant at the BUB1B locus) and H04 (structural variants overlapping
dosage-sensitive genes), under the frozen rule `rules/SV_RULE_v1.md`; then Step 4, a depth check of the two large
calls in the DICER1 region of chromosome 14.

Tools: Manta 1.6.0, container `quay.io/biocontainers/manta:1.6.0--py27h9948957_6`, digest
`sha256:48d0c2464fa0129935438c5cddec5f67c4b3d65e8f7a647f95164ee51662cc70` (`env/containers.txt`); then Python 3.13
with pysam 0.24.1 (in `env/requirements-quick.txt`).

Inputs:

- The BAM and `.bai` (input `bam`, from ALIGN-01 or ours on request) and the GRCh38 FASTA with its `.fai` (input
  `fasta`, the same file as in ALIGN-01).
- GENCODE v44 basic GTF (input `gtf`; see the inputs table in the README).
- The ClinGen gene curation list, GRCh38, release of 16 Oct 2026 (input `clingen_gene_curation`), downloaded on
  2026-10-17 from `https://ftp.clinicalgenome.org/ClinGen_gene_curation_list_GRCh38.tsv` (249,270 bytes; sha256
  `18af35bf83fee59c86f02a2ab49089f36718ddb7abae5bf80acb2f4785ec98c1`, also in `replicate/expected.yaml`; its header
  reads "16 Oct,2026"). ClinGen replaces the file at that URL at each release and we found no archive of earlier
  releases, so the exact release cannot be re-fetched from upstream. Our copy is shipped, unmodified, as
  `references/ClinGen_gene_curation_list_GRCh38.tsv` (ClinGen curated content is CC0 1.0).

Procedure as we ran it:

1. Manta, whole genome, germline mode, no call regions (our launcher, with our folders replaced; it ran as root
   through `sudo`):

   ```
   docker run --rm -v <bam_and_ref_folder>:<bam_and_ref_folder>:ro -v <work>:/work \
     quay.io/biocontainers/manta:1.6.0--py27h9948957_6 \
     bash -c "configManta.py --bam <bam> --referenceFasta <fasta> --runDir /work/run && /work/run/runWorkflow.py -m local -j 12 -g 16"
   ```

   Output: `run/results/variants/diploidSV.vcf.gz`. Ours took 26 min 4 s (1564 s) and exited 0.
2. `as_run/track1/sv_cnv/h03_h04_sv.py` (in this repository, as run): set `P` (the folder holding
   `run/results/variants/diploidSV.vcf.gz` and the ClinGen file) and `GTF` (lines 3 to 6), then run it with Python. It
   prints, to the terminal only, the number of records, every call within BUB1B plus or minus 50 kb, and the
   dosage-sensitive genes (ClinGen haploinsufficiency or triplosensitivity score 3) overlapped by any call. Ours
   printed to the session only; there is no output file.
3. `as_run/track1/sv_cnv/sv_rule_v1.py` (in this repository, as run): set `P`, `VCF`, `CG`, `GTF` and `OUT` (lines 3
   to 7) and run it. It applies the rule (FILTER PASS; PR alt + SR alt at least 4; DEL, DUP or INS of at least 50 bp,
   or BND; overlap with a score-3 dosage gene span from GENCODE v44), writes `sv_rule_v1_summary.tsv` and prints the
   counts and the H03 calls under the same filters.
4. Step 4, the DICER1 depth check (our script is held back: it hard-codes our local BAM path and the two calls'
   coordinates, which are the child's data). Take the two large calls that overlap DICER1 on chr14 in
   `diploidSV.vcf.gz`, one DEL and one DUP. With pysam and one generator `random.Random(3)`, used in this order:
   - baseline: 8 windows of 1 Mb on each of chr1, chr2 and chr3, start drawn uniformly in [5 Mb, length minus 6 Mb);
     baseline = median of `AlignmentFile.count(chrom, start, start + 1_000_000)`;
   - for the DEL call, then the flank chr14:60,000,000-80,000,000, then the DUP call: 12 windows of 1 Mb with start
     drawn uniformly in [segment start, segment end minus 1 Mb), and the median count divided by the baseline.

   A ratio near 1.0 means no copy-number change across the call. No numeric threshold was written down before the
   check.

Expected outcome (register Step 2 and Step 4; Track 1 report): H03 RULED OUT at the structural-variant level (no
Manta call within BUB1B plus or minus 50 kb); H04 NOT CONCLUDED (calls passing the rule still overlap many
dosage-sensitive genes); the two DICER1-region calls are artifacts (ratio near 1.0 for both). With our BAM,
our `diploidSV.vcf.gz` has sha256 `fa8b827b6ef2be032b62b8cd620885fb28452b4016d63f8df7c4ee5bb51d19ad`; whether Manta
gives the same file on a rerun was not tested.

Verdict: PARTLY RECOVERABLE: (1) the Step 4 DICER1 depth script is held back, because the two calls it checks are
written into it; the procedure above is its algorithm, with the same seed and order of draws, but not the file that
ran; (2) the output of `h03_h04_sv.py` exists only in a session transcript, never in a file, so there is no file of
ours to compare a rerun with; (3) `replicate/expected.yaml` has no expected values for this step, so a rerun is
compared with the decisions in the register (H03 RULED OUT, H04 NOT CONCLUDED, DICER1 calls artifacts), not metric by
metric; (4) whether Manta gives the same VCF on a rerun was not tested. Every input can be obtained: the ClinGen
release we used is shipped in `references/`, the BAM is ours on request or yours from ALIGN-01, and the container and
every Manta option are recorded; `h03_h04_sv.py` and `sv_rule_v1.py` are shipped as run.

Failure modes we hit:

- Plain `docker` failed on our machine; we ran the launcher with `sudo -n`.
- Manta refuses to reuse a run folder; give a new `--runDir` each time.
- The first `h03_h04_sv.py` run found no overlaps because chromosome names were compared with the "chr" prefix on
  one side only; both scripts in this repository strip it on both sides.
- A pretest on a 0.69x subset of the reads gave unusable calls; use the full BAM.

## H13-SMN: homozygous SMN1 loss

What it decides: whether the child lacks both copies of SMN1. SMN1 and SMN2 are near-identical paralogs, so the VCF
cannot answer this; the check counts paralog-specific bases in the reads.

Tools: the Ensembl REST API (`https://rest.ensembl.org`, accessed 2026-10-17; no assembly parameter was passed and the
Ensembl release was not recorded); Python `difflib`; pysam 0.24.1 `AlignmentFile.count_coverage` on the BAM. Our
scripts are held back (they hard-code our local paths); the procedure below is complete without them.

Inputs: the BAM and its `.bai` (input `bam`). The reference FASTA is not used: the gene sequences come from Ensembl.

Procedure as we ran it:

1. Gene spans (requests as issued):
   `GET https://rest.ensembl.org/lookup/symbol/homo_sapiens/SMN1?content-type=application/json` and the same for
   `SMN2`. They returned SMN1 ENSG00000172062, 5:70925030-70953942, strand 1, and SMN2 ENSG00000205571,
   5:70049635-70078522 (public annotation).
2. Gene sequences: `GET https://rest.ensembl.org/sequence/region/human/5:70925030..70953942:1?content-type=text/plain`
   and `GET https://rest.ensembl.org/sequence/region/human/5:70049635..70078522:1?content-type=text/plain` (we used a
   240 s timeout).
3. Paralog markers: `difflib.SequenceMatcher(None, smn1, smn2, autojunk=False).get_opcodes()`, keeping only `replace`
   opcodes of one base on each side. SMN1 position = 70925030 + i1, SMN2 position = 70049635 + j1. We obtained 21
   single-base differences (sequence lengths 28,913 and 28,888).
4. Counts on the BAM, for each of the 21 pairs: `count_coverage("chr5", pos - 1, pos, quality_threshold=20,
   read_callback=keep)`, where `keep` accepts reads that are not duplicates, not secondary and have mapping quality
   20 or more. Two passes: (a) both paralog bases at the SMN1 position; (b) the SMN1 base at the SMN1 position and
   the SMN2 base at the SMN2 position (added, as recorded at the time, so that SMN2 copies are counted at their own
   coordinates).
5. Decision as applied (register Step 6; `replicate/expected.yaml`, H13-SMN): homozygous SMN1 loss is ruled out if
   SMN1-specific bases are present in the reads; one copy against two is not resolved.

Expected outcome: homozygous SMN1 loss RULED OUT; copy number 1 against 2 NOT RESOLVED (a dedicated SMN caller would
be needed). Our counts are not repeated here; with a BAM other than ours they are not comparable anyway, only the
decision is. Run time: about 3 minutes, almost all of it the Ensembl downloads and the sequence comparison.

Not in our record: the Ensembl release; a check of the 21 bases against the GRCh38 FASTA (the register asked for it
before counting, and it was not done); a numeric threshold for "present" (no minimum number of reads or positions was
written down).

Failure modes we hit:

- The first attempt (register Step 5) took the 7th exon by position of transcript ENST00000380707, a 111 bp window
  that is identical in SMN1 and SMN2, so it found no marker. Comparing the whole genes fixed it.
- `lookup/id/<gene>?expand=1` returned HTTP 500 intermittently; the same request succeeded on retry.
- pysam's `read_callback`, when given a function, replaces its default filter, so `keep` above does not exclude
  QC-failed or supplementary reads.

Verdict: RECOVERABLE. The comparison is at the level of the decision: the requests, the marker method, the count
parameters and the decision text are in the record, and exact counts are comparable only with our BAM.

## M-REG-BORZOI: regulatory-model calibration

What it decides: whether the Borzoi regulatory model separates known expression-associated variants from random
substitutions on chromosome 15 well enough to be used. Recorded result: it does not (AUC 0.496), so Borzoi is not
used.

Scripts, in this repository as run: `as_run/models/regulatory/borzoi_score.py` (the step) and
`as_run/models/regulatory/gtex_probe.py` (a scout that chose the genes; `borzoi_score.py` does not call it).

Environment: Python 3.13.5 with borzoi-pytorch 0.5.1, torch 2.14.1+cu130, transformers 4.57.6, huggingface_hub
0.36.2, scikit-learn 1.9.1, pandas 3.0.6, numpy 2.5.4 and pysam 0.24.1, all pinned in `env/requirements_freeze.txt`
(the full environment of README step 1). Flash attention was not used. One CUDA GPU (the script calls `.cuda()`).

Inputs:

- Weights: Hugging Face `johahi/borzoi-replicate-0`, revision `521db103372769581b8d1d616e6a3b496da490c5` (CC BY 4.0).
  sha256 of `model.safetensors` (743,692,788 bytes):
  `d839593c3350bc3aea93b7a6d1fc3ce2b1629e0f4322ecb3c6b6743d14932f75`; of `pytorch_model.bin`:
  `782613dcc6155cd0c475d325085424663a9bf8bd6e10a3ee05e62911dfb52e7d`; of `config.json`:
  `36abbcd288215e1df7172b16aae099faf8a5bced15d6e4a3b37f3fc347cc9d35`. We called `snapshot_download` without a
  revision; the revision above is the one our download recorded. Which of the two weight files was loaded was not
  recorded.
- Genome: UCSC hg38 chromosome 15, `https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr15.fa.gz`,
  decompressed (sha256 of the `.gz`: `0e0d988d6cbdf9fe424e1847a2278aa3ff9636b08663a6dd32c046f001dcf427`; of the `.fa`:
  `cc78011619ea32e9f68e84d69b6ac7efae0c1f8aa3247e5dea9161bc42206c67`). The contig must be named `chr15`; the script
  builds the `.fai`.
- GTEx API v2 (network), read by the script itself: `https://gtexportal.org/api/v2/reference/gene?geneId=<symbol>&gencodeVersion=v26&genomeBuild=GRCh38%2Fhg38`
  for each gene's TSS and versioned GENCODE id, then
  `https://gtexportal.org/api/v2/association/singleTissueEqtl?gencodeId=<versioned id>&tissueSiteDetailId=Whole_Blood&datasetId=gtex_v8`.

Procedure as we ran it:

1. Download the weights (`huggingface_hub.snapshot_download("johahi/borzoi-replicate-0",
   revision="521db103372769581b8d1d616e6a3b496da490c5", local_dir=<models>/borzoi)`) and chromosome 15.
2. In `borzoi_score.py`, set `ROOT`, `FASTA`, `MODEL` and `OUT` (lines 16 to 19); `OUT` must exist.
3. Run it on one GPU: `CUDA_VISIBLE_DEVICES=0 python -I borzoi_score.py > run.log 2>&1`.

What the script does: positives are GTEx v8 Whole Blood eQTL single-nucleotide variants with p < 1e-4 for the 11
chromosome-15 genes listed at lines 28 and 29, de-duplicated by position, of which 120 are drawn with
`sample(n=120, random_state=0)`; each positive gets one negative, a random position within 100 kb of its gene's TSS
with a random alternative base (`random.seed(0)`, `np.random.seed(0)`), so the negatives are random, not matched
substitutions. Each variant is scored in a 524,288 bp window on the 1,543 RNA tracks: d = log2(alt + 1) - log2(ref +
1); "total" is the largest, over tracks, of the summed absolute d over all output bins, and "local" the largest
absolute d within 512 bp of the variant. The AUC is `sklearn.metrics.roc_auc_score`. (The script's docstring says
p < 1e-5; the code, which is what ran, uses 1e-4.)

Expected outcome: `run.log` prints the number of eQTL rows returned per gene, `positives available: 1421`,
`controls: {1: 120, 0: 120}`, `RNA tracks: 1543`, progress lines, and `CONTROL AUC total=0.496 local=0.493 n_pos=120
n_neg=120`; the output folder holds `control_scores.tsv` (241 lines; sha256 of ours
`64262aefa3753b2350589502366674e1480f07bce77893b8231db190006a3404`) and `summary.json`. Decision: chance level, so
the model is not used.

Run time: 349 s on one RTX 3090 for the run that produced the result. The five runs together took 413 s; the first
four stopped early on the failures listed below. The "about 7 min" for Borzoi in the Track 1 report's compute
paragraph is the five runs together.

Why our control set is shipped: the GTEx responses were not saved, and the script reads only the first page (at
most 250 rows) of each gene's eQTL list; four genes returned exactly 250 rows, so their lists are cut in the order the
API returns them, and a change in the live API's data or ordering changes the positives. Without our copy the step is
therefore not bit-reproducible. `intermediates/borzoi_control_scores.tsv` is our `control_scores.tsv`, byte for byte
(sha256 above): gene, chromosome-15 position, reference and alternative base, GTEx normalised effect size and p-value
(positives only), label, and the two scores, for the 120 eQTL positions and the 120 random positions. It holds no
position or value from the child's data. With it, the scores can be recomputed on exactly our 240 variants and
compared value by value, and the AUC recomputed from the file alone.

Not in our record: the GPU memory used (the 20 GB once declared for this step had no measurement behind it); a
confidence interval for the AUC (none was computed); whether a rerun is bit-identical (only one run succeeded).

Failure modes we hit (all fixed in the script as shipped): an unversioned GENCODE id returns no eQTL rows (the script
takes the versioned id from `/reference/gene`); `variantId` has five fields, not four; the model returns 6,144 output
bins, so the centre bin is 3,072; scikit-learn was missing from the environment at first.

Verdict: PARTLY RECOVERABLE: the GPU memory, a confidence interval for the AUC, which weight file was loaded and a
second successful run are not in our record. The scripts, the package versions, the weights revision and hashes, the
genome, the endpoints, the seeds and the commands are, and our control set is shipped.

## T2-CLASS-01: niacin and nicotinamide, one candidate or two

What it decides: whether niacin and nicotinamide are one Track 2 candidate or two, and in which regulatory class each
falls.

This step applies written criteria to published sources: see "Reproducing this work: what counts as agreement" at
the head of this file.

Criteria: PRE-REG-T2-CLASS-01, quoted in full in `preregistration/REDACTED_PREREG_LOG_SELF_RECORDED.md` (Section 4):
criteria C1 (regulatory class), C2 (first committed enzyme into NAD+ synthesis), C3 (safety placement, the T2-P5
counts), C4 (does the molecule act against the mechanism at a reached human exposure) and C5 (direct evidence,
descriptive only), the decision rule (any one difference that changes class, placement or the mechanism claim gives
SEPARATE; C4 "opposes" drops a molecule) and the falsifiers. It was synced to the register at 2026-10-20T08:53:30Z,
before any query below. There is no script for this step; the requests were issued one by one, and neither the
responses nor a query script were saved.

Language models: the session logs of this step record Claude Code with the model ids claude-opus-5-5 and
claude-opus-5 (both listed in the README's disclosure). Their wording is not part of the record and would not repeat
on a rerun; the criteria above and the sources below are what a rerun applies.

Requests as issued (2026-10-20, between about 08:55 and 09:02 UTC, no API key):

- C1, openFDA:
  - `https://api.fda.gov/drug/drugsfda.json?search=products.active_ingredients.name:"NIACIN"&limit=100`
  - `https://api.fda.gov/drug/label.json?search=openfda.generic_name:"NIACIN"&limit=50`
  - `https://api.fda.gov/drug/drugsfda.json?search=products.active_ingredients.name:"NIACINAMIDE"&limit=100`
  - `https://api.fda.gov/drug/label.json?search=openfda.generic_name:"NIACINAMIDE"&limit=100`

  Reading: keep single-ingredient oral products; marketing status (prescription, over the counter, discontinued) from
  `drugsfda`, product type and route from `label`. The EMA search page needed JavaScript and the EMA bulk file of
  assessment reports returned HTTP 404, so the EU facts were recorded as unverified. DailyMed was not queried.
- C2, PubMed abstracts: PMIDs 17604275 and 15381699.
- C3: the per-candidate counts of the T2-P5 step (in the harness, quick tier).
- C4: PubMed title searches (for example `nicotinamide[Title] AND SIRT2[Title]`) and the abstracts of PMIDs 12297502,
  8679452 and 8532910; ChEMBL activities,
  `https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL1140&target_chembl_id=CHEMBL4462&format=json&limit=50`
  and the same for targets CHEMBL4506 and CHEMBL4461; the exposure figure 1.28 mM is 156.4 ug/mL divided by 122.12
  g/mol (PMID 8532910), computed with a one-line Python command.
- C5: PubMed counts, `[Title/Abstract]` searches pairing each molecule with BUB1B/BubR1, aneuploidy, SIRT2, spindle
  checkpoint and MVA.

Outcome as recorded: SEPARATE, then DROP nicotinamide on C4. Later register entries changed the source on which C4
rests; the reading that stands, and its caveats, are in the Track 2 report (the T2-CLASS-01 rows).

Not recoverable from our record: the responses themselves (none was saved, and the sources are live); 43 of the 113
openFDA label records for NIACINAMIDE, which were not read (13 were not fetched, since the request fetched 100, and
30 were fetched but not displayed); part of the PubMed results of the C5 searches (for example 3 of 11 and 10 of 18 records were not fetched); the EU
check; DailyMed.

Failure modes, and what to do differently on a rerun:

- `label.json` returned 113 records for NIACINAMIDE and the request fetched 100: page with `&skip=100`.
- Only the names "NIACIN" and "NIACINAMIDE" were searched, and only in `generic_name` or `active_ingredients.name`;
  "NICOTINIC ACID" and "NICOTINAMIDE" were not.
- PubMed result lists were capped at 6 to 8 identifiers per query.
- openFDA allows 240 requests per minute and 1,000 per day per address without a key (openFDA documentation).

Verdict: PARTLY RECOVERABLE: the responses were not saved, 43 of the 113 label records were not read, DailyMed was
not queried and the EMA route failed. The pre-registered criteria, every request with its date, the PubMed and ChEMBL
identifiers and the model ids are in the record.

## PRE-REG-ROWMAP: which two variants go in a submitted row

What it decides: the submission format allows at most two variants per row, so when a candidate gene has more than
two candidate calls a rule has to choose which two. The draft rule (R0) took the highest-weight loss-of-function
call plus the lowest-position missense. This test asks whether a better rule exists, by spiking the same public
ClinVar Pathogenic / Likely pathogenic causals as the spike-in test and adding one or two ClinVar non-P/LP decoy
calls in the same gene, then scoring the rows each rule builds with the organisers' own scorer. Six rules (R0 and
P1 to P5) times three row constructions (C1 to C3) = 18 combinations, 779 primary trials over 201 genes.

Tools: Python 3.13.5, numpy 2.5.4, scipy 1.18.1, pysam 0.24.1, and the organisers' `evaluation.py`, imported
unmodified from the challenge Space (git blob `2aed4922...`, Space commit `60e1c30e`). AlphaMissense supplies the
per-variant score the P2 to P5 rules use.

Inputs and where to get them:

- The spike-in step folder: `trials.tsv`, `pools.tsv`, `bg_consequence.tsv`, `spike_cons_visible.tsv` and
  `spike_cons_hidden.tsv`. Run `./replicate.sh run --steps PRE-REG-SPIKEIN-TRIALS` and use its step folder; the
  harness reproduces those files byte for byte (step PRE-REG-SPIKEIN-TRIALS, metrics `sha256_trials` and
  `sha256_alleles`).
- `clinvar.vcf.gz`, the release pinned in `replicate/expected.yaml` (input `clinvar_vcf`).
- `AlphaMissense_hg38.tsv.gz` (input `alphamissense`, sha256 `0516cfd7...`).
- The organisers' VCF (input `vcf`), read only to confirm every proposed variant is in it and to hash it before and
  after.
- The organisers' `evaluation.py`. It is their code; it is not in this repository. Take it from the challenge Space
  at the commit above.
- The authors' submitted CSV, shipped at `preregistration/rowmap/TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv`, sha256
  `a349d642fb4597ea2ebe1b032cf40e3ea2b962e80860e7cc9538164944d78e4f`. Its ten rows are the published Track 1
  answer and are also the row table of `reports/DETA_track1_report.md`.

Procedure as we ran it, from `as_run/track1/rowmap/`:

1. `python feasibility_decoy.py` before freezing the pre-registration: per-gene counts of ClinVar non-P/LP records
   that look like rare coding decoys. Public ClinVar only, no child data, no ranking.
2. `python run_rowmap.py`. Gate S-R4 first: the sha256 of every input and the git blob of the scorer must match the
   values written into the script, then `evaluation.py` is imported. Gate S-R1 regenerates the spike-in's base
   trials from `pools.tsv` with seeds 101, 102, 103, 501 and 502 and requires them to be identical. The decoy pool
   is then built from ClinVar non-P/LP records in the trial genes and pushed through the same frozen extraction and
   consequence scripts as the causals. S-R3 checks that the real top 10 equals the submitted CSV's genes, that R0 x
   C1 rebuilds the submitted rows exactly, and that the scorer gives 100 points and F-max 1.0 when row 1 is the
   answer. S-R2 reruns the 700 decoy-free controls and requires the spike-in's hit rank and gene for each. S-R5
   requires all six rules to agree wherever the causal gene has one call or two heterozygous calls. Only then does
   the decoy trial loop run, with seeds 601, 602 and 603.
3. `python analyze_rowmap.py`: mean rank points per combination with a stratified gene-cluster bootstrap (10,000
   resamples, `numpy.random.default_rng(1)`), then decision D-RM-1 applied as written.
4. `python propose_csv.py`: the real rows under the adopted combination, and a check that every proposed variant is
   in the organisers' VCF with the exact REF and ALT.
5. `python mech_check.py`: a post-hoc diagnostic of why R0 fails, by consequence class. Not pre-registered, and
   labelled so in the result.

Expected outcome: all five gates pass (S-R2 700/700, S-R3 10/10 rows, S-R5 0 mismatches); the winner is P5 x C3 at
80.20 mean rank points against 49.10 for R0 x C1, a gain of +31.10 with a bootstrap interval of [26.54, 35.47] and a
Bonferroni-adjusted gate interval of [24.26, 37.72]; verdict adopt P5 x C3. Rows 4 and 5 of the submission change
and row 1 does not, in all 18 combinations. The full result, including the secondary strata and the near-tie among
P2, P3 and P5, is `preregistration/rowmap/RESULT.md`.

How to tell the run worked, without our files: `A-d0` under R0 x C1 must give mean rank points 73.83, which is the
same number the spike-in test reports as its stratum A expected score (73.8, step PRE-REG-SPIKEIN, metric
`mean_rank_points`). That is the one figure the two pre-registered tests share, and the harness checks the
spike-in's side of it.

Why this is not a harness step: measured, not assumed

We ported this driver's path constants exactly as a harness step would (six lines, line count unchanged), supplied
every input including the two this repository cannot ship, and ran it under the harness's own sandbox. The results,
on 2026-10-21:

| what was supplied in place of the as-run helper scripts | where it stopped |
|---|---|
| the ported copies, as a harness step would run them | gate S-R4, `S-R4 hashes False` |
| the shipped as-run copies in `as_run/track1/spikein/` | gate S-R4, `S-R4 hashes False` |
| the authors' unredacted as-run originals | nowhere: it ran to the end in 68 s |

With the unredacted originals it reproduced every gate and every count: `S-R4 hashes True`, scorer blob
`2aed4922`, `S-R1` identical for A, A-BUB and E, `S-R3 True True [100.0, 1.0]`, `S-R2` 0 mismatches, `S-R5` 0
mismatches, and the same six decoy strata at the same sizes as the recorded run (A-CH-dec 384, A-hid-dec 558,
A-HOM-dec 174, E-CH-dec 395, E-HOM-dec 200, A-BUB-dec 200). So path-only porting is enough and nothing in the code
defeats a harness step.

What defeats it is gate S-R4 itself, and precisely this: the gate pins the sha256 of the as-run `calls_param.py`
and `consequence_param.py`, and line 4 of each named a local user name and a removable-disk identifier, so the
shipped copies carry `[redacted]` there and hash differently (`spikelib.py` carries no redaction and its shipped
copy matches the pinned hash exactly). The gate therefore cannot pass against any file this repository is allowed
to contain. Rewriting it would change what it checks, so it is left as it ran, and what the gate was for is
covered more strongly elsewhere: `./replicate.sh audit-port` proves, with a keyed hash of each original, that the
ported copies differ from the as-run scripts only on the lines logged in `PORTING_LOG.md`.

Two further things a reader cannot get, measured in the same run:

- `TRACK1_SUBMISSION_FINAL_PROPOSED.csv`, which gate S-R3 compares its rows against. It is the pre-ROW-MAP CSV, and
  two of its variants (`chr7:39339681` and `chr8:38057199`) are calls of the child that are in no published file,
  so it does not ship. Supplied from the authors' copy it matched its pinned hash and S-R3 passed.
- The organisers' `evaluation.py` is theirs, not ours, so it is not here; but it is public, and the copy we used
  matched both its pinned sha256 (`6d18b581`) and its git blob (`2aed4922`), so a reader who fetches it from the
  Space at commit `60e1c30e` has the same file.

Everything else the test reads is reproducible here. The five spike-in files it consumes
(`bg_consequence.tsv`, `spike_cons_visible.tsv`, `spike_cons_hidden.tsv`, `trials.tsv`, `pools.tsv`) came back
byte-identical to their pinned hashes from the step folder of PRE-REG-SPIKEIN-TRIALS, and AlphaMissense and ClinVar
matched theirs.

Not in our record, or held back: `real_rows.tsv` (the rows every combination builds, 180 rows of the child's calls)
and `trials_rowmap.tsv` (4.3 MB of per-trial scores) stay on the authors' machine; the aggregate of both is
`preregistration/rowmap/summary_rowmap.json`, which ships. The kinase-domain boundary the P4 rule uses (residues 766
to 1050) comes from public secondary sources and is UNVERIFIED against UniProt. Whether this use of AlphaMissense
counts as non-commercial is a question the result records as unresolved.

Verdict: PARTLY RECOVERABLE: the pre-registration, the as-run scripts, the deviations and the full aggregate result
all ship, the five spike-in inputs it reads are reproduced byte for byte by PRE-REG-SPIKEIN-TRIALS, the organisers'
scorer is public at a named commit, and the ported driver was measured running the whole test to the end in 68 s
reproducing every gate; but it cannot be made a harness step, because gate S-R4 pins the sha256 of two as-run
helper scripts whose shipped copies must carry `[redacted]` on the line that named a local user name and a disk,
and gate S-R3 compares against a CSV holding two of the child's calls that are in no published file. The decision
and the aggregate tables are therefore checkable here, the per-trial scores are not, and the decision arithmetic is
re-applied without any input at all by the harness step PRE-REG-ROWMAP-CHECK.
