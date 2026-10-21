# The drug-level screen: 181 molecules, one by one

This folder holds the frozen criteria, the scripts, the raw query returns and the per-batch
records behind the statement in the Track 2 report, Section 15.1, that 181 molecules were
evaluated individually against pre-registered criteria and none was kept.

## What this screen was, and what it was not

It read published records and database entries and applied the frozen criteria in
`PRE_REG_NONCHOICES.md` to them. It ran no new experiment, used no cell or sample of the child,
and administered nothing to anyone. The dependency data it draws on measure what happens when a
gene is disabled in cancer cell lines, which is not a test of any molecule.

**Keeping no molecule is a statement about the published record, not about efficacy.** It means
that for none of the 181 did a source establish the proposed mechanism on BUBR1 in the direction
the report needs. UNRESOLVED removes nothing and clears nothing. No entry here is a safety
finding about any product, and no absent flag is a safety clearance. Each `RESULT_*.md` repeats
that clause, because it governs how every row in it should be read.

## What is here

| file | what it is |
|---|---|
| `PRE_REG_NONCHOICES.md` | the criteria, frozen and hashed before the screen ran |
| `PRE_REG_NONCHOICES.sha256` | the hash recorded for the frozen original |
| `BATCHES.md`, `BATCHES.sha256` | how the 181 were divided into the five batches, and its hash |
| `armA_screen.py`, `armB_screen.py`, `assemble.py`, `batches.py` | the scripts that built the universe from the two arms and assembled the batches |
| `armA_raw.json`, `armB_raw.json` | what those queries returned, as returned |
| `eval_B2/` … `eval_B4c/` | one folder per batch: its `RESULT_*.md`, the scripts it ran and the tables they produced |

## The public copy of the pre-registration differs from the frozen original

One sentence was removed from `PRE_REG_NONCHOICES.md` for this public copy. It made a claim
about what the report does not do with respect to other hackathon participants, which this
repository states nothing about in either direction. Nothing else changed: no criterion, no
threshold, no verdict, and the clause that carries the same methodological point, that a name is
treated with no attribution, no count of where it came from and no statement about who proposed
it, is unchanged and immediately above where the removed sentence stood.

- frozen original, as recorded before the run: `ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4`
- this public copy: `a6ffd6204ff5ce1efbfb6acc2cb3f2e7ccae6b3deff47f77defca0ce7ec4fc36`

`PRE_REG_NONCHOICES.sha256` records the frozen original's hash, which is the one the
`RESULT_*.md` files verified before each batch ran.

## How to check this screen

The criteria are the record, not any one reader's judgement of them. To re-run the screen:

1. Read `PRE_REG_NONCHOICES.md`. It states each criterion, its threshold and what decides a
   removal, an UNRESOLVED and a keep.
2. Take the molecule list from `BATCHES.md`.
3. Apply the criteria to the published record for each molecule. Every `RESULT_*.md` names the
   sources it used by PMID, accession or API endpoint, so the evidence is retrievable from the
   source rather than from our copy of it. Abstracts are retrievable from PubMed by the PMIDs
   listed; raw abstract dumps are deliberately not shipped here.
4. Compare your verdicts with ours.

Applying written criteria to published sources is a judgement, so a reader may differ on a
borderline row. A verdict of yours that differs from ours, reached from the same criterion and
the same evidence, is a finding about our criterion, and we would want it reported as such.

The parts that are arithmetic rather than judgement are checked by the harness: see
`replicate/EXTERNAL_STEPS.md`.
