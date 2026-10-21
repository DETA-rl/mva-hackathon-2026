# PRE-REG-NONCHOICES: candidate universe and evaluation plan for the "Non-choices" section

Test ID: T2-NONCHOICE-01
Agent: nonchoice-prereg-2
Status at freeze: FROZEN BEFORE THE SCREEN RUNS. The procedure in Section 2 is fixed here and
run afterwards. The evaluation rules in Section 5 are fixed here and applied afterwards. The
only database or literature calls made before this freeze were the four endpoint-syntax probes
disclosed in Section 1.3, and their returns are recorded there.

Non-clinical clause: this is a hypothesis-screening document about published mechanism, label
and database facts. It is not clinical advice, it proposes no dose or regimen for any person,
and nothing in it may be read as a recommendation to administer anything. No patient-derived
data is used. Every query leaving this machine carries a gene symbol, a drug name, a mechanism
term or a PMID, and nothing else.

---

## 0. Purpose, and what this section is for

The Track 2 report states which medicines we carried forward. It does not yet state, with our
own tests, why we did not carry forward the medicines that a reader would expect to see
proposed for this mechanism. This test builds that candidate universe by a stated procedure and
fixes, in advance, the rules by which each entrant is kept or removed.

The purpose is discipline, not advocacy. A universe assembled after seeing the answers would
prove nothing. So the procedure is fixed first, the universe is whatever the procedure returns,
and the evaluation reuses criteria already frozen elsewhere in this project, unchanged.

Stated plainly, and binding on the write-up: if a drug in this universe passes every frozen
test, it is KEPT AS A CANDIDATE and joins our ranked list under the unchanged rule. We do not
hide a winner that our own procedure found. A "Non-choices" section that could only ever
produce non-choices would be a rhetorical device, not a test.

## 1. Honesty clause: what is already known to the author at freeze time

Listed so that no finding below can be presented as having been reached in ignorance.

### 1.1 Known about the project's own prior results

- Our carried candidates are niacin, arimoclomol, sodium phenylbutyrate (4-PBA), fingolimod,
  NMN and NR (TRACK2_REPORT_v2.md Section 5). Nicotinamide was dropped by T2-CLASS-01 on
  criterion C4.
- Already removed or demoted by pre-registered tests, with the test named in the report
  Section 6: mTOR inhibitors (everolimus, sirolimus) on the T2-P4 dependency flag, MTOR
  fraction 0.986; APC/C inhibitors on CDC20 1.000, ANAPC4 0.994, UBE2C 0.767; PLK4 inhibitors
  on PLK4 0.982; KIF18A inhibition on KIF18A 0.885.
- RESULT-R2C-HDAC excluded the class I HDAC inhibitor class on mechanism direction, with zero
  entrants, over seven named drugs: valproate, sodium phenylbutyrate, vorinostat, romidepsin,
  belinostat, panobinostat, givinostat. The direction verdict there is class-level.
- RESULT-R2B-EXPOSURE removed fingolimod on mechanism direction and exposure, and left every
  other candidate E-UNRESOLVED.
- RESULT-R2D-R2E declared criterion C4 NON-DISCRIMINATING. That finding is why Section 5.4
  below reports C4 but does not let it remove anything. This decision is made here, before the
  universe is known.
- PRE-REG-B found no co-dependent lever gene against BUB1B among 17,916, and RESULT-R2D-R2E
  then showed that rule had power 0.514 against its own pre-registered minimum effect. So a
  negative DepMap co-dependency result is NOT available to this test as a removal ground, and
  Section 5 does not use one.

### 1.2 Known about popularity, stated because it would otherwise look like a discovery

An internal, unpublished completeness list of drug names proposed elsewhere for this disease
exists in this project's private material. The author has read it. Three consequences are fixed
here:

1. It is NOT a source for the reportable universe. The universe comes from Section 2 only.
2. It is used ONLY as a completeness check on Section 2, at the level of drug names.
3. A drug that only the internal list contributes enters the universe tagged
   **"also considered"**, with no attribution of any kind, no count of how many places it came
   from, and no statement about who proposed it.

