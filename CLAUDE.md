# Working in this repository with Claude Code

This repository is the code and evidence release for two reports submitted to a rare-disease
genomics challenge. One report prioritises candidate variants in a single child's exome and names
one candidate. The other evaluates mechanism hypotheses for the affected gene, independently of
any individual's genotype. Both reports are in `reports/`, as the submitted PDF and as the
Markdown it was built from.

The input data are controlled-access and are **not** here. Readers hold them under their own
agreement. Some steps therefore cannot run from this repository alone, and the harness says which
and why rather than failing silently.

## What to read first

| you want to | go to |
|---|---|
| understand the claims and where each is evidenced | `README.md` |
| run or modify the replication harness | `replicate/CLAUDE.md` and `replicate/AGENTS.md` |
| know what a step should produce | `replicate/expected.yaml` |
| run a step the harness never runs | `replicate/EXTERNAL_STEPS.md` |
| check a citation | `references/BIBLIOGRAPHY.md` |
| see what was fixed before the analysis ran | `rules/` and `preregistration/` |

## Map of the repository

528 files. Agents are bad at finding things by guessing, so this is the whole tree at two levels,
with what each directory is for. Paths are from the repository root.

```
.gitignore  CITATION.cff  LICENSE  NOTICE        licences and attribution
PORTING_LOG.md                                   every edit made when a script was ported
README.md                                        start here: the claims and where each is evidenced
config.example.yaml                              harness configuration template
replicate.sh                                     the entry point: check | plan | run | report | audit-port

replicate/                     19   the harness itself
  steps.py                          the 53 step declarations; read this before believing a step runs
  runner.py  cli.py  plan.py        execution, command line, dependency plan
  compare.py                        applies each metric's tolerance
  expected.yaml                     501 recorded metrics with provenance and tolerance
  check.py  config.py  system.py    machine and input verification
  hashing.py  porting.py            file hashing, ported-script audit
  report.py  registry.py            report writing, step registry
  framework.py                      the step base class and run_sh / run_py
  EXTERNAL_STEPS.md                 the six steps that never execute, and how to run them by hand
  CLAUDE.md  AGENTS.md              these notes
  _sandbox/run.py            1      the write and network audit hook
  analysis/                 52      the scripts the harness runs
  helpers/                   4      small re-derivations that need no dataset

tests/                         9    73 test cases on synthetic fixtures, no dataset needed
env/                           8    pinned environments: quick, test, full freeze, container, system
tools/                         7    leak scan, public-tree export, downloads, exon BED, fq2bam

rules/                        14    the frozen ranking and consequence rules with their sha256
preregistration/               2    what was fixed before each run, and the redacted log
  frozen/                      3    the pre-registration texts that are published
  spikein/                     7    the 1,611-trial spike-in test: criteria, result, tables
  rowmap/                      9    the row-building rule test and the submitted CSV
  nonchoices/                 59    the 181-molecule drug screen: criteria, scripts, per-batch results

reports/                       4    both submitted reports, each as PDF and as Markdown source
references/                    5    ClinGen list and the bibliography index
  papers/                    225    one folder per cited work: metadata, abstract, licence
citations/                     8    the scripts that resolve and verify every citation

as_run/                        1    historical record, NOT runnable; see PORTING_LOG.md first
  track1/                     47    as-run Track 1 scripts
  track2/                     19    as-run Track 2 scripts
  models/                     12    as-run model scripts
intermediates/                 3    public-derived outputs supplied so quick-tier steps can run
```

### Where to look first, by question

| question | file |
|---|---|
| What does this project claim? | `README.md` |
| Does a step actually run? | `replicate/steps.py`, then `replicate/EXTERNAL_STEPS.md` |
| What value should a step produce? | `replicate/expected.yaml` |
| Why did a comparison fail? | `replicate/compare.py` and the metric's own `tol` |
| What was fixed before the run? | `rules/` and `preregistration/frozen/` |
| Where is the 181-molecule screen? | `preregistration/nonchoices/` |
| Where is the spike-in test? | `preregistration/spikein/` |
| Is a citation real? | `references/BIBLIOGRAPHY.md` and `references/papers/<pmid>/` |
| What changed when a script was ported? | `PORTING_LOG.md` |
| What is deliberately absent, and why? | `README.md`, the "Held back" section |

## House rules

These are not style preferences. They are why the repository is worth reading.

1. **A verdict is never changed after a result is seen.** Fix code, log the fix, keep the verdict.
2. **Measure, do not infer.** Three figures in this project were reasoned rather than measured and
   all three were wrong.
3. **A declared step is not a step that runs.** Read the function it calls before saying it ran.
4. **If an instruction disagrees with what you measure, write neither version and say so.**
5. **Negative and inconclusive results are reported in full**, with the value that produced them.
6. **Never edit a recorded expectation to make a run pass.** The comparison is the point.
7. No em dashes in anything that ships.

`replicate/EXTERNAL_STEPS.md`, section "Reproducing this work: what counts as agreement", sets the
standard for judging any result here. It is two standards, not one: scripted steps are
deterministic and a difference is a difference, while steps that apply a written criterion to
published sources agree on verdicts rather than on wording. Read it before concluding that
something failed to reproduce.

## Agents

Heavy work here was delegated to agents working one bounded task at a time. The dispatch pattern,
the roster, and the rules that made it work are in `replicate/CLAUDE.md`, together with how to
install a scientific capability an agent lacks.

The short version: one agent per bounded task, a self-contained brief, the criterion frozen before
the run, four agents at once at most, deterministic work never gets an agent, and never correct a
running agent. Stop it, fix the brief, relaunch.
