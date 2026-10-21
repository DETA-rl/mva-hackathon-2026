# Porting log

Every analysis script the harness runs is a copy of the script that produced the register result, with
only path constants, hard-coded candidate coordinates and the candidate's protein-change labels replaced.
This file lists every replaced line.

Line edits that turn the as-run analysis scripts into the ported copies under replicate/analysis/. Only path constants, hard-coded candidate coordinates and the candidate's protein-change labels are replaced; three comment-only edits label public coordinates as public annotation. Each edit replaces exactly one line, so the ported file has the same number of lines as the original and every other line is byte-identical. The original text of an edited line is NOT stored here (some contain the organiser sample ID or candidate coordinates); its keyed hash (HMAC-SHA256; the authors keep the key with the originals) is stored in replicate/analysis/PORTING.json instead, because a plain sha256 of a short line can be reversed by trying candidates. Origins: 'candidates:' = copy of the as-run script kept privately by the authors (the repo as-run copy is named in repo_copy when it exists); 'recovered:' = script recovered from the session transcript that ran it. The as-run copies in this repository are under as_run/; where one of them named a local user name, disk identifier or session folder, that token is replaced by '[redacted]' in the public copy (column 'repo_copy_redactions' in PORTING.json); the audit then compares every other line.

How to check it: `./replicate.sh audit-port` verifies that each ported file still has the hash below and,
where the as-run copy is in this repository (column 'repo as-run copy', under `as_run/`), that the two files
differ only on the listed lines (lines marked `[redacted]` in a public as-run copy are skipped there). With the
private originals and the key: `./replicate.sh audit-port --candidates DIR --recovered DIR --root t2tests=DIR
--root asrun=DIR --key-file FILE`.

