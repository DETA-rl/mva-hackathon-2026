# Working in `replicate/` with Claude Code

This folder is the replication harness for the two reports in `reports/`. It reruns the recorded
analyses and compares each result against the value stored at the time of the original run.

Run every command below **from the repository root**, not from this folder.

## Where things are

The map of the repository, two levels deep with what each directory holds and a table of which
file answers which question, is in the root ../CLAUDE.md and ../AGENTS.md. It is kept in one
place so it cannot drift from itself.

## How a result is judged

`expected.yaml` holds **501 recorded metrics**. Each one declares its own comparison in `tol`:

| `tol` | count | meaning |
|---|---|---|
| `exact` | 304 | byte or value equality |
| `{round: n}` | 159 | equal after rounding to n decimals |
| `set` | 24 | same members, order irrelevant |
| `{abs: x}` | 4 | within an absolute tolerance |
| `{sigfig: n}` | 4 | equal to n significant figures |
| `subset` | 3 | observed is a subset of recorded |
| `{lt: x}` | 3 | below a threshold |

Read the metric before interpreting a difference. A value is not wrong because it differs; it is
wrong because it fails the comparison that metric declares.

`exact_if` names the inputs and artifacts whose hashes must match before `tol` applies. When they
differ, `tol_alt` is used if present, otherwise the metric is **NOT COMPARABLE**. A higher number
does not by itself establish a pass.

**Never edit `expected.yaml` to clear a failure.** The comparison is the only thing this folder is
for. If a value differs, establish which is right and report the difference.

Each expected value carries its provenance: `register:` came from the append-only hypothesis
register kept during the analysis; `harness:` was recorded by this harness from the stored output
of the original run.

## Statuses

`PASS`, `FAIL` (a metric failed its comparison or was not observed), `INCONCLUSIVE` (inputs
differed so the comparison was unavailable), `ERROR` (execution failed), `NOT RUN` and `REFUSED`
(execution never started; the recorded reason says why).

The documented baseline carries three FAILs that the authors' own run also produced. Investigate a
difference before calling it a regression.

## Running it

```bash
export MVA_WORK=/your/scratch          # required even for `plan`
export MVA_DATA=/the/organisers/data
export MVA_REF=/public/references      # singular REF, not REFS
export MVA_MODELS=/model/weights       # full tier only

cp config.example.yaml config.yaml     # gitignored
./replicate.sh check                   # machine, input hashes, rule hashes
./replicate.sh plan                    # dependency and selection plan
./replicate.sh run --tier quick        # CPU only; writes both report files
./replicate.sh report                  # prints the report path
./replicate.sh audit-port              # ported scripts against their as-run originals
```

The workdir must be **outside this repository** and either empty or already owned by the harness.
`check` and `plan` write files there, so neither is read-only.

`plan` fails with "environment variable MVA_WORK is used in the config but not set" if the exports
are skipped. That is the first thing most readers hit.

`plan` checks selection, network permission, rules and upstream artifacts. It does **not** check
that inputs exist, that companion indexes are present, or that resources suffice; execution does.
A step marked `run` by the planner can still refuse at run time.

`config.example.yaml` defines paths and guards. `replicate/expected.yaml` records the input hashes
and where each input came from. Neither supplies the data.

## Environment

Python 3.13. Quick-tier work needs `env/requirements-quick.txt`; the tests also need
`env/requirements-test.txt`. Read `env/README.md` before installing the full GPU freeze: it cannot
be installed with one ordinary `pip install -r`, and pointing at it for CPU work pulls CUDA you do
not need.

```bash
python3 -m pytest -q      # 73 test cases, synthetic fixtures, no dataset needed
```

## What runs, and what does not

53 steps are declared. The documented outsider quick run executes **16** with the organisers'
data, a BAM and public references. The authors' **41**-step quick run also supplies stored
intermediates and the rule file that is held back; see `intermediates/README.md` and the root
README. Raw inputs alone do not reach 41, so a refusal is often correct rather than a bug.

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

## Which copy to edit

The harness runs `replicate/analysis/`. `as_run/` holds the historical record and is not a
runnable copy. Ported scripts are hash-checked against the porting manifest, so editing the wrong
copy breaks `audit-port`. Read `PORTING_LOG.md` first, and keep original and corrected variants
both present: an intentionally preserved bug is evidence, not a defect to fix.

## Guards you must not disable

`_sandbox/run.py` installs a Python audit hook: a write that resolves outside the workdir raises
`PermissionError`, symlinks included, and sockets are blocked in steps not declared as network
steps. Native code such as htslib and CUDA sits outside that hook, which is why the harness checks
that `.fai`, `.tbi` and `.bai` exist before htslib would need to create one next to an input.

`write_guard: warn` exists for debugging. Do not ship a run made with it.

Keep patient-derived data, raw logs, harness state and step outputs out of this repository. The
shareable outputs are the two report files under `<workdir>/results/`.

## House rules

1. Never change a recorded verdict after seeing a result. Fix code, log the fix, keep the verdict.
2. Measure, do not infer. Three figures in this project were reasoned rather than measured and all
   three were wrong.
3. A declared step is not a step that runs. Read the function it calls.
4. If an instruction you were given disagrees with what you measure, write neither version and say
   so.
5. Negative and inconclusive results are reported in full, with the value that produced them.
6. No em dashes in anything that ships.

## Running a team of agents

Parts of this work were produced by several agents working in parallel on bounded tasks. The two
skills the authors used are not public, so the transferable content is written out here. You do
not need them installed.