The author therefore already expects, before running Section 2, that certain names will appear:
NAD+ precursors and the proteostasis agents we already carry, plus mTOR inhibitors, senolytic
combinations, readthrough agents, proteasome inhibitors, antimalarials of the chloroquine
class, metformin, and HSP90 inhibitors. Recording the expectation in advance is the only way a
later "we found these" is honest. If Section 2 reaches them, that is a confirmed expectation and
is labelled as one, not as a discovery.

### 1.3 Endpoint-syntax probes run before the freeze, with their returns

Four calls were made to validate query syntax before fixing it here. Disclosed in full:

- DGIdb GraphQL, gene BUB1B: returned one interaction, drug "GEMCITABINE PRODRUG LY2334737",
  `approved: false`. Under the Section 2 inclusion rule it does not enter the universe.
- ChEMBL `target.json?target_synonym__icontains=NAMPT`: 7 targets, first CHEMBL1744525
  (Nicotinamide phosphoribosyltransferase, Homo sapiens, UniProt P43490).
- ChEMBL `mechanism.json?target_chembl_id=CHEMBL1744525`: 2 records, CHEMBL190412 and
  CHEMBL566757, both "Nicotinamide phosphoribosyltransferase inhibitor". Approval status not
  retrieved at probe time.
- PubMed esearch for query L1 of Section 2.2: count 451. No record was opened.

No other database or literature call was made before this freeze.

---

## 2. The reportable procedure (fixed here, run after the freeze)

Two independent arms. The universe is the UNION of arm A and arm B, then the completeness check
of Section 3. Every entrant carries its source: a database record ID, or a PMID, or the
"also considered" tag.

### 2.1 Arm A: gene-to-drug database screen

**Gene set, fixed and exhaustive for this test (45 symbols).** Chosen to cover every mechanism
in play in this project, not chosen by what returns drugs.

| Mechanism block | HGNC symbols |
|---|---|
| BUB1B and direct checkpoint partners | BUB1B, BUB3, MAD2L1, CDC20, TTK, BUB1 |
| NAD+ metabolism | NAMPT, NAPRT, NMNAT1, NMNAT2, NMNAT3, NMRK1, NMRK2 |
| Sirtuins | SIRT1, SIRT2 |
| Acetyltransferases acting on BubR1 | CREBBP, EP300, KAT2B |
| Proteostasis | HSF1, HSPA1A, HSP90AA1, HSP90AB1 |
| APC/C and ubiquitin-proteasome route documented for BubR1 | ANAPC1, ANAPC2, ANAPC4, ANAPC5, ANAPC11, CDC16, CDC23, CDC27, UBE2C, UBE2S, PSMB1, PSMB2, PSMB5 |
| PP2A | PPP2CA, PPP2R1A, PPP2R5A, PPP2R5B, PPP2R5C, PPP2R5D, PPP2R5E |
| Aneuploidy-tolerance and mitotic targets with documented inhibitors | KIF18A, PLK4, AURKB, MTOR, FBXW7 |

KAT2B is the HGNC symbol for PCAF and is included under the brief's "PCAF if documented"
clause; whether a BubR1-directed acetylation role is documented for it is a question for the
evaluation, not for admission to the universe.

**A1. DGIdb.** POST to `https://dgidb.org/api/graphql`, query
`{genes(names:[...]){nodes{name interactions{drug{name conceptId approved} interactionTypes{type}}}}}`,
genes submitted in batches of at most 10 symbols. Retain an interaction only if
`drug.approved == true`. Record drug name, DGIdb `conceptId`, gene, and interaction type.

**A2. ChEMBL.** Four chained steps, all GET, `Accept: application/json`:
1. UniProt accession per symbol: `https://rest.uniprot.org/uniprotkb/search` with
   `query=(gene_exact:SYM) AND organism_id:9606 AND reviewed:true`, `fields=accession,gene_primary`.
2. ChEMBL target: `https://www.ebi.ac.uk/chembl/api/data/target.json?target_components__accession__in=<accessions>`,
   keep `organism == "Homo sapiens"` and `target_type == "SINGLE PROTEIN"`.
