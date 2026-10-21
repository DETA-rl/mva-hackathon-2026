# Pre-registration log: redacted, times self-recorded, not notarised

Team DETA, SageBio MVA Hackathon 2026.

This log shows what we pre-registered, when we recorded freezing it, and which rule each result applied. It is built
from a snapshot of our hypothesis register taken on 2026-10-20T13:22:28Z (1140 lines, sha256
`aa2e9a3758a34caed2d3ddf4422a0b77aafc610a6e899f85cad408396e76dbc7`). The register is append-only and continued to grow after the snapshot, so this log covers the
project up to that point and nothing later.

It has six parts:

- Section 1: the limits of this log. Read it first.
- Section 2: the frozen pre-registration files and register entries, with sha256 and freeze time.
- Section 3: how a reader can check this log, and what a reader cannot check.
- Section 4: the text of every pre-registration entry written inside the register.
- Section 5: each result entry, by heading, date, verdict and the rule it applied.
- Section 6: amendments, deviations and errata that touch a pre-registration.

## 1. Limits of this log

- Every time in this log is self-recorded by the authors. The sources are: text written into the register by us or
  our agents, file modification times (mtimes) on our own machines, and dates written inside our own rule files.
- We have no third-party timestamp for any of it. No timestamping service, public commit or deposit (for example OSF
  or Zenodo) was used before the tests ran.
- File mtimes are weak evidence. Anyone with the machine can change them, and copying a file can reset them. Some of
  our copies on the analysis machine carry slightly different mtimes from the originals, which is what copying
  without preserving times produces.
- The public repository is a single-commit export made after the analysis, so its commit date says nothing about
  when any rule was written.
- The register records its own sha256 at four points (Section 2.4). Each recorded hash matches the first lines of the
  register snapshot exactly. This shows those lines were not edited after the hash was computed. It does not show
  when the hash was computed.
- The register itself is not published, because it holds read-level values and the full working record rather than
  only the submitted content. Section 4 reproduces its pre-registration entries with the read-level values replaced,
  and Section 5 lists its result entries by heading, date, verdict and rule only. Their bytes differ from the
  register, so the recorded hashes cannot be recomputed from this log.
- Some result entries in the register were not covered by a frozen rule. They are listed in Section 3.2.

In short: this log documents the order and the content of our pre-registrations as we recorded them. It cannot prove
that order or content to an outsider.

## 2. Frozen pre-registrations

Source tags used in the time columns: [register] = text written in the hypothesis register; [mtime] = file
modification time on our machine; [rule text] = a date written inside the rule file. All times are UTC. The register
writes calendar dates without a time zone; several rule files were written shortly after midnight Japan time
(JST = UTC+9), so a register date can be one day later than the UTC date.

### 2.1 Rule files

| file | what it pre-registers | sha256 (full) | freeze time (source) | in this repository? | later amendments (name, date) |
|---|---|---|---|---|---|
| `rules/RANKING_RULE_v1.md` | Gene ranking v1: candidate consequence classes, call weights, score threshold, paralog-family exclusion list, unweighted and shuffled-label baselines | `b5176f200a1a63d772524995172bc163d2cfb8daab346d3f2df8cbe03d68ea4b` | 2026-10-17T03:50:03Z [mtime]. "frozen before the run", no date [rule text] | yes | none. Superseded for the rerun by v2 |
| `rules/RANKING_RULE_v2.md` | Ranking v2: v1 plus the male chrX rule (PAR coordinates of GRCh38) and the cluster-artifact flag | `38c588be982dbb1fdc9cf23b8fdff444d68b507d9c120834caed08171c188834` | 2026-10-17T04:26:46Z [mtime]. "frozen before the run", no date [rule text] | yes | none |
| `rules/SV_RULE_v1.md` | Structural-variant filters (PASS, read support, size, ClinGen dosage genes) | `f34662d7d3755975663431ac54726440c65109ef39c654bb8247c86002334844` | 2026-10-17T05:07:49Z [mtime]. "frozen before run" [rule text] and [register] | yes | none recorded. The rule file was hashed and run in the same command, after the unfiltered output of the same analysis was already visible in the session [session transcript] |
| `rules/RANKING_RULE_v3.md` | Ranking v3: tiers (ClinVar P/LP, compound pattern, other), ablations, shuffled-ClinVar baseline | `3aec99bae249acf343dbd70b5f6ce075490f9b99f977670cf50e3554f74c951d` | 2026-10-17T15:06:59Z [mtime]; register heading date 2026-10-18 | yes | T1-FILTER (2026-10-20): the v3 script never reads the VCF FILTER column; disclosed, rule not amended |
| `rules/RANKING_RULE_v4.md` | Ranking v4: phenotype layer with the organisers' 8 HPO terms inside the v3 tiers | original text: `51dd5efe2867d694cd0cd265059645c5dcedf5153f1b2a9467d8dc4f373c13c3`; current text with Amendment 1: `5884b0edf7e8a31034c332816145ffbdb9ad3aa5f663921b562af384e81b813d` | original text: not recorded (amended in place; no copy of the original text was kept). Amended file: 2026-10-17T15:09:20Z [mtime]. Both hashes in `RANKING_RULE_v4.sha256`, matching "Hash correction (2026-10-18)" [register] | yes (current text only) | Amendment 1, chrM excluded (2026-10-18, "before reading the corrected output") [rule text]; Hash correction (2026-10-18); BUG-V4-CHRM (2026-10-20) |
| `rules/CNV_RULE_v1.md` | Whole-chromosome copy-number call: bins, GC correction, clonal-fraction estimate, call threshold, falsifier | `f15a869924beba1f233f0160ec1bd7e7b6afae0c39c0334eb58e082fe2f649fd` (text with Amendment 1) | "frozen before the run, 2026-10-19" and "Amendment 1 (2026-10-19, before any run)" [rule text]; 2026-10-18T17:03:34Z [mtime]. No hash of the text before Amendment 1 was recorded | no: its frozen text names a local file, and editing it would break the hash; `rules/CNV_RULE_v1.sha256` is shipped | Amendment 1, no MAPQ filter (2026-10-19, before any run) |
| `rules/CALIBRATION_RULE.md` | Calibration of model scores: ClinVar control pool, AUC with bootstrap CI, "informative" threshold (lower bound above 0.7), percentile reporting, falsifier | `eaffd1c97e926a38a9ff50b9aa85d5beab3a728efd2a60f62fd23e1d70c65ae8` | 2026-10-18T17:30:34Z [mtime]. "Written before any model is run" [rule text] | yes | none. Deviations recorded without editing the rule: M-EVO2-CAL-01 and M-PROT-CAL-02 (2026-10-20) |

`rules/SHA256SUMS.txt` lists the six shipped rule files. All seven files above matched their recorded sha256 when this
log was built.

### 2.2 Pre-registrations written outside the register

The register points to each of these files (POINTER entries) with its sha256. Two of them are in this repository,
under `preregistration/frozen/`, listed with their shipped sha256 in `preregistration/frozen/SHA256SUMS.txt`. The
spike-in file is unchanged. The ROW-MAP file is a public copy: passages that cite the authors' internal research
notes are not reproduced. Two lines are dropped (a provenance line, replaced by one line that says so, and a pointer
to an internal note); on 11 lines only the words or the table column that cite those notes are removed. Every
definition, threshold and decision rule of the original is unchanged. Its shipped sha256 therefore differs from the
frozen original's, which is the one in the register and in the table below.