### The tool

In Claude Code, `Agent` spawns a subagent. Launch a fan-out's agents **in a single message** or
they run one after another instead of concurrently. Each spawn is a fresh context with no memory
of your conversation, so brief it like a new hire. A `fork` type inherits your context but ignores
a model override; use a fresh type when you want a different model.

### The roster that was used

| Role | Model | Effort | Count |
|---|---|---|---|
| Explorer, one per area of the repo | Haiku | low | 0 to 4 |
| Planner, writes the PRD and acceptance criteria | Opus | high | 1 |
| Plan reviewer, one lens each | Haiku | medium | 1 to 3 |
| Architect, cuts the work into packages | Opus | high | 1 |
| Implementer, one per package, isolated worktree | Sonnet | medium | 1 per package |
| Cross-cutting reviewer, reads the whole diff | Haiku | medium | 1 |
| Second-provider reviewer and final judge | a different vendor's model | high | 1 |

**Hard cap: four agents running at once.** Larger fan-outs run in waves. Pass `effort`
explicitly; the default is lower than these roles need.

### The rules that made it work

- **Deterministic work never gets an agent.** Tests, linters, `git`, a grep for a known symbol,
  reading one or two files: the orchestrator does those itself. Spawning an agent for them wastes
  a context and adds a summarisation step between you and the truth.
- **Vet every fan-out before launching it.** Write one line per proposed agent: role, exact input,
  expected output, and why you cannot do it yourself. Then judge each as **KEEP**, **MERGE into
  <id>**, or **DROP**. Keep an agent only when the material is too large or too separate for one
  context, or when independence is the point. The authors sent this proposal to a different
  vendor's model so the judgement was not made by the same model that wrote it.
- **Disjoint files or no parallelism.** Two implementers editing one file in separate worktrees
  produce conflicts. The architect's file list per package is the contract; enforce it before
  launching.
- **The orchestrator does not read raw output.** Agents write their result to a file; you read the
  verdict table, not the transcript. This is what keeps a long pipeline inside one context.
- **Never correct a running agent.** Stop it, fix the brief, relaunch from scratch. A corrected
  agent carries the confusion of both versions. This cost the authors several hours.
- **One report at the end, in a fixed shape.** Ask for a table with one row per input and a
  verdict column, so the result can be diffed against the recorded one.

### Capabilities a scientific agent needed here

The screens in `preregistration/` were not run by a general-purpose agent reading the web. Each
batch agent was given a narrow capability set and nothing else. If you are reproducing one, these
are the abilities it needs, however you obtain them:

- **Literature lookup by identifier**, not by search engine: resolve a PMID or DOI against PubMed,
  Europe PMC or Crossref and read the record, so a citation is checked rather than recalled.
- **Citation handling**: convert between PMID, DOI and PMCID, and emit a stable reference entry.
  `citations/collect_references.py` in this repository does exactly this for all 110 cited works
  and is the worked example.
- **Public database queries**: ChEMBL, PubChem, UniProt, ClinicalTrials.gov and DGIdb for the
  drug-to-gene universe; DepMap for the dependency flags.
- **Ordinary statistics**: bootstrap intervals, proportion tests and power calculations. No step
  here needs anything exotic.

A general model with a shell and network access can do all of it. The point of giving an agent a
narrow capability set is not capability, it is that a narrow agent cannot wander off the
criterion.

### Giving an agent a scientific capability it lacks

Claude Code skills can be installed on demand from a public collection, one at a time:

```bash
npx -y skills add <owner>/<repo> -s <skill-name> -g -a claude-code -y   # installs to ~/.claude/skills/<name>/
gh api repos/<owner>/<repo>/contents/scientific-skills --jq '.[].name'  # list what a collection offers
```

The working rule, in order:

1. **Check locally first.** Glob `~/.claude/skills/*/SKILL.md`. A skill installed once stays.
2. **Match the need to one skill name**, not to a category. If unsure, read the first twenty lines
   of its `SKILL.md` from the collection before installing.
3. **Install only that one.** Never bulk-install a collection: it floods the context with
   descriptions of skills the task will never use, which is the opposite of the point.
4. **Read it and follow it** for the current turn; it auto-loads on the next matching request.
5. **If nothing fits, say so** and use ordinary tools. A forced match is worse than none.

The capability names that mattered for the work in `preregistration/`, as a starting list:
`paper-lookup` (PubMed, arXiv, OpenAlex, Crossref, Semantic Scholar, bioRxiv),
`citation-management` (BibTeX, DOI and PMID conversion), `database-lookup` (public databases
including PubChem, ChEMBL, UniProt and ClinicalTrials.gov), `depmap`, `pysam`, `esm`,
`statistical-analysis`, `scientific-writing`, `scholar-evaluation`, `peer-review`.

None of this is required to reproduce the harness. It matters when reproducing a judgement step,
where the agent has to read literature and apply a criterion rather than run a script.

### Reproducing a delegated judgement

The screens in `preregistration/` were run this way. Their recorded verdicts are the thing to
reproduce, not the wording: none of this is deterministic. Give the fresh context the criterion,
the exact input list, the admissible evidence, the verdict vocabulary and the exclusions. Keep the
criterion unchanged. Report missing evidence instead of working around it. A reproduction that
overturns a recorded conclusion needs a second independent review before it is accepted.

The literal briefs were not kept as files. Do not reconstruct one and present it as the original.