3. Mechanisms: `https://www.ebi.ac.uk/chembl/api/data/mechanism.json?target_chembl_id__in=<ids>`,
   paginated to exhaustion.
4. Approval and name: `https://www.ebi.ac.uk/chembl/api/data/molecule.json?molecule_chembl_id__in=<ids>`,
   retain `max_phase == 4`. Record `pref_name`, `molecule_chembl_id`, `mechanism_of_action`,
   target symbol.

**A3. Supplements.** Dietary supplements are in scope and are mostly absent from A1 and A2's
approval flags. A molecule entering through A1 or A2 without an approval flag is admitted if it
is a dietary supplement, established at evaluation time under C1. No separate supplement
database is queried, because none of the catalogued public databases carries an authoritative
supplement register; this is recorded as a coverage limit of the procedure, not worked around.

**Inclusion rule for arm A, fixed:** admitted if DGIdb `approved == true` OR ChEMBL
`max_phase == 4`. These are the database's own approval flags and are treated as an admission
ticket only. Regulatory class is established independently at evaluation under C1, and a drug
whose approval cannot be confirmed there is resolved as UNRESOLVED on C1, never silently kept
and never silently dropped.

**Bound on work, fixed:** at most 100 API calls across arm A. If a single gene returns more than
50 approved drugs, all are counted, the count is reported, and the drugs are carried as a
**mechanism class** rather than as individual rows (Section 5.6). If the call bound is reached
before the gene set is exhausted, the run stops and the unscreened genes are listed by name as
an incomplete arm. Failing visibly beats a plausible completion.

### 2.2 Arm B: literature screen

PubMed E-utilities esearch, `db=pubmed`, `retmax=200`, no date filter, no language filter.
Four queries, fixed verbatim:

- **L1:** `(BUB1B[tiab] OR BubR1[tiab]) AND (drug[tiab] OR treatment[tiab] OR inhibitor[tiab] OR activator[tiab])`
- **L2:** `"mosaic variegated aneuploidy"[tiab] AND (treatment[tiab] OR therapy[tiab])`
- **L3:** `aneuploidy[tiab] AND "drug repurposing"[tiab]`
- **L4:** `(BUB1B[tiab] OR BubR1[tiab]) AND (stabilization[tiab] OR stabilisation[tiab] OR "protein level"[tiab] OR degradation[tiab])`

L4 is added because L1 to L3 are mechanism-neutral and the arm must also reach sources about
raising BubR1 abundance specifically. It is fixed here, before any result is seen.

**Extraction rule, fixed:** titles and abstracts are retrieved by esummary and efetch. A drug or
supplement name is extracted only if it appears in the title or abstract as a named molecule
given to cells, animals or people. Drug-name recognition uses the Drugs@FDA bulk `Products.txt`
lexicon already on the box (51,900 rows, public file, used as a name list only), plus manual
reading of the abstracts of L2, which is small. A class name without a named molecule
("HDAC inhibitors") is recorded as a class, not as a drug. Every extracted name carries its PMID.

**Bound, fixed:** at most 200 records per query are considered. If a query returns more, the
count is reported and the arm is marked truncated for that query.

### 2.3 What arm A and arm B cannot do, stated now

- Neither arm reaches a drug whose rationale for this mechanism has never been written down.
  The universe is a screen of published and curated knowledge, not of pharmacological space.
- DGIdb and ChEMBL approval flags are curation, not a regulator's register. They can be stale
  in both directions. C1 is what settles class.
- Arm B indexes titles and abstracts. A drug named only in a full text is missed.
- Neither arm is a systematic review. There is no PRISMA flow, no second screener and no
  inter-rater agreement, and the write-up must not imply otherwise.

---

## 3. Completeness check against the internal list

After arms A and B have run and the union is fixed, the internal completeness list is read at
the level of drug names only. Any name it contains that the procedure did not reach is added to
the universe tagged **"also considered"**.

Fixed now: the tag carries no source, no count, no team name, and no statement of popularity.
The report wording for these rows is fixed here as "also considered, reached outside the stated
screen", and nothing more. This clause exists to satisfy the binding report policy, and it also
keeps the honest fact that our screen did not reach them.