| file | what it pre-registers | sha256 (full) | freeze time (source) | in this repository? | later amendments or deviations |
|---|---|---|---|---|---|
| `PRE_REG_T2_GRADE_01.md` | Operational definition of "published contradiction" for RANKING-RULE-T2 (criteria E, M, D, I, S) | `e18655b31d4ec7a4dac67e167d6cea33238b68c37ee59411d94de2087aad2d37` | 2026-10-20T08:55:03Z [mtime, register] | no | none to the file; the adversarial verification found one material deviation |
| `PRE_REG_SPIKEIN_EPCR.md` | Spike-in test of the frozen ranking: public ClinVar P/LP alleles placed into the child's background calls; the measured rank distribution sets the Track 1 EPCR values; hypotheses, bars and gates | `6d40e58fe2d34d92fa9ff42b7171ad5034b45c2409591779c4cc3775650ede69` | 2026-10-20T09:06:28Z [mtime, register]; "Written: 2026-10-20T09:06Z" [rule text] | yes: `preregistration/frozen/PRE_REG_SPIKEIN_EPCR.md`, unchanged | one deviation disclosed, three more found by the verifier, all without effect |
| `PRE_REG_T2_C4_PRECURSORS.md` | Criterion C4 (mechanism direction) applied to NMN and NR: threshold source, exposure rule, readings | `66aad129e448c21d891c7d92f639a3cd01f02c36c7a309eb92fe5b4d71e3a8e6` | 2026-10-20T09:10:50Z [mtime, register] | no | extended to niacin by the addendum below, which does not change the rule |
| `PRE_REG_T2_C4_NIACIN_ADDENDUM.md` | The same frozen C4 rule applied to niacin, with the dose windows that define admissible human studies | `5c461d4f817d2800e193f2a0ed229b251f2cabc2db029384cbeadfcd523c3ae9` | 2026-10-20T09:37:12Z [mtime, register] | no | none recorded |
| `PRE_REG_R2C_HDAC.md` | Class I HDAC mechanism-class screen (T2-HDAC-R2C): query, universe, falsifiers, DepMap cross-check | `e97a150047caf3deb80538c729729853412c1862a253b2ee4940ac4bd5d6b3e8` | frozen 2026-10-20T11:17:46Z [register]; 11:17:40Z [mtime] | no (its DepMap script is, under `as_run/track2/hdac_screen/`) | not amended [register]; ERRATUM-FACTCHECK-T2: the printed query count is not reproducible as written |
| `PRE_REG_R2B_EXPOSURE.md` | Symmetric exposure and mechanism-direction test (T2-EXPOSURE-01) | `338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534` | frozen 2026-10-20T11:18:24Z, "before any figure was opened" [register]; 11:18:19Z [mtime] | no | not amended [register] |
| `PRE_REG_R2D_R2E.md` | Two instrument-validity tests: criterion C4 (test D) and the DepMap co-dependency thresholds (test E) | `a37962431d2cff8e24f97561ce4f9ffba0619a87bfb46b4ecf8ab7287e32af74` | frozen 2026-10-20T11:19:19Z [register]; 11:19:13Z [mtime] | no | no deviations [register] |
| `PRE_REG_R2A_ABUNDANCE_CLASS.md` | Structural abundance-class test of the missense allele: ThermoMPNN ddG on AlphaFold models, threshold calibrated on public PTEN and TPMT abundance data, controls and decision rule | `be9390e6eafad5cc9c23fb297f67739113a7680d198ab0b4e9c35ecf5a776c00` | frozen 2026-10-20T11:23:17Z; first download 11:23:36Z; first scoring 11:26:37Z [register]; 11:23:24Z [mtime] | no (its scripts are, under `as_run/track2/structural_prediction/`) | adversarial verification: CONFIRMED-WITH-CAVEATS |
| `PRE_REG_ROWMAP.md` | Row-map rule test for the rows of the Track 1 submission CSV | `9f7a440ddbb427783a525e976f898b602cd95471654e9f681ded8ee50d1a0a45` | frozen read-only and copied 2026-10-20T11:31:36Z; run started 11:36:22Z; first ranking 11:37:14Z [register] | yes, as a public copy: `preregistration/frozen/PRE_REG_ROWMAP.md`, shipped sha256 `80ee1affd39c5b3af4f760086dd2df14bc4e4970c98d243adda37ccaea3ae1ad` | one deviation, in a sanity check, no effect on any decision |
| `PRE_REG_NONCHOICES.md` | Mechanism-class screen of 21 classes (later 24), with direction and exposure rules | `ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4` | frozen 2026-10-20T11:42:00Z, "before the screen ran" [register]; 11:41:11Z [mtime] | no | unchanged through the rerun; ERRATUM-NONCHOICES-COUNTS corrected two prose counts, no verdict |

All ten files matched the sha256 recorded in the register when this log was built.

### 2.3 Pre-registrations written inside the register

For these the "file" is the register entry. Their text is in Section 4.

| register entry | what it pre-registers | register sha256 recorded at the time? | recorded time (source) | later amendments |
|---|---|---|---|---|
| HYPOTHESIS REGISTER header (Stages 0 to 5: H01 to H16, M01 to M03) | Test order fixed before any test; prediction and falsifier per hypothesis; the interpretive rule | no | not recorded; the first dated line is 2026-10-17 [register] | Amendments (2026-10-17) |
| PRE-REG-2026-10-20, with P1 (read-backed phasing of the candidate pair), P2 (rare-variant sweep), P3 (CENATAC exact alleles), T2-P4 (DepMap dependency of targets) | P1 phase rule; P2 flag rule; P3 read-count rule; T2-P4 flag rule (fraction of lines with Chronos below -0.5 at least 0.25) | no; inside the first checkpoint (Section 2.4), which also holds its results | date 2026-10-20 [register] | P1-CODE-DEVIATION; REPLICATION-ERRATA E5; P3 restated as PRE-REG-2026-10-20-C |
| PRE-REG-2026-10-20-B | DepMap co-dependency rule (rho at least 0.20 and genome percentile at least 95), falsifier | no; inside the first checkpoint | date 2026-10-20 [register] | test E of PRE_REG_R2D_R2E found the rule underpowered; relabelled, not amended |
| PRE-REG-2026-10-20-C | CENATAC alleles: POSITIVE if at least 3 supporting reads (MAPQ at least 30), NEGATIVE if zero | no; inside the first checkpoint | date 2026-10-20 [register] | deviation disclosed in the result (deletion cutoff 15 bp) |
| PRE-REG-2026-10-20-D | Descriptive placement of the candidate missense against BUB1B I909T and L1012P with three models; falsifier | no; inside the first checkpoint | date 2026-10-20 [register] | none |
| RANKING-RULE-T2 | Evidence grades G1 to G4 and an ordering rule | no; inside the first checkpoint | date 2026-10-20 [register] | APPLICATION-FIX-T2-01 (one application clause withdrawn, rule text unchanged); the ordinal output was later withdrawn by a framing decision |
| PRE-REG-T2-P5 | Dependency of the remaining candidate targets: fixed gene list (26), same method and flag as T2-P4, falsifiers | yes: `6c3c28be8a4278a5096680418c08e9bdd369a2562526cc7f0419d014478ac275` | synced 2026-10-20T08:53:30Z [register] | none |
| PRE-REG-T2-CLASS-01 | Niacin and nicotinamide, one candidate or two: criteria C1 to C5, decision rule, precedence, falsifiers | yes: same hash as above | synced 2026-10-20T08:53:30Z [register] | none |