| ported file | origin | repo as-run copy | keyed hash before | sha256 after | edited lines |
|---|---|---|---|---|---|
| `replicate/analysis/track1/blind_exonic/child_exonic_calls.py` | candidates:track1/blind_exonic/child_exonic_calls_scratchcopy.py | held back or recovered | `224bcc88220f7bd6` | `723ed7c65bdffe3f` | 3, 4 |
| `replicate/analysis/track1/blind_exonic/gnomad_match.py` | candidates:track1/blind_exonic/gnomad_match.py | `as_run/track1/blind_exonic/gnomad_match.py` | `0a8a7a04a42fece1` | `c8e5677c068c61f7` | 3 |
| `replicate/analysis/track1/blind_exonic/blind_rare_exonic.py` | candidates:track1/blind_exonic/blind_rare_exonic.py | `as_run/track1/blind_exonic/blind_rare_exonic.py` | `e4359c6a9300bc50` | `0780af44fd3faff5` | 3 |
| `replicate/analysis/track1/blind_exonic/consequence.py` | candidates:track1/blind_exonic/consequence.py | `as_run/track1/blind_exonic/consequence.py` | `7e73566c9b8cf8b1` | `3218501830c95184` | 3, 4 |
| `replicate/analysis/track1/blind_exonic/consequence_fixed.py` | candidates:track1/blind_exonic/consequence_fixed.py | `as_run/track1/blind_exonic/consequence_fixed.py` | `f11d58ead7ad21bb` | `81f3721c1788c3e6` | 3, 4 |
| `replicate/analysis/track1/blind_exonic/summarize_consequence.py` | candidates:track1/blind_exonic/summarize_consequence.py | `as_run/track1/blind_exonic/summarize_consequence.py` | `7d244f02ab3837fd` | `26a7a7d533517dd1` | 2 |
| `replicate/analysis/track1/blind_exonic/compound_check.py` | candidates:track1/blind_exonic/compound_check.py | `as_run/track1/blind_exonic/compound_check.py` | `071265ec19afc225` | `e0bcbb151434d3f2` | 2 |
| `replicate/analysis/track1/blind_exonic/compound_check_fixed.py` | candidates:track1/blind_exonic/compound_check_fixed.py | `as_run/track1/blind_exonic/compound_check_fixed.py` | `42b98a25fbd9d745` | `4fc9b0de5bcd9c2c` | 2 |
| `replicate/analysis/track1/blind_exonic/validate_consequence.py` | candidates:track1/blind_exonic/validate_consequence.py | `as_run/track1/blind_exonic/validate_consequence.py` | `5f15b689220b2336` | `c00829d1cd438be8` | none (copied unchanged) |
| `replicate/analysis/track1/ranking/ranking_v1.py` | candidates:track1/ranking/ranking_v1.py | `as_run/track1/ranking/ranking_v1.py` | `707d5e84359734a1` | `1eaa642c6a395795` | 3, 4 |
| `replicate/analysis/track1/ranking/ranking_v1_fixed.py` | candidates:track1/ranking/ranking_v1_fixed.py | `as_run/track1/ranking/ranking_v1_fixed.py` | `931c84c22fb38d34` | `601ea247e618d7c4` | 3, 4 |
| `replicate/analysis/track1/ranking/ranking_v2.py` | candidates:track1/ranking/ranking_v2.py | `as_run/track1/ranking/ranking_v2.py` | `aced360fd358df04` | `c4df1a514d7c24b7` | 3, 4 |
| `replicate/analysis/track1/ranking/ranking_v2_fixed.py` | candidates:track1/ranking/ranking_v2_fixed.py | `as_run/track1/ranking/ranking_v2_fixed.py` | `e30ef5cd47710ce4` | `3c7c138bf49409ad` | 3, 4 |
| `replicate/analysis/track1/ranking/ranking_v3.py` | candidates:track1/ranking/ranking_v3.py | `as_run/track1/ranking/ranking_v3.py` | `f08f531a0dc34044` | `0804c56997c5bc09` | 3 |
| `replicate/analysis/track1/ranking/ranking_v3_fixed.py` | candidates:track1/ranking/ranking_v3_fixed.py | `as_run/track1/ranking/ranking_v3_fixed.py` | `8e0da3b94a0ff400` | `26f758f426c73e72` | 3 |
| `replicate/analysis/track1/ranking/ranking_v4.py` | candidates:track1/ranking/ranking_v4.py | `as_run/track1/ranking/ranking_v4.py` | `43a50b7f7b2977b0` | `e382075f8837a820` | 3 |
| `replicate/analysis/track1/ranking/ranking_v4b.py` | candidates:track1/ranking/ranking_v4b.py | `as_run/track1/ranking/ranking_v4b.py` | `3768288ce69413f9` | `f9cfa16356ea16bf` | 3 |
| `replicate/analysis/track1/ranking/ranking_v4_fixed.py` | candidates:track1/ranking/ranking_v4_fixed.py | `as_run/track1/ranking/ranking_v4_fixed.py` | `ad5c96718dc857b1` | `c2b91aab6dcd1151` | 3 |
| `replicate/analysis/track1/readlevel/bub1b_readcheck.py` | candidates:track1/readlevel/bub1b_readcheck.py | held back or recovered | `a80547b0b6fff451` | `899bf7a648d18715` | 3, 4, 5 |
| `replicate/analysis/track1/readlevel/cenatac_check.py` | candidates:track1/readlevel/cenatac_check.py | held back or recovered | `7005d4a885966a25` | `b32c52b2abf6892e` | 7, 8, 9, 10 |
| `replicate/analysis/track1/readlevel/p2_annot.py` | candidates:track1/readlevel/p2_annot.py | held back or recovered | `8944947b74dd4a33` | `0777d634720e6817` | 19 |
| `replicate/analysis/track1/readlevel/p1_tlen_bridging.py` | recovered:P1-phasing/p1_step4_tlen_bridging.py | held back or recovered | `15203dcf2c14f93d` | `1d25afb62a82d48e` | 2, 6, 15 |
| `replicate/analysis/track1/readlevel/p1_het_list_vcf.sh` | recovered:P1-phasing/p1_step2_het_list_vcf.sh | held back or recovered | `be37c4de9a9d3a96` | `42607f490eab00c3` | extracted (see note) |
| `replicate/analysis/track2/depmap/dep_corr.py` | candidates:track2/depmap/dep_corr.py | `as_run/track2/depmap/dep_corr.py` | `4243726fee06c197` | `db7d00f7cd2cd2a0` | none (copied unchanged) |
| `replicate/analysis/track2/depmap/lever_screen.py` | candidates:track2/depmap/lever_screen.py | `as_run/track2/depmap/lever_screen.py` | `45aab213500fd3bf` | `353150d69640f1ff` | 9 |
| `replicate/analysis/track2/depmap/p4_depmap_safety.py` | candidates:track2/depmap/p4_depmap_safety.py | `as_run/track2/depmap/p4_depmap_safety.py` | `374f1b19f73e1c98` | `b0be9c8e0ba94915` | 8 |
| `replicate/analysis/track2/power/power_guide.py` | recovered:T2-POWER-01/power_guide.py | held back or recovered | `89699b775566447d` | `eada0c4710d19283` | none (copied unchanged) |
| `replicate/analysis/track2/trials/ctgov_nmn_nr_query.sh` | recovered:T2-TRIAL-01/ctgov_nmn_nr_query.sh | held back or recovered | `d7a440e78b5b6bb5` | `f18998bcab6049ea` | none (copied unchanged) |
| `replicate/analysis/models/protein_rule/build_rule_controls.py` | candidates:models/protein_rule/build_rule_controls.py | `as_run/models/protein_rule/build_rule_controls.py` | `d2cdeba90c63f97e` | `98df6946060e4f36` | none (copied unchanged) |
| `replicate/analysis/models/protein_rule/build_protein_rule.py` | candidates:models/protein_rule/build_protein_rule.py | `as_run/models/protein_rule/build_protein_rule.py` | `0e21288887e63670` | `7814204b45fab33e` | 17, 18, 19, 153, 156 |
| `replicate/analysis/models/protein_rule/score.py` | candidates:models/protein_rule/score.py | held back or recovered | `f62b32ed68d6d958` | `9efef0416e4933c5` | 1, 36, 37, 144, 149 |
| `replicate/analysis/models/protein_rule/protein_calibration.py` | candidates:models/protein_rule/protein_calibration.py | `as_run/models/protein_rule/protein_calibration.py` | `c764b1cb8f2808ec` | `39fe2ac366d31ac2` | 3, 43 |
| `replicate/analysis/models/protein_rule/placement.py` | candidates:models/protein_rule/placement.py | `as_run/models/protein_rule/placement.py` | `10b4ceea17c11354` | `929baf48c145b6a1` | 1, 11, 17, 56 |
| `replicate/analysis/models/evo2/evo2_score_safe.py` | candidates:models/evo2/evo2_score_safe.py | `as_run/models/evo2/evo2_score_safe.py` | `fc5e718da524414f` | `0e9e5df4552b3613` | none (copied unchanged) |
| `replicate/analysis/models/evo2/configs/evo2-7b-1m.yml` | candidates:models/evo2/configs/evo2-7b-1m.yml | `as_run/models/evo2/configs/evo2-7b-1m.yml` | `f61198c2cfba69bc` | `1e06f12d29443814` | none (copied unchanged) |
| `replicate/analysis/models/evo2/evo2_auc_bootstrap.py` | recovered:M-EVO2-CAL-01/evo2_auc_bootstrap.py | held back or recovered | `e36872c91faad23b` | `486617a8b7e6ff53` | none (copied unchanged) |
| `replicate/analysis/track1/stage1_targeted/s01_sex_from_bai.py` | candidates:track1/stage1_targeted/s01_sex_from_bai.py | held back or recovered | `50b7ecc831352362` | `b5ef379fb4cfd308` | 3 |
| `replicate/analysis/track1/stage1_targeted/h01_cep57_dup11.py` | candidates:track1/stage1_targeted/h01_cep57_dup11.py | held back or recovered | `27d9880d6fe7ab2a` | `ef1d5c270e998d79` | 3 |
| `replicate/analysis/track1/stage1_targeted/h_batch.py` | candidates:track1/stage1_targeted/h_batch.py | held back or recovered | `babfb74d0d7ebafd` | `0d80656f414dae75` | 3, 4, 7, 21, 26 |
| `replicate/analysis/track1/sv_cnv/h08_depth.py` | candidates:track1/sv_cnv/h08_depth.py | held back or recovered | `3f162aabf7050b84` | `3dd19f0fcbad0864` | 3, 4 |
| `replicate/analysis/track1/sv_cnv/detection_limit.py` | candidates:track1/sv_cnv/detection_limit.py | held back or recovered | `77f69bea3b7b2ba2` | `a3d0c9f20e7b1215` | 3, 4 |
| `replicate/analysis/track1/sv_cnv/cnv_bins.py` | candidates:track1/sv_cnv/cnv_bins.py | held back or recovered | `099cfdad602ddd9b` | `eee521bad2d06455` | 3, 4, 5 |
| `replicate/analysis/track1/sv_cnv/cnv_call.py` | candidates:track1/sv_cnv/cnv_call.py | `as_run/track1/sv_cnv/cnv_call.py` | `c13c5563c242a6a3` | `95d8bcfd934af384` | 3, 39 |
| `replicate/analysis/track2/depmap/p5_depmap_safety.py` | t2tests:p5_depmap_safety.py | held back or recovered | `d36559c6cbe8025d` | `ebd738bb641d3ad0` | 14, 15 |
| `replicate/analysis/track1/spikein/spikelib.py` | asrun:as_run/track1/spikein/spikelib.py | `as_run/track1/spikein/spikelib.py` | `452e419d12324337` | `aaa8b1dfc36770b0` | 5, 6 |
| `replicate/analysis/track1/spikein/calls_param.py` | asrun:as_run/track1/spikein/calls_param.py | `as_run/track1/spikein/calls_param.py` | `43593801fccccee3` | `404cf0c3e044d6cd` | 4 |
| `replicate/analysis/track1/spikein/consequence_param.py` | asrun:as_run/track1/spikein/consequence_param.py | `as_run/track1/spikein/consequence_param.py` | `b5706278c379ff5c` | `a382aa6fa277bfc5` | 3, 4 |
| `replicate/analysis/track1/spikein/run_spikein.py` | asrun:as_run/track1/spikein/run_spikein.py | `as_run/track1/spikein/run_spikein.py` | `a769fb3fe4c8f9dd` | `8847de6e05e6e275` | 7, 8, 9 |
| `replicate/analysis/track1/spikein/validate.py` | asrun:as_run/track1/spikein/validate.py | `as_run/track1/spikein/validate.py` | `7999b35968cd008e` | `27dae2ea37a321df` | 7, 36 |
| `replicate/analysis/track1/spikein/analyze.py` | asrun:as_run/track1/spikein/analyze.py | `as_run/track1/spikein/analyze.py` | `6a7e1883ced957a9` | `816168c6314368ee` | 123 |
| `replicate/analysis/track1/spikein/feasibility.py` | asrun:as_run/track1/spikein/feasibility.py | `as_run/track1/spikein/feasibility.py` | `2551fa547b7d8a0e` | `cb423712613213e0` | 3, 4 |