## 4. Normalisation and the already-evaluated split

- **Names** are normalised to INN where an INN exists; otherwise to the USAN or the common
  chemical name, with the alternates recorded. Salt and ester forms collapse to the parent
  (sodium phenylbutyrate and glycerol phenylbutyrate collapse to phenylbutyrate, with the forms
  recorded, because the frozen tests act on the moiety).
- **Already evaluated** means a drug or its mechanism class has a disposal in this project's
  register or in a frozen R2 result. Each such row names the deciding test. The pre-set list of
  what counts as already evaluated: our six carried candidates; nicotinamide (T2-CLASS-01);
  mTOR, APC/C, PLK4 and KIF18A inhibitors (T2-P4); the seven class I HDAC inhibitors
  (RESULT-R2C-HDAC); fingolimod (RESULT-R2B-EXPOSURE).
- **New** means everything else. Only new drugs are evaluated in the next stage, and only new
  drugs go into the batches of Section 6.

---

## 5. The evaluation, pre-registered here and run later

Every criterion below is reused unchanged from a rule frozen earlier in this project. No
threshold is new, and none is set after seeing the universe.

### 5.1 C1, regulatory class and paediatric label

Source and reading identical to criterion C1 of PRE-REG-T2-CLASS-01: Drugs@FDA and openFDA
(drugsfda and label endpoints), DailyMed SPLs, EMA medicine pages, queried by drug name only.
Reading: "Rx" if every authorised oral or systemic single-agent product is prescription; "OTC"
if an authorised non-prescription drug product exists; "no authorised drug product" if none
exists, in which case the class for the rule is dietary supplement. A supplement sold under
DSHEA is not an FDA approval and never reads as OTC. The paediatric label statement is recorded
verbatim and is **reported, not used to exclude**, matching the report's Section 3 constraint.

### 5.2 C2, DepMap dependency flags for the named targets

Method identical to the T2-P5 script `p5_depmap_safety.py`, itself identical to
`p4_depmap_safety.py` (sha256 c7d87310a11c2448ba2a3d2845dd8bd6750d6c675a1e7ff27d607ed6d889f524):
DepMap 24Q4 `CRISPRGeneEffect.csv` and `Model.csv` on the box at
`~/Documents/HACKATON/_private/public_data/depmap_24Q4/`; column matched on the symbol before
" ("; blood lineage is OncotreeLineage in {Myeloid, Lymphoid}; per gene, the fraction of lines
with Chronos gene effect < -0.5 over all lines with a value, plus the blood-lineage median.

Flag rule, unchanged: flag a gene if fraction >= 0.25. A gene with no column is reported
"not measured", never 0, and never counts as an unflagged target.

Carried caveat, unchanged and not used to re-flag anything: a CRISPR knockout is a
loss-of-function proxy in cancer lines, never normal marrow. No flag is a safety verdict and no
absent flag is a safety clearance.

**A DepMap flag alone does not remove a drug here.** It is the RANKING-RULE-T2 safety tie-break
input. The T2-P4 removals of the mTOR, APC/C, PLK4 and KIF18A routes already stand on the
register and are not re-litigated; this test does not extend that precedent to new drugs,
because doing so would be a new rule.

### 5.3 C3, exposure and mechanism direction

The frozen R2-B rule, applied verbatim: PRE_REG_R2B_EXPOSURE.md, sha256
`338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534` (verified against the file
at freeze time). Per arm: achieved free plasma concentration against C_demo, the concentration
at which the proposed mechanism was demonstrated in its cited source; R = C_free / C_demo; the
direction definitions of its Section 4 including the node rule, the transcriptional override
and the stress-dependence clause; the outcomes E-FAIL, E-PASS, E-WEAK, E-UNRESOLVED of its
Section 5; and its aggregation rule. Unit conversions per its Section 3.1.

E-UNRESOLVED never removes anything. Absence of exposure data is never read as safety.

### 5.4 C4, reported but NOT used to remove. Decided here, before the universe is known