### 2.4 Register checkpoints

The register records its own sha256 at four points. We hashed the first N lines of the snapshot and compared.

| recorded in | recorded time (source) | recorded sha256 | lines | matches the first N lines of the snapshot? |
|---|---|---|---|---|
| headings of T2-P5 RESULT and T2-CLASS-01 RESULT | 2026-10-20T08:53:30Z [register] | `6c3c28be8a4278a5096680418c08e9bdd369a2562526cc7f0419d014478ac275` | not stated; matches N = 594 (77,702 bytes), which ends with the PRE-REG-T2-CLASS-01 entry | yes |
| REGISTER-SCRIBE BATCH | "about 2026-10-20T09:45Z" [register] | `512cf80357e004d75a64c79de0e062669b3d3217fbdc34978d5273c84c28ab95` | 701 | yes |
| APPLICATION-FIX-T2-01 | not recorded | `2d5c0dd96f9a7188f43d283a64a14dd4b3d5d2a1e6b2d496bea074e6cbab18fc` | 803 | yes |
| REGISTER-SCRIBE BATCH 2 | "about 2026-10-20T10:55Z" [register] | `d86333887a57bfa812e53e66ef71b931f52b35b99f84557b3ba62e60a1153462` | 852 | yes |

What this shows: the first 594 lines, which hold PRE-REG-T2-P5 and PRE-REG-T2-CLASS-01 and no result of either, are
byte-identical to the text that was hashed at the recorded sync time; the same holds for the first 701, 803 and 852
lines. What it does not show: that the recorded times are true. For the earlier register pre-registrations
(PRE-REG-2026-10-20, -B, -C, -D, RANKING-RULE-T2) the same checkpoint holds both the pre-registration and its result,
so it gives no order between them. No checkpoint was recorded after line 852; the later entries (lines 853 to
1140) are covered by no self-hash.

### 2.5 Order of freeze and first result, as recorded

| pre-registration | frozen (source) | first result evidence (source) |
|---|---|---|
| PRE-REG-T2-P5 and PRE-REG-T2-CLASS-01 | synced 08:53:30Z with register hash `6c3c28be...` [register] | both RESULT entries appear after line 594; their own times are not recorded |
| PRE_REG_T2_GRADE_01.md | 08:55:03Z [mtime] | first evidence files 08:55:35Z and 08:55:36Z; RESULT 09:04:00Z [register] |
| PRE_REG_SPIKEIN_EPCR.md | 09:06:28Z [mtime] | run.log first line 09:09:15Z, which logs the pre-registration sha256; first spiked trial 09:09:39Z [register] |
| PRE_REG_T2_C4_PRECURSORS.md | 09:10:50Z [mtime] | first evidence file 09:11:25Z [register]; RESULT 09:32:01Z [mtime] |
| PRE_REG_T2_C4_NIACIN_ADDENDUM.md | 09:37:12Z [mtime] | RESULT 09:51:50Z [mtime, register] |
| PRE_REG_R2C_HDAC.md | 11:17:46Z [register] | not recorded |
| PRE_REG_R2B_EXPOSURE.md | 11:18:24Z [register] | not recorded ("before any figure was opened") |
| PRE_REG_R2D_R2E.md | 11:19:19Z [register] | not recorded |
| PRE_REG_R2A_ABUNDANCE_CLASS.md | 11:23:17Z [register] | first download 11:23:36Z; first scoring 11:26:37Z [register] |
| PRE_REG_ROWMAP.md | 11:31:36Z [register] | run started 11:36:22Z; first ranking 11:37:14Z [register] |
| PRE_REG_NONCHOICES.md | 11:42:00Z [register] | not recorded ("before the screen ran") |

All times are on 2026-10-20, UTC.

## 3. How a reader could check this

### 3.1 What a reader can verify

1. The shipped rule files against their hashes: `cd rules && sha256sum -c SHA256SUMS.txt`. The hashes in Section 2.1
   should match too. For `RANKING_RULE_v4.md` only the current text can be checked; the original text was not kept.
2. That each result in Section 5 names the rule or pre-registration it applies, and that the rule's text is in
   `rules/` or in Section 4, or is a file whose sha256 is in Section 2.2.
3. That amendments, deviations and errata were written as new dated entries that name what they correct, rather than
   as edits (Section 6).
4. That falsifiers were stated and that negative or unresolved outcomes were reported (for example P1 UNRESOLVED,
   PRE-REG-C NEGATIVE, PRE-REG-D NOT PLACED, H-SPK-1 FALSIFIED, R2C ZERO ENTRANTS).
5. Several results in Section 5 can be rerun with the replication harness in this repository (`./replicate.sh plan`
   names each step after its register entry).

### 3.2 What a reader cannot verify

1. That any time in this log is true. All times are self-recorded (Section 1).
2. That Sections 4 and 5 match the private register. The texts were redacted, so the checkpoint hashes cannot be
   recomputed from them.
3. The files listed as not in this repository in Sections 2.1 and 2.2: a reader has their hashes but not their text.
   The two that are in the repository can be checked against `preregistration/frozen/SHA256SUMS.txt`
   (`cd preregistration/frozen && sha256sum -c SHA256SUMS.txt`); for the ROW-MAP public copy that checks the shipped
   file, not the frozen original.
4. That results not tied to a frozen rule were not tuned. These register entries report work that no frozen rule
   covered: "Frequency step", "Genome-wide blind exonic pass", "Consequence step", "Step 3" to "Step 6", "Read-level
   check of the two BUB1B calls", "Proof search", "Readout detection limit", "Model calibration results
   (2026-10-19)", "Protein-model calibration (2026-10-18)" (superseded), "T2-DEPMAP-01" (its hypothesis is stated in
   the same entry as its result), "T2-TRIAL-01", "T2-POWER-01", "C-FIX-01" and "C-FIX-02".

### 3.3 Options for third-party timestamps in future work (none of these was done)

Each option needs only hashes to leave the machine, never the child's data.

1. OpenTimestamps: stamp a text file with the hash list before a test runs. The proof is anchored in the Bitcoin
   blockchain and anyone with the file can check it later. Free.
2. An RFC 3161 timestamp from a public timestamp authority, requested and checked with `openssl ts`.
3. An OSF registration of the pre-registration text (or of its hash list) before results exist. OSF records the
   registration date on its own servers, and registrations can be embargoed.
4. A Zenodo deposit of the hash list. Zenodo records the deposit date and gives a DOI.
5. Push the hash list to a public repository and save the page in the Internet Archive. A commit date alone is set by
   the author's machine; the archive snapshot time is not.
6. E-mail the hash list to the organisers before each run. Their mail server records the receipt time.

## 4. Pre-registration texts from the register

Each entry is reproduced from the snapshot in register order, from its heading to the end of its pre-registration
text. Where an entry also records its own application or result, that part is listed in Section 5 instead. Lines that
cite the authors' internal research notes ("Source: ...") are not reproduced. `[n]` replaces a read-level value
measured on the child's data; nothing else in these texts is changed. The candidate's coordinates and protein change
appear as written, because they are our Track 1 answer. Headings are demoted two levels; dashes used as separators are
written as hyphens.