## Edits, line by line

### `replicate/analysis/track1/blind_exonic/child_exonic_calls.py`

Origin: The copy in the project folder cannot be the one that ran: its line 29 is a SyntaxError on Python 3.12 and 3.13, and its header says "gene" while the stored table says "genes". The analysis_scripts copy (the origin above; same bytes as the scratchpad copy) writes the stored header; the harness reproduces the stored table byte for byte with it (BLIND-01A).

- line 3 (old line keyed hash `586738ba56ee6c64`): organiser VCF path constant -> config input
  new: `VCF = __import__("os").environ["REPL_VCF"]`
- line 4 (old line keyed hash `fffd605d1654845c`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `D = __import__("os").environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/blind_exonic/gnomad_match.py`

- line 3 (old line keyed hash `fffd605d1654845c`): project folder constant -> step folder in the workdir
  new: `D = __import__("os").environ["REPL_OUT"] + "/"`
- public as-run copy `as_run/track1/blind_exonic/gnomad_match.py`, line 3: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/track1/blind_exonic/blind_rare_exonic.py`

- line 3 (old line keyed hash `fffd605d1654845c`): project folder constant -> step folder in the workdir
  new: `D = __import__("os").environ["REPL_OUT"] + "/"`
- public as-run copy `as_run/track1/blind_exonic/blind_rare_exonic.py`, line 3: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/track1/blind_exonic/consequence.py`

- line 3 (old line keyed hash `3c109b5adb6a8b36`): project folder constant -> step folder in the workdir
  new: `HERE = os.environ["REPL_OUT"] + "/"`
- line 4 (old line keyed hash `263c6e9ac75b6fc6`): reference FASTA path constant -> config input
  new: `FA = os.environ["REPL_FASTA"]`
- public as-run copy `as_run/track1/blind_exonic/consequence.py`, line 4: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/track1/blind_exonic/consequence_fixed.py`

- line 3 (old line keyed hash `3c109b5adb6a8b36`): project folder constant -> step folder in the workdir
  new: `HERE = os.environ["REPL_OUT"] + "/"`
- line 4 (old line keyed hash `263c6e9ac75b6fc6`): reference FASTA path constant -> config input
  new: `FA = os.environ["REPL_FASTA"]`
- public as-run copy `as_run/track1/blind_exonic/consequence_fixed.py`, line 4: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/track1/blind_exonic/summarize_consequence.py`

- line 2 (old line keyed hash `2106a379cbf68e06`): input table path constant -> set by the harness (original or corrected table)
  new: `F = os.environ["REPL_CONSEQUENCE_TSV"]`

### `replicate/analysis/track1/blind_exonic/compound_check.py`

- line 2 (old line keyed hash `2106a379cbf68e06`): project folder constant -> step folder in the workdir
  new: `F = os.environ["REPL_OUT"] + "/child_exonic_consequence.tsv"`

### `replicate/analysis/track1/blind_exonic/compound_check_fixed.py`

- line 2 (old line keyed hash `0a0cdb5f988ea137`): project folder constant -> step folder in the workdir
  new: `F = os.environ["REPL_OUT"] + "/child_exonic_consequence_fixed.tsv"`

### `replicate/analysis/track1/ranking/ranking_v1.py`

- line 3 (old line keyed hash `2106a379cbf68e06`): project folder constant -> step folder in the workdir
  new: `F = os.environ["REPL_OUT"] + "/child_exonic_consequence.tsv"`
- line 4 (old line keyed hash `4c85b0892e3e052c`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/ranking_v1_summary.tsv"`

### `replicate/analysis/track1/ranking/ranking_v1_fixed.py`

- line 3 (old line keyed hash `0a0cdb5f988ea137`): project folder constant -> step folder in the workdir
  new: `F = os.environ["REPL_OUT"] + "/child_exonic_consequence_fixed.tsv"`
- line 4 (old line keyed hash `1863f67f5bdf2b8d`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/ranking_v1_summary_fixed.tsv"`

### `replicate/analysis/track1/ranking/ranking_v2.py`

- line 3 (old line keyed hash `2106a379cbf68e06`): project folder constant -> step folder in the workdir
  new: `F = os.environ["REPL_OUT"] + "/child_exonic_consequence.tsv"`
- line 4 (old line keyed hash `7a5c4574a1ae3946`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/ranking_v2_summary.tsv"`

### `replicate/analysis/track1/ranking/ranking_v2_fixed.py`

- line 3 (old line keyed hash `0a0cdb5f988ea137`): project folder constant -> step folder in the workdir
  new: `F = os.environ["REPL_OUT"] + "/child_exonic_consequence_fixed.tsv"`
- line 4 (old line keyed hash `a8718c4790fba499`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/ranking_v2_summary_fixed.tsv"`

### `replicate/analysis/track1/ranking/ranking_v3.py`

- line 3 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir
  new: `D = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/ranking/ranking_v3_fixed.py`

- line 3 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir
  new: `D = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/ranking/ranking_v4.py`

- line 3 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir
  new: `D = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/ranking/ranking_v4b.py`

- line 3 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir
  new: `D = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/ranking/ranking_v4_fixed.py`

- line 3 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir
  new: `D = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/readlevel/bub1b_readcheck.py`

- line 3 (old line keyed hash `ca9c6069525b79f2`): BAM path constant -> config input
  new: `BAM = os.environ["REPL_BAM"]`
- line 4 (old line keyed hash `97856212740cffbd`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/bub1b_readcheck.json"`
- line 5 (old line keyed hash `591b54476a573304`): hard-coded candidate coordinates -> taken at run time from the upstream ranking output (T1-CANDIDATE)
  new: `sites = [tuple(s) for s in json.loads(os.environ["REPL_CANDIDATE_SITES"])]`

### `replicate/analysis/track1/readlevel/cenatac_check.py`

- line 7 (old line keyed hash `1b8d01f43998068e`): GENCODE path constant -> config input
  new: `GTF = __import__("os").environ["REPL_GTF"]`
- line 8 (old line keyed hash `c1f384cbc7fa0187`): reference FASTA path constant -> config input
  new: `FA = __import__("os").environ["REPL_FASTA"]`
- line 9 (old line keyed hash `586738ba56ee6c64`): organiser VCF path constant -> config input
  new: `VCF = __import__("os").environ["REPL_VCF"]`
- line 10 (old line keyed hash `ca9c6069525b79f2`): BAM path constant -> config input
  new: `BAM = __import__("os").environ["REPL_BAM"]`

### `replicate/analysis/track1/readlevel/p2_annot.py`

- line 19 (old line keyed hash `68fd9f39463fa668`): organiser VCF path constant -> config input
  new: `    out = subprocess.run(["tabix", __import__("os").environ["REPL_VCF"], f"{ch}:{s}-{e}"], capture_output=True, text=True).stdout`

### `replicate/analysis/track1/readlevel/p1_tlen_bridging.py`

- line 2 (old line keyed hash `2fefcb6a7ed7fa12`): BAM path constant -> config input
  new: `bam = pysam.AlignmentFile(__import__("os").environ["REPL_BAM"], "rb")`
- line 6 (old line keyed hash `d92e0ce9aa3e6c8f`): hard-coded window around the candidate pair -> computed at run time from T1-CANDIDATE
  new: `for r in bam.fetch(contig, int(__import__("os").environ["REPL_P1_WINDOW_START"]), int(__import__("os").environ["REPL_P1_WINDOW_END"])):`
- line 15 (old line keyed hash `72559dd7156b7365`): hard-coded coordinates in the label and the gap threshold (a coordinate difference) -> computed at run time; the label keeps the original '>= 4000' wording
  new: `print("templates with |TLEN| >= 4000 (span from the first candidate site to the next het site needs >= " + __import__("os").environ["REPL_P1_GAP1"] + "):", sum(1 for t in tl if t >= int(__import__("os").environ["REPL_P1_GAP1"])))`

### `replicate/analysis/track1/readlevel/p1_het_list_vcf.sh`

The recovered file is one ssh command. The ported file keeps only the listing pipeline inside it (zcat | awk contig filter | awk interval filter | head -40), byte-for-byte except: the VCF path, the contig name and the two interval ends become environment variables. Dropped: the 'ls' of the data folder and the 'grep -m3 ##contig' header probe, which only printed diagnostics.

### `replicate/analysis/track2/depmap/lever_screen.py`

- line 9 (old line keyed hash `f9b380410a4205e9`): DepMap folder constant -> step folder in the workdir (DepMap files linked in by name)
  new: `DIR = __import__("os").environ["REPL_OUT"] + "/"`
- public as-run copy `as_run/track2/depmap/lever_screen.py`, line 9: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/track2/depmap/p4_depmap_safety.py`

- line 8 (old line keyed hash `f9b380410a4205e9`): DepMap folder constant -> step folder in the workdir (DepMap files linked in by name)
  new: `DIR = __import__("os").environ["REPL_OUT"] + "/"`
- public as-run copy `as_run/track2/depmap/p4_depmap_safety.py`, line 8: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/models/protein_rule/build_protein_rule.py`

- line 17 (old line keyed hash `37cb3de31e9966ad`): GENCODE path constant -> config input
  new: `GTF = os.environ["REPL_GTF"]`
- line 18 (old line keyed hash `131e6120e04c2b31`): reference FASTA path constant (two lines) -> config input
  new: `FA = os.environ[`
- line 19 (old line keyed hash `32920451263f9b00`): reference FASTA path constant (two lines) -> config input
  new: `    "REPL_FASTA"]`
- line 153 (old line keyed hash `4d090a5e49f9fd1f`): privacy: hard-coded residue number and amino acid of the candidate missense -> taken at run time from T1-CANDIDATE (same check; not run when no candidate is available)
  new: `_cand = __import__("json").loads(__import__("os").environ.get("REPL_CANDIDATE_RESIDUE", "null")); child_ok = (proteins.get(_cand[0], "")[_cand[1] - 1:_cand[1]] == _cand[2]) if _cand else None`
- line 156 (old line keyed hash `e2dabe003e6f7843`): privacy: same residue as line 153 in the printed label
  new: `print(f"{_cand[0]} residue {_cand[1]} is {_cand[2]} (child check):" if _cand else "candidate residue not checked (no candidate in this run) (child check):", child_ok)`

### `replicate/analysis/models/protein_rule/score.py`

- line 1 (old line keyed hash `5b5e9bbd7d52d597`): privacy: the docstring named the candidate's protein change (comment-only)
  new: `"""Score ClinVar controls + the candidate missense (from T1-CANDIDATE) with local protein LMs and AlphaMissense lookup.`
- line 36 (old line keyed hash `0ef3e49a40711ce4`): hard-coded candidate missense (genomic coordinate) -> taken at run time from T1-CANDIDATE
  new: `CHILD = dict(__import__("json").loads(__import__("os").environ["REPL_CHILD_PROTEIN_VARIANT"]),`
- line 37 (old line keyed hash `b520b81294431b3b`): continuation of the line above
  new: `             review="child")`
- line 144 (old line keyed hash `503ff3de94931c56`): privacy: the printed label named the candidate's protein change; generic label
  new: `        print(f"candidate_missense {name}: not in table")`
- line 149 (old line keyed hash `85cdcd366fd2e637`): privacy: the printed label named the candidate's protein change; generic label, same numbers
  new: `    print(f"candidate_missense {name}: damage={cv:.4f} percentile_among_controls={pct:.3f} n_controls={len(allv)}")`

### `replicate/analysis/models/protein_rule/protein_calibration.py`

- line 3 (old line keyed hash `1addb54f2b998893`): privacy: the docstring named the candidate's protein change (comment-only)
  new: `Also reports the child's candidate missense damage and its percentile among controls (only if the model passes).`
- line 43 (old line keyed hash `8dbe9e6788bd27ef`): privacy: the printed label named the candidate's protein change; generic label, same numbers
  new: `            print(f"   child candidate_missense damage={cv:.4f} percentile among {len(allv)} controls={pct:.3f}")`

### `replicate/analysis/models/protein_rule/placement.py`

- line 1 (old line keyed hash `8c529d2032f24d7a`): privacy: the docstring named the candidate's protein change (comment-only)
  new: `"""PRE-REG-D: place BUB1B I909T, L1012P and the candidate missense (from T1-CANDIDATE) among the calibration controls (ESM-1v, ESM-2, AlphaMissense).`
- line 11 (old line keyed hash `1484be2f396e35de`): project folder constant -> step folder in the workdir
  new: `BASE = __import__("os").environ["REPL_OUT"] + "/"`
- line 17 (old line keyed hash `30c1f575c52d3621`): the child's allele is taken at run time from T1-CANDIDATE; the two literature alleles stay as written
  new: `ALLELES = [("I909T", 909, "I", "T"), ("L1012P", 1012, "L", "P")] + [tuple(a) for a in __import__("json").loads(__import__("os").environ["REPL_CANDIDATE_ALLELES"])]`
- line 56 (old line keyed hash `c453a32627f26d9e`): same allele names as line 17, no longer hard-coded
  new: `        if p[7] in tuple(a[0] for a in ALLELES):`
- public as-run copy `as_run/models/protein_rule/placement.py`, line 11: `[redacted]` in place of the local user name and disk identifier in a path

### `replicate/analysis/track1/stage1_targeted/s01_sex_from_bai.py`

- line 3 (old line keyed hash `b126f389a521498e`): BAM path constant -> config input
  new: `bam = __import__("os").environ["REPL_BAM"]`

### `replicate/analysis/track1/stage1_targeted/h01_cep57_dup11.py`

- line 3 (old line keyed hash `b126f389a521498e`): BAM path constant -> config input
  new: `bam = __import__("os").environ["REPL_BAM"]`

### `replicate/analysis/track1/stage1_targeted/h_batch.py`

- line 3 (old line keyed hash `ca9c6069525b79f2`): BAM path constant -> config input
  new: `BAM = __import__("os").environ["REPL_BAM"]`
- line 4 (old line keyed hash `586738ba56ee6c64`): organiser VCF path constant -> config input
  new: `VCF = __import__("os").environ["REPL_VCF"]`
- line 7 (old line keyed hash `c42a21e6b5c19572`): label only (comment): the coordinate is public annotation, not child data
  new: `    # H02: bases at chr15:40117088 (1-based); public annotation: dbSNP rs576524605, the upstream allele reported by Ochiai 2014; not a variant of the child`
- line 21 (old line keyed hash `9967f4865fffcdc0`): label only (trailing comment): the coordinates are public gene annotation, not child data
  new: `    out["H03_BUB1B_intron_region"] = rates("chr15", 40160984, 40221137)  # public gene annotation: the BUB1B gene span (GENCODE v44) with a few bp of flank; not a variant position`
- line 26 (old line keyed hash `fad41ecbe31823e9`): label only (trailing comment): the coordinates are public gene annotation, not child data
  new: `    d_naa = depth("chrX", 153928799, 153935083)  # public gene annotation: the NAA10 gene span (GRCh38) with flank; not a variant position`

### `replicate/analysis/track1/sv_cnv/h08_depth.py`

- line 3 (old line keyed hash `ca9c6069525b79f2`): BAM path constant -> config input
  new: `BAM = os.environ["REPL_BAM"]`
- line 4 (old line keyed hash `2aac9f5632fc37b6`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/h08_depth_sampled.json"`

### `replicate/analysis/track1/sv_cnv/detection_limit.py`

- line 3 (old line keyed hash `ca9c6069525b79f2`): BAM path constant -> config input
  new: `BAM = os.environ["REPL_BAM"]`
- line 4 (old line keyed hash `a00e2f82e530ff76`): project folder constant -> step folder in the workdir
  new: `OUT = os.environ["REPL_OUT"] + "/detection_limit.json"`

### `replicate/analysis/track1/sv_cnv/cnv_bins.py`

- line 3 (old line keyed hash `ca9c6069525b79f2`): BAM path constant -> config input
  new: `BAM = os.environ["REPL_BAM"]`
- line 4 (old line keyed hash `263c6e9ac75b6fc6`): reference FASTA path constant -> config input
  new: `FA = os.environ["REPL_FASTA"]`
- line 5 (old line keyed hash `f8360d0d1f02e239`): project folder constant -> step folder in the workdir
  new: `OUTD = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/sv_cnv/cnv_call.py`

- line 3 (old line keyed hash `5c8687b3ea3966d4`): project folder constant -> step folder in the workdir
  new: `D = os.environ["REPL_OUT"] + "/"`
- line 39 (old line keyed hash `98d177a8f0fe064e`): project folder constant -> step folder in the workdir
  new: `json.dump(out, open(os.environ["REPL_OUT"] + "/cnv_calls_v1.json", "w"), indent=1)`

### `replicate/analysis/track2/depmap/p5_depmap_safety.py`

Origin: Run by the t2-tests agent on 2026-10-20 (its output folder on the analysis machine); not staged in the repo before this port.

- line 14 (old line keyed hash `f9b380410a4205e9`): DepMap folder constant -> step folder in the workdir (DepMap files linked in by name)
  new: `DIR = __import__("os").environ["REPL_OUT"] + "/"`
- line 15 (old line keyed hash `5bee7a588d315eb4`): output folder constant -> step folder in the workdir
  new: `OUT = __import__("os").environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/spikein/spikelib.py`

- line 5 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `D = os.environ["REPL_OUT"] + "/"`
- line 6 (old line keyed hash `b0beb7bb1d65d4a5`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `W = os.environ["REPL_OUT"] + "/"`

### `replicate/analysis/track1/spikein/calls_param.py`

Origin: machine-generated by make_params.py from the frozen child_exonic_calls.py by two exact text replacements (input and output path only); the unified diff is as_run/track1/spikein/calls_param.py.diff. The frozen original's own ported copy is replicate/analysis/track1/blind_exonic/child_exonic_calls.py.

- line 4 (old line keyed hash `fffd605d1654845c`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `D = __import__("os").environ["REPL_OUT"] + "/"`
- public as-run copy `as_run/track1/spikein/calls_param.py`, line 4: `[redacted]` in place of the local user name, disk identifier or session folder in a path

### `replicate/analysis/track1/spikein/consequence_param.py`

Origin: machine-generated by make_params.py from the frozen consequence_fixed.py by two exact text replacements (input glob and output path only); the unified diff is as_run/track1/spikein/consequence_param.py.diff. The frozen original's own ported copy is replicate/analysis/track1/blind_exonic/consequence_fixed.py.

- line 3 (old line keyed hash `3c109b5adb6a8b36`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `HERE = os.environ["REPL_OUT"] + "/"`
- line 4 (old line keyed hash `263c6e9ac75b6fc6`): reference FASTA path constant (on a removable disk) -> config input
  new: `FA = os.environ["REPL_FASTA"]`
- public as-run copy `as_run/track1/spikein/consequence_param.py`, line 4: `[redacted]` in place of the local user name, disk identifier or session folder in a path

### `replicate/analysis/track1/spikein/run_spikein.py`

- line 7 (old line keyed hash `f63c5d63ad8d3fe2`): the authors' virtual-environment interpreter -> the interpreter running this step. The two helper scripts this driver launches as subprocesses therefore run outside the audit guard that covers the driver itself; each writes only to the output path the driver passes.
  new: `PY = sys.executable`
- line 8 (old line keyed hash `9a3b48580cd0f28f`): organiser VCF path constant -> config input
  new: `VCF = os.environ["REPL_VCF"]`
- line 9 (old line keyed hash `263c6e9ac75b6fc6`): reference FASTA path constant (on a removable disk) -> config input
  new: `FA = os.environ["REPL_FASTA"]`
- public as-run copy `as_run/track1/spikein/run_spikein.py`, line 9: `[redacted]` in place of the local user name, disk identifier or session folder in a path

### `replicate/analysis/track1/spikein/validate.py`

- line 7 (old line keyed hash `f63c5d63ad8d3fe2`): the authors' virtual-environment interpreter -> the interpreter running this step (same subprocess note as run_spikein.py line 7)
  new: `PY = sys.executable`
- line 36 (old line keyed hash `14f0cc8e2708c638`): path constant of the authors' 10-row draft submission CSV -> config input. The CSV is child-derived and is not in this repository; the harness supplies the rows it needs from the upstream ranking artifacts (replicate/helpers/draft_rows_csv.py), which makes gate G1e a self-consistency check rather than the independent comparison it was in the original run
  new: `draft = list(csv.DictReader(open(os.environ["REPL_DRAFT_CSV"])))`

### `replicate/analysis/track1/spikein/analyze.py`

- line 123 (old line keyed hash `b4580caacadc30ce`): path constant of the authors' 10-row draft submission CSV -> config input; it is read only to attach the EPCR column to its rows, and no metric of this step depends on it
  new: `src = os.environ["REPL_DRAFT_CSV"]`

### `replicate/analysis/track1/spikein/feasibility.py`

- line 3 (old line keyed hash `52330fe83ecc52f7`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `D = os.environ["REPL_OUT"] + "/"`
- line 4 (old line keyed hash `b0beb7bb1d65d4a5`): project folder constant -> step folder in the workdir (inputs are linked in by name)
  new: `W = os.environ["REPL_OUT"] + "/"`

## Other public copies with redacted lines

Files in `as_run/` and `citations/` that the harness does not run. Each differs from the file that ran only on
the listed lines, where a local user name, a disk identifier or a session folder became `[redacted]`.

| file | lines | sha256 of the public copy |
|---|---|---|
| `as_run/track1/alignment/dl.py` | 3 | `f28e88e604e52db7` |
| `as_run/track1/alignment/dv_run.sh` | 5 | `2aee8686de76729d` |
| `as_run/track1/alignment/dv_run_split.sh` | 6 | `dce63db496d079f3` |
| `as_run/track1/alignment/split_fallback.sh` | 6 | `dce63db496d079f3` |
| `as_run/track1/blind_exonic/find_pending.py` | 2 | `9aea2f357d7cb266` |
| `as_run/track2/evidence_checks/checkA_build.py` | 2, 151 | `1bddb2adcee99f4b` |
| `as_run/track2/evidence_checks/checkA_extract.py` | 4, 5 | `c8782b0cb9e277b0` |
| `as_run/track2/evidence_checks/checkA_verbatim.py` | 2 | `37c330a441d7fc8c` |
| `as_run/track2/evidence_checks/checkB_build.py` | 2 | `bdd9170061ae5c3a` |
| `as_run/track2/evidence_checks/checkC_verify.py` | 2, 3 | `50844bbedccf09b4` |
| `citations/t1_rows.py` | 3, 58, 59 | `59c06c7ce06ef465` |
| `citations/t1cite_cite.py` | 2 | `f7980c3947148082` |
| `as_run/track2/hdac_screen/r2c_depmap_hdac.py` | 11, 12 | `fdcbbdedfcbaa3f6` |
| `as_run/track1/spikein/make_params.py` | 16 | `1a1155329b4cdd5e` |
| `as_run/track1/spikein/calls_param.py.diff` | 6, 8 | `738a26ce4ea647bb` |

## Scripts the harness runs on another input (no line changed)

- `track1/ranking/ranking_v4b.py` in step RANK-V4BF: run unchanged in a step folder where the CORRECTED v3 summary (output of RANK-V3F) is linked under the name ranking_v3_summary.tsv, which is the file name the script reads. Why: BUG-V4-CHRM: ranking_v4_fixed.py was derived from ranking_v4.py and lacks the Amendment 1 chrM skip (ranking_v4b.py line 48). The frozen rule is RANKING_RULE_v4.md including Amendment 1; ranking_v4b.py is the as-run code of that rule, so the harness applies it to the corrected input instead of editing ranking_v4_fixed.py. RANK-V4F still runs ranking_v4_fixed.py to reproduce what was recorded; the candidate (T1-CANDIDATE) is taken from RANK-V4BF.

- `track1/blind_exonic/summarize_consequence.py` in step C-FIX-01: run unchanged with REPL_CONSEQUENCE_TSV pointing at the corrected table. Why: the register reports summary counts for both tables; the summary script was written for the original table

- `track1/blind_exonic/consequence_fixed.py` in step T1-CANDIDATE: its tables and functions are loaded by replicate/helpers/candidate_protein.py (text before the per-call loop, as validate_consequence.py does) to write protein notation for the candidate calls. Why: no coordinate in code: the candidate's protein changes are computed, not typed

Full hashes are in `replicate/analysis/PORTING.json`.
