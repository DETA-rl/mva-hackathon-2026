# AGENTS.md: `replicate/`

Replication harness for the two reports in `reports/`. It reruns the recorded analyses and
compares each result against the value stored at the time of the original run.

## Where things are

The map of the repository, two levels deep with what each directory holds and a table of which
file answers which question, is in the root ../CLAUDE.md and ../AGENTS.md. It is kept in one
place so it cannot drift from itself.

## Working here

Run the commands below **from the repository root**, not from this folder.

`replicate/steps.py` declares the steps and parses their outputs. `runner.py` executes them,
`compare.py` applies each metric's tolerance, `expected.yaml` holds the recorded values and their
provenance.

The harness runs `replicate/analysis/`. `as_run/` holds the historical record, not runnable
copies. Ported scripts are hash-checked against the porting manifest, so read `PORTING_LOG.md`
before changing one and keep original and corrected variants both present. An intentionally
preserved bug is evidence, not a defect to fix.

Keep frozen rules and recorded results unchanged; log a correction beside the original record
rather than editing it. Keep patient-derived data, raw logs, harness state and step outputs out of
this repository. The shareable outputs are the two report files under `<workdir>/results/`.

## Environment

Python 3.13. Quick-tier work needs `env/requirements-quick.txt`; the tests also need
`env/requirements-test.txt`. Read `env/README.md` before installing the full GPU freeze: it cannot
be installed with one ordinary `pip install -r`, and using it for CPU work pulls CUDA you do not
need.

`REPLICATE_PYTHON` selects the harness interpreter and, unless the config's `python` key overrides
it, the analysis interpreter too.

## Setup

```bash
export MVA_WORK=/your/scratch          # required, even to run `plan`
export MVA_DATA=/the/organisers/data
export MVA_REF=/public/references      # singular REF
export MVA_MODELS=/model/weights       # full tier only
cp config.example.yaml config.yaml     # gitignored
```

The workdir must be outside the repository and either empty or already owned by this harness.
`check` and `plan` create files there, so neither is read-only.

`config.example.yaml` defines paths and guards. `replicate/expected.yaml` records input hashes and
acquisition details, including URLs where they exist. Neither supplies the data.

## Commands

| command | what it does |
|---|---|
| `./replicate.sh check` | machine, input hashes, frozen rule hashes |
| `./replicate.sh plan` | dependency and selection plan; does not verify every input or resource |
| `./replicate.sh run --tier quick` | CPU only; writes both report files |
| `./replicate.sh run --tier full` | adds the GPU and network steps |
| `./replicate.sh report` | prints the report path; `run` is what writes the files |
| `./replicate.sh audit-port` | ported scripts against their as-run originals |
| `python3 -m pytest -q` | 73 test cases on synthetic fixtures, no dataset needed |

## Verification model

`expected.yaml` holds 501 recorded metrics. Each declares its comparison in `tol`: 304 are
`exact`, 159 compare after rounding, 24 compare as sets, and the rest use absolute tolerance,
significant figures, subset membership or a threshold. Read the metric before interpreting a
difference.

`exact_if` names the inputs and artifacts whose hashes must match before `tol` applies. When they
differ, `tol_alt` applies if supplied; otherwise the metric is NOT COMPARABLE. A higher number
does not by itself establish a pass.

Do not edit `expected.yaml` to make a run green. If a value differs, establish which one is
correct and report the difference. That comparison is the entire purpose of this folder.

Each expected value carries its source: `register:` came from the append-only hypothesis register
kept during the analysis; `harness:` was recorded by this harness from the stored output of the
original run.

FAIL means a metric failed its comparison or was not observed. INCONCLUSIVE means the comparison
was unavailable because inputs differed. ERROR means execution failed. NOT RUN and REFUSED mean
execution never started; read the recorded reason. The documented baseline includes three FAILs
that the authors' own run also produced, so investigate a difference before treating it as a
regression.

## Step accounting

53 steps are declared. The documented outsider quick run executes 16 with the organisers' data, a
BAM and public references. The authors' 41-step quick run also supplies stored intermediates and
the rule file that is held back; see `intermediates/README.md` and the root README. Raw inputs
alone do not reach 41.