### HYPOTHESIS REGISTER (pre-registered, MVA Track 1)

Rule: this order is fixed before any test runs. Each test is recorded as PASS, RULED OUT, or NOT TESTABLE with the data used. A RULED OUT is a result, not a reason to reorder. Nothing is moved, dropped, or added after a result is seen without a dated amendment line at the bottom.

Interpretive rule: a hypothesis counts as supported only if its prediction held AND its falsifier did not occur. Literature mention alone never counts as support.

Stage 0: data facts (not hypotheses, they gate other tests)

- S0.1 Child sex: MALE. Declared by the user (2026-10-17). Read-level check agrees: BAI mapped counts give chrY/autosome [n] and chrX/autosome [n] (scratchpad/s01_sex_from_bai.py). Opens H12.
- S0.2 Data inventory: which files exist for the child (BAM/CRAM, supplied VCF, reference build, contig naming). Gates all others.

Stage 1: cheapest, most specific tests (existing data, CPU, falsifiable)

- H01 CEP57 duplication c.915_925dup11 present in the child's reads, missed by the supplied caller.
  Predicts: excess reads with the 11-bp tandem duplication at CEP57 exon location, supported by reads spanning the junction.
  Falsified by: no junction-spanning reads above background.

- H02 BUB1B upstream regulatory allele (rs576524605, ~44 kb upstream of BUB1B) present in the child.
  Predicts: the allele is called or has supporting reads.
  Falsified by: reference homozygous at that position with adequate depth.

- H03 BUB1B intronic mobile-element insertion (Alu/SVA class), by analogy with the reported Kato 2017 case.
  Predicts: discordant or split reads at the BUB1B locus indicating an insertion.
  Falsified by: no discordant or split read cluster in the gene.

Stage 2: genome-wide scans on existing data (no gene prior)

- H04 Dosage-sensitive structural variant genome-wide. Annotate existing SV calls against ClinGen haploinsufficiency and triplosensitivity.
  Falsified by: no dosage-sensitive gene carries a call.

- H05 Low-VAF allele-balance variants genome-wide (mosaic SNV signal).
  Falsified by: no gene shows a consistent low-VAF cluster above the null.

- H06 Runs of homozygosity, uniparental disomy, and chrX hemizygous calls genome-wide.
  Predicts: a recessive candidate in an autozygous or hemizygous region.
  Falsified by: no candidate in an autozygous or hemizygous segment.

- H07 ACMG secondary-findings screen of the supplied VCF, all genes.
  Falsified by: no pathogenic or likely pathogenic call in an SF gene.

- H08 Aneuploidy or mosaic copy change at chr18 and chr19 from depth.
  Predicts: arm-level depth shift in chr18 or chr19.
  Falsified by: flat arm-level depth.

Stage 3: candidate gene families (applied only after Stage 1 and 2 results are recorded)

- H09 TRIP13 biallelic loss-of-function. Positive control for the pipeline; expected to be found if the method works.
- H10 CEP57 biallelic loss-of-function beyond H01 (second allele).
- H11 Second-tier MVA genes: SMC5, SLF2, MAD1L1, CENATAC, TRIM37, MAD2L1BP, CEP192, CDC20.
- H12 Hemizygous X-linked loss-of-function in NAA10. Only if S0.1 says male.
- H13 Spinal muscular atrophy copy loss at SMN1. Requires copy-number calling on reads, not the VCF.

Stage 4: not testable with current data (reported as such, not dropped)

- H14 Phase of the BUB1B pair (cis vs trans). Needs parents or long reads.
- H15 De novo dominant. Needs parents.
- H16 Functional effect of N1002K. Needs wet-lab assays.

Stage 5: method hypotheses (tested on the pipeline, not on the child)

- M01 Gene-plus-genotype ranking outperforms single-variant ranking on the positive control.
- M02 Phenotype-only ranking, with no literature prior, recovers the positive control in the top tier.
- M03 Ablation: results from H09 to H11 survive when the literature prior is removed.

#### Amendments
- 2026-10-17: S0.1 resolved as male (user-declared, consistent with read counts). H12 is now testable.

#### Amendment (2026-10-17)
- Terminology: a test that excludes a hypothesis is a completed test. Results read RULED OUT (test completed). NOT TESTABLE means the data or tools were missing.
- The exon-level read of family genes was run after the H01 to H03 tests, so the order was kept. The TRIP13 positive control is not present at the exon level in this call set, so M01 to M03 cannot be validated on this data yet.

#### PRE-REG-2026-10-20 (written BEFORE any of the tests below are run)
Inputs verified: VCF WGS_EX2312012_HGWCNDSX7.vcf.gz sha256 bec64c68…42175 (matches register); PROBAND01.bam sha256 9b92f9db…dc85b (matches). Local analysis only; nothing identifying the child leaves the box; no external lookups by coordinate.

##### P1 - read-backed phasing of the BUB1B pair (chr15:40209701 nonsense, chr15:40220612 missense, ~10.9 kb)
- H-trans: the two alt alleles are on different homologues (compound heterozygote). H-cis: same homologue.
- Method: list heterozygous SNVs in the interval from the Sentieon VCF; for each adjacent het pair, count read pairs (insert ≤ 800 bp, MAPQ ≥ 30, base quality ≥ 20) carrying both alleles; build the connectivity chain from the nonsense site to the missense site.
- Decision rules (fixed):
  - Connected: at least one chain of het pairs each with ≥ 5 informative bridging read pairs links the two sites. If not connected, the result is UNRESOLVED (no phase call).
  - If connected: report trans if ≥ 90% of informative bridges are concordant with H-trans, cis if ≥ 90% with H-cis; otherwise UNRESOLVED.
- Falsifier of the compound-het reading: a connected chain with ≥ 90% H-cis concordance.
- Expected outcome stated in advance: UNRESOLVED is a possible and acceptable result at this read length.

##### P2 - rare-variant sweep for phenocopy and U12-spliceosome genes
- Genes (pre-set list): RNU4ATAC, RNU6ATAC, ZRSR2, SNRNP48, ESCO2, PCNT, CENPF, plus the MVA set already tested.
- Method: from the Sentieon VCF, list every non-reference call in these genes; annotate frequency with the local gnomAD v4.1 exome files (no network).
- Decision rule: a gene is flagged if it carries (a) a homozygous rare call, or (b) two rare heterozygous protein-altering or splice calls. Flags are reported descriptively; no gene is called causal from this sweep alone.
- Falsifier of the "not covered" claim: none; this is a coverage test. Report the count of calls and the coverage at each gene.

##### P3 - exact-allele check for the published CENATAC family alleles
- Alleles (from claude-gap-010, unverified citation de Wolf 2021): c.805+2_805+19del18 and c.803A>T.
- Method: locate CENATAC in the GENCODE v44 GTF; convert the c. positions to GRCh38 genomic coordinates with the canonical transcript; search the VCF and the BAM at those coordinates; for the deletion, count split and soft-clipped reads at the junction.
- Decision rule: POSITIVE if ≥ 3 alt-supporting reads (MAPQ ≥ 30) at the SNV or ≥ 3 junction-spanning split reads for the deletion; NEGATIVE if zero; otherwise INDETERMINATE.
- Falsifier of the "no supporting paper" statement: none; the test checks the child, not the literature.

