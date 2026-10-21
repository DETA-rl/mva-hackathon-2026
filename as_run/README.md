# As-run copies (records, not run by the harness)

The folders `track1/`, `track2/` and `models/` here are verbatim copies of the scripts as they ran on the
analysis machine. They are kept as evidence of what ran. The harness never runs them: it runs the ported copies
in `replicate/analysis/`, which differ from the as-run scripts only on the lines listed in `PORTING_LOG.md`
(`./replicate.sh audit-port` checks that, file by file, against the copies in this folder).

These copies keep the authors' folder layout in their path constants, but the local user name, the disk
identifier and the temporary session folder are replaced by `[redacted]`, for example
`D = "/home/[redacted]/Documents/HACKATON/_private/blind_gnomad/"` in `track1/blind_exonic/gnomad_match.py`.
Do not run them as they are. To download the organisers' dataset use `tools/dl.py` (it takes `--local-dir`), not
`track1/alignment/dl.py`.

## Redactions (the only differences from the files that ran)

In this public copy a token is replaced by `[redacted]` only where a line named a local user name, a disk
identifier or a temporary session folder (24 lines in 20 files, all of them path constants), and on two lines of
`citations/t1_rows.py` that cite the authors' internal research notes; every other byte is the original. The candidate's coordinates, protein change and residue number appear as the scripts used them, because
they are our published Track 1 answer. Every redacted line is listed in `replicate/analysis/PORTING.json`
(`repo_copy_redactions` for the as-run copies of ported scripts, `public_copy_redactions` for the others; also in
`PORTING_LOG.md`), and the public audit skips only those lines. The authors keep the unredacted files; with them and
the HMAC key, `./replicate.sh audit-port --candidates DIR --recovered DIR --root t2tests=DIR --root asrun=DIR
--key-file FILE` checks the full files.

## Track 2 scripts added on 2026-10-20

- `track2/hdac_screen/r2c_depmap_hdac.py`: the DepMap cross-check of the class I HDAC mechanism screen (register
  entry T2-HDAC-R2C): dependency fraction and blood-lineage median for the 11 HDAC genes, same method as T2-P4. It
  reads the public DepMap 24Q4 files only. The literature part of that screen used fixed PubMed queries recorded in
  its pre-registration; it has no script. That part applies written criteria to published sources; see
  "Reproducing this work: what counts as agreement" in the README.
- `track2/structural_prediction/`: the structural abundance-class test of the missense allele (register entry R2-A):
  `prep_structures.py` (AlphaFold models of BUBR1 and the two calibration proteins), `thermo_ssm.py` (ThermoMPNN
  site-saturation ddG), `rsa.py` (relative solvent accessibility), `calibrate.py` (threshold calibrated on public
  PTEN and TPMT VAMP-seq abundance data), `extra_controls.py`, and `bubr1_decide.py` (the pre-registered decision
  rule). ThermoMPNN, the structures and the calibration data are not included; the scripts take a work folder as
  an argument.
- Neither is run by the harness. In `r2c_depmap_hdac.py` the local user name in two path lines is `[redacted]`
  (logged in `replicate/analysis/PORTING.json`, `public_copy_redactions`); `bubr1_decide.py` is unchanged.

## Coordinates and identifiers that remain, and why

- `chr15:40117088` (`models/regulatory/borzoi_score.py`, docstring "Child site"): the public dbSNP site
  rs576524605, the upstream allele reported by Ochiai et al. 2014. "Child site" means the site that was tested in
  the child; the child is reference there (register H02). It is public annotation, not a variant of the child.
- The eight HPO terms in `track1/ranking/ranking_v4.py`, `ranking_v4b.py` and `ranking_v4_fixed.py` are the
  organisers' phenotype terms for the child; they are also in the frozen rule `rules/RANKING_RULE_v4.md`, which
  must ship unchanged to keep its sha256.
- No local user or machine name is in this folder.

## A comment that disagrees with its code

- `models/regulatory/borzoi_score.py`: the docstring (line 3) says the eQTL positives have p < 1e-5; the code, which
  is what ran, uses p < 1e-4 (`P_MAX`). The file is kept verbatim; `replicate/EXTERNAL_STEPS.md` describes what the
  code does.

## Held back (not in this folder)

- The alignment and Manta launchers (our local paths are in them). A parameterised copy of the alignment launcher is
  `tools/fq2bam.sh`; the Manta step is external (SV-MANTA in `./replicate.sh plan`). Both commands, as run, are in
  `replicate/EXTERNAL_STEPS.md`.
- The Step 4 DICER1 depth script of SV-MANTA (our local BAM path, and two of the child's structural-variant calls
  written into it); its procedure is in `replicate/EXTERNAL_STEPS.md`.
- The SMN scripts as run (they still carry local path constants); the SMN step is external (H13-SMN in
  `./replicate.sh plan`).
- Scripts whose as-run copy hard-coded the candidate's coordinates: their ported copies are in `replicate/analysis/`
  (marked "held back or recovered" in `PORTING_LOG.md`).
- `rules/CNV_RULE_v1.md` (it contains a local file name; available to organisers on request; its sha256 is in
  `rules/CNV_RULE_v1.sha256`).

These folders were at the repository root until 2026-10-20; git records the move as renames, so
`git log --follow <file>` shows each file's history.