RESULT-R2D-R2E declared criterion C4 (mechanism direction by plasma concentration against an
enzyme IC50) NON-DISCRIMINATING, on four independent flags: the measured intracellular baseline
in the headline human compartment is 2.6 to 7.1 uM and the supplements do not move it; the
assay cofactor is 21 to 83-fold off; and the exposure behind the original DROP is above the
pre-fixed ordinary-dose window.

Therefore, in this test, C4 is computed and reported for every entrant for which it can be
computed, and it removes nothing. This is fixed now, before the universe is known, so that it
cannot be applied selectively to a drug whose answer is later found inconvenient.

Note the distinction, which must not be collapsed in the write-up: C4 is the plasma-versus-IC50
instrument and is non-discriminating. C3's direction limb is the R2-B node and override rule,
which rests on primary sources about what a mechanism does to BUBR1 or to the checkpoint, not
on a concentration comparison. C3 can still remove. C4 cannot.

### 5.5 C5, evidence grade

RANKING-RULE-T2, unchanged: G1 human data on BUBR1 or aneuploidy endpoints in a clinical or
patient-derived setting, replicated; G2 patient-derived cell data on BUBR1 protein or mitotic
endpoints; G3 mouse or cell-line data on BUBR1 protein or checkpoint endpoints, not contradicted
by an independent source; G4 mechanism or pathway evidence only, or G3 with a published
contradiction. Ranking by grade, ties by the C2 safety tie-break, and a supplement or OTC drug
above a prescription drug only on a strictly higher grade.

### 5.6 Class-level disposal, fixed

Where a mechanism class is excluded by a frozen class-level result, every member of that class
takes the class disposal and the deciding test is named. This applies to the class I HDAC
inhibitors, excluded on direction by RESULT-R2C-HDAC over seven named drugs including one with
a chronic paediatric indication. A class disposal is used only where the deciding evidence is
itself class-level; otherwise each drug is evaluated individually.

### 5.7 Outcomes, exhaustive

- **REMOVED.** One deciding test is named, with the value that decided it. Removal is on
  regulatory class, mechanism direction or exposure. **Never on a safety claim**, and a removal
  is never stated as a safety finding about any drug.
- **KEPT AS CANDIDATE.** Passes every criterion that returned a reading. It then joins the
  ranked list under RANKING-RULE-T2 unchanged, at whatever rank its grade and tie-break give.
  No clause permits keeping it out of the ranking because we did not propose it first.
- **UNRESOLVED.** A datum needed by a criterion is missing. The missing datum and the search
  route that failed are both named. UNRESOLVED never removes and is never read as safety.

### 5.8 Falsifiers, fixed per outcome

| Outcome I might reach | What would falsify it |
|---|---|
| The universe is small (under about 20 new drugs) | Arm A returning more approved drugs per gene than the Section 2.1 bound anticipated, which would mean the gene set, not the biology, produced a short list |
| Every new drug is REMOVED | Any single drug passing C1, C3 and C5 with a reading on each. One such drug falsifies the premise that our carried list was already complete |
| A class disposal is sound | A primary source showing a member of the class acting oppositely to the class verdict at an achievable exposure |
| "Also considered" rows are a small residue | The internal list contributing more names than arms A and B together, which would mean the stated procedure is a poor instrument and the report must say so |
| The procedure is reproducible | Any arm whose counts cannot be reconciled on a re-run |

---

## 6. Deliverable after this freeze

`BATCHES.md`, listing the new drugs grouped into at most four batches by mechanism, each drug
with its claimed target or mechanism and its source (a database record ID or a PMID). The
batches are evaluation units only; the grouping carries no ranking and no judgement.

## 7. Amendment policy

This file is frozen at the timestamp below and is not amended. Any correction is a separate
addendum file with its own hash, stating what changed and why, with the original left in place.
Negative results are recorded, including the case where a drug we expected to remove survives
and joins the candidate list. Verified and unverified are marked throughout, where VERIFIED
means read at source or computed here from the public file, and UNVERIFIED means anything else.

FROZEN: 2026-10-20T11:42:00Z