##### T2-P4 - DepMap 24Q4 safety numbers for candidate targets (cancer lines only, not normal marrow)
- Targets (pre-set): MTOR, CDC20, SIRT2, PLK4, ANAPC4, UBE2C, KIF18A, ABL1, SRC, NAMPT, NMNAT1.
- Metric per target: fraction of lines with Chronos gene effect < −0.5; and the median in blood-lineage lines.
- Decision rule: a target is flagged as "high on-target dependency" if its fraction ≥ 0.25. Descriptive only.
- Falsifier of a "safe to target" claim: any flagged target cannot be called safe from this data.

#### PRE-REG-2026-10-20-B (written BEFORE the lever screen runs) - T2 DepMap lever screen
- Question: which candidate lever genes have knockout fitness effects that co-vary with BUB1B across cancer cell lines?
- Data: DepMap 24Q4 CRISPRGeneEffect (1,178 lines). Local only.
- Candidates (pre-set): FBXW7, AURKB, PPP2R5A, PPP2R5B, PPP2R5C, PPP2R5D, PPP2R5E, KIF18A, ANAPC1, ANAPC2, ANAPC4, ANAPC5, ANAPC10, ANAPC11, ANAPC13, ANAPC15, ANAPC16, CDC16, CDC23, CDC27, UBE2C, UBE2S, MAD2L1BP.
- Negative controls (pre-set): SIRT2, NAMPT, NMNAT1, ABL1, SRC.
- Metric: Spearman rho between each gene's gene-effect vector and BUB1B's, across lines with both values.
- Empirical null: the rho of every gene in the genome versus BUB1B. Percentile of each candidate in that null.
- Decision rule: "co-dependent" if rho ≥ 0.20 AND percentile ≥ 95th of the genome-wide null. "Not co-dependent" if rho < 0.10 or percentile < 50th. Otherwise "indeterminate".
- Falsifier of the lever hypothesis: no candidate reaches "co-dependent". Reported in full either way.
- Caveat stated in advance: co-dependency reflects shared essentiality and lineage structure; it does not show mechanism or direction.

#### PRE-REG-2026-10-20-C (written BEFORE the CENATAC check runs) - exact-allele test for the published CENATAC family alleles
- Alleles (from claude-gap-010; citation de Wolf 2021, EMBO J; PMID not verified): c.805+2_805+19del18 and c.803A>T, on the canonical GENCODE v44 CENATAC transcript.
- Coordinate convention: c.N = Nth base of the CDS on the canonical transcript (transcript-oriented, so minus-strand genes are complemented). c.805+k = intronic base k after c.805 in transcript orientation.
- Data: Sentieon VCF and PROBAND01.bam, local only.
- Decision rules (fixed):
  - POSITIVE for c.803A>T: an alt-supporting call at the mapped genomic position with ≥ 3 alt reads (MAPQ ≥ 30) in the BAM.
  - POSITIVE for c.805+2_805+19del18: ≥ 3 reads at the junction that split across the deletion (soft-clip or split alignment spanning the 18-bp span), with MAPQ ≥ 30.
  - NEGATIVE: zero supporting reads for either. INDETERMINATE: between.
- Falsifier of "the child carries a published CENATAC family allele": a NEGATIVE on both.
- Note: this checks the child. It does not test the literature claim.

#### PRE-REG-2026-10-20-D (written BEFORE scoring) - placement of N1002K among two characterised kinase-domain alleles
- Alleles: BUB1B p.I909T and p.L1012P (characterised in the literature per the library file; citation PMC2887387 UNVERIFIED), and the child's p.N1002K.
- Models: ESM-1v and ESM-2 masked-marginal LLR (damage = −LLR), AlphaMissense score (hg38 table, looked up by UniProt protein_variant string). Same models and controls as M-PROT-CAL-02 (98 controls).
- Reference: protein sequence from the canonical transcript (protein_rule/controls/BUB1B.fasta); residue checks asserted before scoring.
- Output: each allele's score and its percentile among the 98 controls, per model.
- Decision rule: none on class. The result is descriptive placement only. No allele is called pathogenic, benign, or abundance-class from this test.
- Falsifier of "N1002K sits with I909T and L1012P": a model that places N1002K outside the range spanned by I909T and L1012P would contradict it; reported either way.
- Note: "abundance class" is a literature claim not verified here; this test does not test it.

#### RANKING-RULE-T2 (2026-10-20, written before applying it to candidates)
Scope: every candidate treated as a medication: market-approved prescription drugs, OTC drugs (e.g., niacin, nicotinamide) and dietary supplements (e.g., NMN, NR). No separate tier for supplements.
Evidence grades for the BUBR1 mechanism in patient-relevant cells:
- G1: human data on BUBR1 or aneuploidy endpoints in a clinical or patient-derived setting, replicated.
- G2: patient-derived cell data on BUBR1 protein or mitotic endpoints, one or more independent sources.
- G3: mouse or cell-line data on BUBR1 protein or checkpoint endpoints, not contradicted by an independent source.
- G4: mechanism or pathway evidence only, or G3 evidence with a published contradiction.
Ranking: candidates ordered by grade (G1 first). Ties resolved by safety: fewer broadly-essential targets in Table 2 ranks higher.
A supplement or OTC drug sits above a prescription drug only if its grade is strictly higher.

#### PRE-REG-T2-P5 (2026-10-20, written and synced BEFORE any DepMap value for any gene below was opened) - on-target dependency of the candidate targets not covered by T2-P4
Question: for every candidate medication in the Track 2 list, how does its molecular target or entry enzyme score on the pre-registered T2-P4 dependency metric? T2-P4 measured 11 genes; the candidates' own entry enzymes and receptors were largely not among them (see APPLICATION_FIX_PROPOSAL.md section 3: "fingolimod, arimoclomol and 4-PBA have no target in Table 2"). This test measures them. The user's instruction was "measure first".