Use `plan` for dependencies and selection and `check` for inputs and environment. Execution
additionally checks indexes, resources and existing step folders, so a step the planner marks
`run` can still refuse.

Six steps **never execute in any tier**: their execute function raises `StepError("external")`
unconditionally. `EXTERNAL_STEPS.md` documents each one with the manual procedure, the tools and
inputs it needs, and a verdict on how far it can be recovered at all: RECOVERABLE, or PARTLY
RECOVERABLE with the specific thing that was not recorded. Read that verdict before spending time
on one.

That file also sets the standard this folder is judged by, in its section "Reproducing this work:
what counts as agreement". Two standards, not one. The scripted steps are deterministic and a
difference is a difference. The steps that apply a written criterion to published sources can
yield different wording and, at a threshold, a different verdict; agreement there is not textual,
and a different verdict from the same criterion and the same quotation is evidence about the
criterion rather than a failure to reproduce. Read it before judging any result here.

Read the function before attributing a non-run to the tier.

## Sandbox

`_sandbox/run.py` installs a Python audit hook: writes resolving outside the workdir raise
`PermissionError`, symlinks included, and sockets are blocked in steps not declared as network
steps. Native code such as htslib and CUDA is outside the hook, so the harness verifies `.fai`,
`.tbi` and `.bai` exist beforehand. `write_guard: warn` is for debugging only.

## Running several Codex agents

Codex does not spawn subagents inside a session. It runs **independent sessions on a shared local
app-server daemon**, and you address them by thread:

```bash
codex exec "<brief>"                     # start a non-interactive session
codex exec -s read-only "<brief>"        # a worker that judges must not be able to edit
codex exec --output-last-message out.md  # capture the final response as a file
codex exec --output-schema schema.json   # make that response structured
codex agents                             # browse every session on the daemon
codex queue --thread <uuid|name> --message "<text>"
codex resume --last                      # continue a session
codex fork --last                        # branch one
codex review                             # a code review pass over the repo
```

So a "team" here is several `codex exec` processes started in parallel, tracked by `codex agents`,
each writing its result through `--output-last-message` rather than to a shared file. That matters
for a read-only worker: it cannot write a verdict table from its shell, so ask for the table in
its final response and let the caller save it.

Reasoning effort is set per run with `-c model_reasoning_effort=...` and the accepted values
depend on the model you select. A session started this way has no network access, so a brief that
assumes it can fetch a page will fail: give it the files, or do the retrieval first and pass the
results in.

Use the tools and permissions your current session actually has. This file does not require you to
delegate anything, and it does not choose a model for you.

## Reproducing a delegated judgement

Several screens in `preregistration/` were produced by agents applying a frozen criterion, one
bounded batch at a time. Their recorded verdicts are what to reproduce, not the wording: none of
this is deterministic.

Give the fresh session the criterion, the exact input list, the admissible evidence, the verdict
vocabulary and the exclusions. Keep the criterion unchanged. Report missing evidence instead of
working around it; some screens deliberately omit raw abstracts from this repository, and missing
evidence is a limit rather than a verdict. A reproduction that overturns a recorded conclusion
needs a second independent review before it is accepted.

The literal briefs were not kept as files. Do not reconstruct one and present it as the original.

## Capabilities a reproducing agent needs

The screens in `preregistration/` need a narrow set of abilities, not a general research agent:
literature lookup by PMID or DOI against PubMed, Europe PMC or Crossref; conversion between PMID,
DOI and PMCID; queries to ChEMBL, PubChem, UniProt, ClinicalTrials.gov and DGIdb for the
drug-to-gene universe; DepMap for dependency flags; and ordinary statistics such as bootstrap
intervals and power calculations.

`citations/collect_references.py` is the worked example: it resolves all 110 cited works and
writes the bibliography. Nothing here needs a capability beyond a shell and network access.

## Conventions

1. A verdict is never changed after a result is seen. Bugs are fixed and logged; verdicts stand.
2. Figures are measured, not inferred.
3. A declared step is not a step that runs.
4. When an instruction conflicts with a measurement, write neither and say so.
5. Negative and inconclusive results are reported in full, with the value that produced them.
6. No em dashes in shipped text.
