# Pre-registration: what was fixed in advance, and what each test returned

| folder | what is in it |
|---|---|
| `frozen/` | the two pre-registration texts the spike-in tests ran under, with `SHA256SUMS.txt`. `PRE_REG_SPIKEIN_EPCR.md` is the file that ran, unchanged; `PRE_REG_ROWMAP.md` is a public copy whose passages citing the authors' internal research notes are not reproduced, with every rule definition unchanged and the frozen original's sha256 in the log |
| `spikein/` | the result of the EPCR spike-in test (register `PRE-REG-SPIKEIN-EPCR`) |
| `rowmap/` | the result of the ROW-MAP rule test (register `PRE-REG-ROWMAP`) |
| `REDACTED_PREREG_LOG_SELF_RECORDED.md` | what was pre-registered and when, as recorded at the time, with read-level values removed |

Each result folder holds the same five kinds of file: `RESULT.md` (every figure with its interval, the decisions as
the pre-registered rules produced them, and the limits), `DEVIATIONS.md` (every departure from the frozen text, and
there is one in each test), the timestamped run log, the aggregate output as JSON (`summary*.json`, `sanity*.json`,
and for the spike-in the gate record `val_G1.json`), and the pre-freeze feasibility counts.

## What is here and what is not

These are statistics about the method: trial counts, recalls, intervals, per-gene breakdowns and decisions. The
per-trial tables and the row-level outputs are not here. `trials.tsv` and `alleles.tsv` are bulk, and the harness
rebuilds both byte for byte; `real_rows.tsv` and the two proposed CSVs hold rows of the child's calls that are not
part of the published Track 1 answer. "What is deliberately not in this repository" in the main README lists them
with the reason for each.

## How to check these numbers

The EPCR spike-in is three harness steps. From the repository root, with the organisers' VCF and the pinned ClinVar
release configured:

```
./replicate.sh run --steps PRE-REG-SPIKEIN-G1,PRE-REG-SPIKEIN-TRIALS,PRE-REG-SPIKEIN
```

That rebuilds the masked background, the spike pools, all 1,611 trials and the EPCR vector, and compares 67 values
against `replicate/expected.yaml`, including the sha256 of the two trial tables. It takes about 40 seconds after the
upstream exonic chain has run. The steps are refused, rather than run to produce incomparable numbers, if the
ClinVar release supplied is not the one the test was pre-registered against.

The ROW-MAP test is not a harness step: it imports the organisers' `evaluation.py`, which is their code and is not
in this repository, and two of its gates pin files that are not shipped. `replicate/EXTERNAL_STEPS.md`
(PRE-REG-ROWMAP) gives the procedure, the inputs and where to get each one, the command as it ran, and what cannot
be regenerated. The one figure the two tests share is a cross-check a reader can make: stratum `A-d0` under the
draft rule gives 73.83 mean rank points, which is the spike-in's own stratum A expected score (73.8, step
PRE-REG-SPIKEIN, metric `mean_rank_points`).

## Two results that run against the method

Both are kept here in full rather than summarised away, and both are in the Track 1 report.

- The ranking rules missed their pre-registered rank-1 bar: 0.533 [0.477, 0.589] against a bar of 0.80
  (`spikein/RESULT.md`, decision D1).
- The consequence classifier labelled 0 of 311 stop-loss alleles as `stop_lost` (decision D3). The blind spot is
  listed in the methods and under "Disclosed deviations" in the main README.

The phenotype layer also traded recall for specificity in a direction the pre-registration called harm: decision D5
records v4 at 0.533 against v3 at 0.840 in the primary stratum, with unrelated recessive genes falling from 0.760 to
0.010. `spikein/RESULT.md` section 3 states both halves of that trade.

## Editorial note, 2026-10-21: the AlphaMissense licence question in `rowmap/RESULT.md`

`rowmap/RESULT.md` section 9 records, as an open item at the time of the run, that the AlphaMissense table it read
is "licensed CC BY-NC-SA 4.0 (file header)" and that whether this use counts as non-commercial was UNVERIFIED. That
question has since been resolved and the answer is that there is no non-commercial term: the predictions were
re-licensed to CC BY 4.0 on 2024-03-13, and the Zenodo metadata and description of record 10813168, the README.pdf
distributed with the tables and the upstream README all say CC BY 4.0. The header line inside the downloaded table
is stale. "AlphaMissense licence" under step 3 of the main README gives the detail and the sources, and `NOTICE`
carries the attribution.

The RESULT file is not edited. It is the record of what was known when the test ran, and a record is not rewritten
after the fact; this note sits beside it instead.