Target assignment, fixed before the run. Sources named per row; PubMed records resolved by title and year at pre-registration time (abstract quotes are given in the RESULT entry, not here). ChEMBL and KEGG DRUG were queried by drug name only; no patient data left the machine.
| candidate | target or entry enzyme (HGNC symbol) | source (named at pre-registration) | confirm or reject of the starting point given in the brief |
|---|---|---|---|
| niacin (nicotinic acid) | NAPRT | PMID 17604275 Hara 2007 J Biol Chem, "Elevation of cellular NAD levels by nicotinic acid and involvement of nicotinic acid phosphoribosyltransferase in human cells" | CONFIRMED |
| niacin | HCAR2 (GPR109A, HM74A) | PMID 12563315 Tunaru 2003 Nat Med, "PUMA-G and HM74 are receptors for nicotinic acid and mediate its anti-lipolytic effect" | CONFIRMED |
| niacin, nicotinamide, NMN, NR (shared downstream step) | NMNAT1, NMNAT2, NMNAT3 | PMID 16118205 Berger 2005 J Biol Chem, "Subcellular compartmentation and differential catalytic properties of the three human nicotinamide mononucleotide adenylyltransferase isoforms" | CONFIRMED (NMNAT1 was already measured in T2-P4; NMNAT2 and NMNAT3 were not) |
| nicotinamide | NAMPT | PMID 15381699 Revollo 2004 J Biol Chem (rate-limiting salvage enzyme) | CONFIRMED, already measured in T2-P4 (0.296, flagged) |
| nicotinamide | SIRT1, SIRT2 (reported inhibition at high concentration) | PMID 12297502 Bitterman 2002 J Biol Chem (record resolved; abstract quoted in the RESULT) | CONFIRMED as a reported target; SIRT2 already measured in T2-P4 (0.006) |
| NMN | NMNAT1, NMNAT2, NMNAT3 | PMID 16118205 | CONFIRMED |
| NMN | SLC12A8 (reported NMN transporter; contested in the literature) | Grozio 2019 Nat Metab (record to be resolved in the RESULT); reported, not assumed | ADDED to the brief's list, flagged as contested |
| NR | NMRK1, NMRK2 | PMID 15137942 Bieganowski and Brenner 2004 Cell, "Discoveries of nicotinamide riboside as a nutrient and conserved NRK genes establish a Preiss-Handler independent route to NAD+ in fungi and humans" | CONFIRMED |
| fingolimod | SPHK2 (the kinase that phosphorylates FTY720 to the active species) | PMID 13129923 Billich 2003 J Biol Chem, "Phosphorylation of the immunomodulatory drug FTY720 by sphingosine kinases" | CONFIRMED |
| fingolimod | S1PR1, S1PR3, S1PR4, S1PR5 | PMID 11967257 Brinkmann 2002 J Biol Chem and PMID 11923495 Mandala 2002 Science; US label (openFDA, recorded in APPLICATION_FIX_PROPOSAL.md section 2) names S1P receptors 1, 3, 4, 5; ChEMBL mechanism record for CHEMBL544665 gives "Sphingosine 1-phosphate receptor agonist" (DailyMed reference) | CONFIRMED. S1PR2 is NOT included: the label and the primary sources exclude it |
| fingolimod | SET (I2PP2A), PPP2CA, PPP2R1A | PMID 23180565 Saddoughi 2013 EMBO Mol Med and PMID 17717597 Neviani 2007 J Clin Invest (FTY720 as a PP2A activator acting through SET) | CONFIRMED as a reported route; the PP2A catalytic and scaffold subunits are measured as proxies for that route, not as drug binding sites |
| arimoclomol | HSF1, HSPA1A, HSPA1B | PMID 12893279 Hargitai 2003 Biochem Biophys Res Commun (bimoclomol, the parent compound class, acts by prolonged HSF1 activation) and PMID 15034571 Kieran 2004 Nat Med (arimoclomol as a heat shock protein coinducer). The US label (NDA214927) states the mechanism is unknown | CONFIRMED as the reported route, with the label disagreement recorded |
| 4-PBA (sodium phenylbutyrate) | HDAC1, HDAC2, HDAC3, HDAC8 (class I) | PMID 26260271 Kusaczuk 2016 Tumour Biol (phenylbutyrate as a pan-HDAC inhibitor) and PMID 25557635 Kusaczuk 2015 Curr Pharm Des (review) | CONFIRMED for class I; published characterisation is pan-HDAC, so class I is a subset chosen in advance, not the whole reported activity |

Genes measured in this test (fixed list, 26): NAPRT, HCAR2, NAMPT, NMNAT1, NMNAT2, NMNAT3, NMRK1, NMRK2, SLC12A8, SIRT1, SIRT2, SPHK2, S1PR1, S1PR3, S1PR4, S1PR5, SET, PPP2CA, PPP2R1A, HSF1, HSPA1A, HSPA1B, HDAC1, HDAC2, HDAC3, HDAC8. NAMPT, NMNAT1 and SIRT2 are re-measured so that the whole table comes from one run; their T2-P4 values are the check.

Method, identical to the T2-P4 script p4_depmap_safety.py (sha256 c7d87310a11c2448ba2a3d2845dd8bd6750d6c675a1e7ff27d607ed6d889f524): DepMap 24Q4 CRISPRGeneEffect.csv and Model.csv; column matched on the symbol before " ("; blood lineage defined as OncotreeLineage in {Myeloid, Lymphoid}; metric per gene = fraction of lines with Chronos gene effect < -0.5 over all lines with a value, and the median Chronos in blood-lineage lines.

Flag rule (unchanged, the pre-registered T2-P4 rule the user confirmed is the definition of "broadly essential"): flag a gene if fraction >= 0.25. No other threshold is introduced. Per-candidate count of flagged targets = the number of its genes above that meet the flag, counted over the genes listed for that candidate (shared genes are counted for every candidate that uses them).

Reporting of absent genes: a gene with no column in CRISPRGeneEffect.csv is reported as "not measured". It is never reported as 0, and it never counts as an unflagged target.

Caveat stated in advance, and not used to change any rule: a CRISPR knockout dependency is a loss-of-function proxy. It measures what happens when the gene is removed from a cancer cell line. It is not a safety measure for a drug that activates or supplies a target (niacin, nicotinamide, NMN, NR feed enzymes; fingolimod is an S1P receptor agonist and a reported PP2A activator; arimoclomol is a reported HSF1 coinducer). For an inhibitor (4-PBA on HDACs, nicotinamide on sirtuins) the proxy is closer but still a cancer-line proxy, never normal marrow. This caveat is reported, not used to re-flag or un-flag anything.

Decision rule: descriptive. No candidate is called safe or unsafe from this test. The output feeds criterion C3 of T2-CLASS-01 and the RANKING-RULE-T2 safety tie-break.
Falsifier of the claim "the targets of fingolimod, arimoclomol and 4-PBA are unmeasured, so the tie-break is undefined for them" (APPLICATION_FIX_PROPOSAL.md section 3, Decision U): any of those genes returning a value here falsifies it for that candidate.
Falsifier of "niacin and nicotinamide have the same safety placement": a different flagged-target count for the two.
Expected outcomes stated in advance as acceptable: zero flagged targets for every candidate, or several; and "not measured" for the non-expressed receptor genes (the S1P receptors and HCAR2 are plausible absentees in a CRISPR screen of cancer lines).

#### PRE-REG-T2-CLASS-01 (2026-10-20, written and synced BEFORE any new evidence for this question was gathered, and before T2-P5 was run) - are niacin and nicotinamide one candidate or two, and in which regulatory class?
Question: RANKING-RULE-T2 lists "niacin or nicotinamide" as a single OTC candidate (register line H518). This test decides, by rule, whether that is one candidate or two, and which class each belongs in. The outcome changes the candidate's placement under RANKING-RULE-T2; the rule text itself is NOT amended by this test.

Honesty clause: facts already known to the author when this entry was written (so the reader can see what the test could not be blind to).
1. From agent_out/citations/CITATION_CHECK.md section 5 (verified against openFDA and Drugs@FDA on 2026-10-20): every FDA-approved niacin product is a prescription product (Niacor ANDA040378, extended-release generics; Niaspan NDA020381 discontinued); no FDA-approved OTC niacin drug product was found; nicotinamide has no FDA-approved single-agent oral product and appears in Drugs@FDA only inside prescription parenteral multivitamins; niacin has no EU authorisation (Tredaptive withdrawn 2013).
2. From APPLICATION_FIX_PROPOSAL.md section 3: niacin's entry enzyme is NAPRT (Preiss-Handler) and nicotinamide's is NAMPT (salvage); NAMPT meets the pre-registered T2-P4 flag at 0.296 and NAPRT was not measured in T2-P4.
3. General prior knowledge held by the author, not yet sourced at pre-registration time: nicotinamide is a reported sirtuin inhibitor at high concentration. The concentrations, the sirtuin isoforms involved, and human plasma levels reached are NOT known to the author at pre-registration time and are what C4 must establish.
4. Not known at pre-registration time: the T2-P5 dependency numbers (C3), including NAPRT, SIRT1, NMNAT2, NMNAT3; any human pharmacokinetic figure for nicotinamide; any BUBR1, SIRT2 or aneuploidy result for niacin or for nicotinamide as separate molecules (C5).

Outcomes, exhaustive and fixed: MERGE-Rx (one candidate, prescription class), MERGE-supplement (one candidate, supplement class), SEPARATE (niacin prescription plus nicotinamide supplement, two candidates), DROP-one (one molecule removed; the entry must state which and why).

Criteria, each with its source class and a reading fixed in advance.
- C1 regulatory. Does a product authorised by the FDA or the EMA exist for oral systemic use of this molecule as a single agent, and is it prescription or over the counter? Sources: Drugs@FDA and openFDA (drugsfda and label endpoints), DailyMed SPLs, EMA medicine pages, queried by drug name only. Reading: "Rx" if every authorised oral single-agent product is a prescription product; "OTC" if an authorised non-prescription drug product exists; "no authorised drug product" if none exists, in which case the molecule's class for the rule is dietary supplement. A dietary supplement sold under DSHEA is not an FDA drug approval and never reads as OTC.
- C2 NAD+ entry route. Which enzyme is the rate-limiting or first committed step for this molecule entering NAD+ synthesis? Source class: primary literature (PubMed, abstract or full text), with a verbatim quote. Reading: the named enzyme. "Same route" only if the first committed enzyme is the same gene.
- C3 safety tie-break placement. The count of flagged targets from T2-P5 for each molecule, using the pre-registered T2-P4 flag (fraction of lines with Chronos < -0.5 at or above 0.25) over that molecule's target list as fixed in PRE-REG-T2-P5. Reading: the integer count, plus the list of genes reported "not measured".
- C4 mechanism direction. Does either molecule act against the hypothesis it is proposed for? The hypothesis (report Section 2.3) needs SIRT2 activity: the NMN-induced BubR1 rise was SIRT2-dependent (PMID 24825348). Nicotinamide is a reported sirtuin inhibitor. Source class: primary literature for the inhibition constant and the isoform, plus published human pharmacokinetics for plasma or tissue concentrations reached by an oral dose. Reading: "opposes" if a primary source reports inhibition of SIRT2 (or of sirtuins including SIRT2) at a concentration at or below a published human plasma concentration reached by an oral dose of the molecule; "does not oppose" if the inhibitory concentration is above every published reached concentration; "unresolved" if no human exposure figure is found. Absence of exposure data is never read as "does not oppose".
- C5 direct BUBR1, SIRT2 or aneuploidy evidence, for each molecule separately. Source class: PubMed, searched by molecule name crossed with BUB1B, BUBR1, SIRT2, aneuploidy, mosaic variegated aneuploidy, spindle assembly checkpoint. Reading: the count and nature of primary sources per molecule, with PMIDs. No evidence is an acceptable finding and is recorded as such.

Decision rule, fixed in advance:
- SEPARATE if the two molecules differ on C1, C2, C3 or C4 in a way that changes their class, their placement under RANKING-RULE-T2, or the mechanism claim made for them.
- MERGE only if they agree on all of C1, C2, C3 and C4. The merged class then follows C1.
- DROP a molecule if C4 reads "opposes" for it at a reached exposure. If C4 reads "unresolved" the molecule is NOT dropped and the unresolved state is recorded in the entry and carried into the report.
- C5 does not change the outcome by itself; it changes the evidence grade only through RANKING-RULE-T2, which is not amended here. If C5 produced grade-relevant evidence it would be recorded and the grade reassessed under the existing rule.
- Precedence if two criteria point different ways: any single difference on C1, C2, C3 or C4 that meets the SEPARATE test is sufficient for SEPARATE. DROP is applied on top of the merge or separate decision, not instead of it.

Falsifiers, one per outcome, stated before the evidence was gathered:
- MERGE-Rx would have required an authorised prescription oral single-agent product for both molecules, the same first committed enzyme, the same flagged-target count, and the same C4 reading. Evidence that would have produced it: an FDA or EMA authorised oral nicotinamide drug product, prescription, plus identical C2, C3, C4.
- MERGE-supplement would have required no authorised oral single-agent drug product for either molecule, with C2, C3, C4 identical. Evidence that would have produced it: no approved niacin drug product anywhere (contradicting fact 1 of the honesty clause), plus identical C2, C3, C4.
- SEPARATE requires at least one qualifying difference. Evidence that would have blocked it: identical regulatory class, a shared first committed enzyme, equal flagged-target counts, and the same C4 reading.
- DROP-one requires a primary source showing sirtuin or SIRT2 inhibition at or below a published reached human concentration for that molecule. Evidence that would have blocked it: inhibition only at concentrations above every reached human level, or no published human exposure figure (which gives "unresolved", not DROP).

Scope limits stated in advance: this test decides candidate identity and class only. It does not grade the evidence, does not change RANKING-RULE-T2, and does not propose any dose. No patient-derived data is used; only molecule, gene and protein names leave the machine.

## 5. Result entries, by the rule they applied

One row per result entry in the snapshot that applies a pre-registered rule, in register order. The verdict is the
label the entry records.

| register entry | date | rule applied | verdict recorded |
|---|---|---|---|
| Results log: S0.1 | 2026-10-17 | header, Stage 0 | MALE (declared by the user; read counts consistent) |
| Results log: H01 | 2026-10-17 | header, H01 | RULED OUT at alignment level |
| Results log: H02 | 2026-10-17 | header, H02 | RULED OUT |
| Results log: H03 | 2026-10-17 | header, H03 | RULED OUT at the level tested |
| Results log: H04 | 2026-10-17 | header, H04 | NOT TESTABLE with the supplied data (see Step 2) |
| Results log: H05 | 2026-10-17 | header, H05 | PARTIAL, not a gene finding |
| Results log: H06 | 2026-10-17 | header, H06 | RULED OUT (proxy) |
| Results log: H07 | 2026-10-17 | header, H07 | NOT TESTABLE locally |
| Results log: H08 | 2026-10-17 | header, H08 | NOT COMPLETED (see Step 2) |
| Results log: H09 | 2026-10-17 | header, H09 | RULED OUT; the positive control is not in this call set |
| Results log: H10 | 2026-10-17 | header, H10 | RULED OUT for coding |
| Results log: H11 | 2026-10-17 | header, H11 | outcome deferred to the frequency step |
| Results log: H12 | 2026-10-17 | header, H12 | RULED OUT |
| Results log: H13 | 2026-10-17 | header, H13 | NOT TESTABLE with this data |
| Results log: H14, H15, H16 | 2026-10-17 | header, Stage 4 | NOT TESTABLE |
| Results log: M01 to M03 | 2026-10-17 | header, Stage 5 | NOT RUN |
| Ranking v1 | 2026-10-17 | `RANKING_RULE_v1.md` | no unique candidate |
| Ranking v2 | 2026-10-17 | `RANKING_RULE_v2.md` | no unique candidate |
| Step 2: structural variants | 2026-10-17 | `SV_RULE_v1.md`; header H03, H04, H08 | H03 RULED OUT at SV level; H04 NOT CONCLUDED; H08 RULED OUT at 1 Mb sampled resolution |
| Ranking v3, hierarchical evidence | 2026-10-18 | `RANKING_RULE_v3.md` | tier A: BUB1B, LZTR1, GNRHR; under the shuffled-ClinVar baseline BUB1B is not ranked |
| Ranking v4, phenotype layer | 2026-10-18 | `RANKING_RULE_v4.md` (run 1, then with Amendment 1) | BUB1B rank 1 under v4, without phenotype, phenotype only and shuffled |
| Copy-number mosaicism rule v1, amended run | 2026-10-19 | `CNV_RULE_v1.md` | no chromosome called; falsifier met |
| M-EVO2-CAL-01 | 2026-10-20 | `CALIBRATION_RULE.md` section 2 | EXPLORATORY, not informative |
| M-PROT-CAL-02 | 2026-10-20 | `CALIBRATION_RULE.md` sections 2 and 3 | ESM-1v, ESM-2 and AlphaMissense INFORMATIVE |
| M-EVO2-CHILD-01 | 2026-10-20 | `CALIBRATION_RULE.md` section 3 | exploratory model output; no percentile reported |
| T2-P4 RESULT | 2026-10-20 | PRE-REG-2026-10-20, T2-P4 | 7 of 11 targets flagged |
| P1 RESULT | 2026-10-20 | PRE-REG-2026-10-20, P1 | UNRESOLVED |
| P2 RESULT | 2026-10-20 | PRE-REG-2026-10-20, P2 | one gene flagged (BUB1B, the known pair); no other gene flagged |
| PRE-REG-B RESULT | 2026-10-20 | PRE-REG-2026-10-20-B | no candidate co-dependent (the rule was later found underpowered by test E) |
| PRE-REG-C RESULT | 2026-10-20 | PRE-REG-2026-10-20-C | NEGATIVE for both published alleles |
| PRE-REG-D RESULT | 2026-10-20 | PRE-REG-2026-10-20-D | NOT PLACED: two of three models contradict the placement |
| RANKING-RULE-T2, application recorded in the same entry | 2026-10-20 | RANKING-RULE-T2 | every candidate at grade G4; the ordinal output was later withdrawn |
| T2-P5 RESULT | 2026-10-20 | PRE-REG-T2-P5 | 24 of 26 genes measured, 4 flagged; the falsifier of equal safety placement for niacin and nicotinamide triggered |
| T2-CLASS-01 RESULT | 2026-10-20 | PRE-REG-T2-CLASS-01 | SEPARATE, then DROP nicotinamide |
| POINTER-SPIKEIN-EPCR | 2026-10-20 | `PRE_REG_SPIKEIN_EPCR.md` | H-SPK-1 FALSIFIED (bar 0.80); verified, no number corrected |
| POINTER-T2-GRADE-01 | 2026-10-20 | `PRE_REG_T2_GRADE_01.md` | the adversarial verification judged the outcome G3-contested |
| POINTER-T2-C4-PRECURSORS | 2026-10-20 | `PRE_REG_T2_C4_PRECURSORS.md` | C4-PASS for NMN and NR |
| POINTER-T2-C4-NIACIN | 2026-10-20 | `PRE_REG_T2_C4_NIACIN_ADDENDUM.md` | C4-UNRESOLVED; niacin not dropped |
| POINTER-R2A | 2026-10-20 | `PRE_REG_R2A_ABUNDANCE_CLASS.md` | ABUNDANCE-LIKE under the rule applied mechanically; reported as weak evidence; verification CONFIRMED-WITH-CAVEATS |
| POINTER-R2B | 2026-10-20 | `PRE_REG_R2B_EXPOSURE.md` | one arm removed on direction; for five of seven arms the exposure arithmetic cannot be done |
| POINTER-R2C | 2026-10-20 | `PRE_REG_R2C_HDAC.md` | ZERO ENTRANTS; the class is excluded on direction |
| POINTER-R2D-R2E | 2026-10-20 | `PRE_REG_R2D_R2E.md` | test D: criterion C4 NON-DISCRIMINATING; test E: INFORMATIVE-AT-T_A-ONLY (T2-DEPMAP-01 not relabelled, PRE-REG-B relabelled) |
| POINTER-ROWMAP | 2026-10-20 | `PRE_REG_ROWMAP.md` | ADOPT P5 x C3; row 1 unchanged |
| POINTER-NONCHOICES, POINTER-NONCHOICES-V2 | 2026-10-20 | `PRE_REG_NONCHOICES.md` | 25 verdict rows from 24 classes: 11 EXCLUDED, 6 NOT TESTED, 8 OPEN |

## 6. Amendments, deviations and errata that touch a pre-registration

| register entry | date | what it changes |
|---|---|---|
| Amendments, and Amendment (2026-10-17) | 2026-10-17 | S0.1 resolved as male, so H12 became testable; terminology RULED OUT / NOT TESTABLE fixed; the test order was kept |
| Amendment 1 of `RANKING_RULE_v4.md` and Hash correction | 2026-10-18 | chrM genes excluded, recorded before the corrected output was read; both hashes of the rule recorded |
| Amendment 1 of `CNV_RULE_v1.md` | 2026-10-19 | no MAPQ filter, recorded before any run |
| BUG-V4-CHRM | 2026-10-20 | one ranking script lacks Amendment 1; the rule is unchanged; the harness adds a step that runs the amended rule (RANK-V4BF) |
| P1-CODE-DEVIATION | 2026-10-20 | the recovered P1 code is a fragment-span check, not the pre-registered bridge count; the outcome (UNRESOLVED) is unchanged |
| LIMIT-STOPLOST, T1-FILTER, COUNT-487 | 2026-10-20 | method limits disclosed (stop-loss calls cannot be called; the v3 script ignores the VCF FILTER column) and one count withdrawn and recounted; no rule amended |
| APPLICATION-FIX-T2-01 | 2026-10-20 | one application clause of RANKING-RULE-T2 withdrawn; the rule text is unchanged |
| REPLICATION-ERRATA, E1 to E9 | 2026-10-20 | ten expected metric values differed across six executed steps and produced E1 to E6, each naming the register entry it corrects and leaving that entry unedited, with the conclusion holding in all six. The other three are not corrections of that kind: E7 corrects a manifest entry that sits outside the register; E8 revises the counting definition behind a withdrawn figure, and its conclusion holds only in part; E9 corrects nothing and records the scope that the unrun GPU and network steps leave unverified. |
| ERRATUM-NONCHOICES-COUNTS and ERRATUM-NONCHOICES-UNIVERSE-CLOSED | 2026-10-20 | two prose counts of the mechanism-class screen corrected to its own table, and a one-row gap explained; no verdict changed |
| ERRATUM-FACTCHECK-T2 | 2026-10-20 | the HDAC screen's printed query count is not reproducible as written (a rerun gives 25 unfielded and 11 with field tags); the falsifier is reported over the 14 records retrieved at the run |
| Framing decision on the Track 2 output | 2026-10-20 | the ordinal output of RANKING-RULE-T2 withdrawn; verdicts are stated per mechanism; no pre-registered rule text changed |
