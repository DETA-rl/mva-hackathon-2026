# RESULT-B3: evaluation of batch 3 (ubiquitin-proteasome, APC/C and PP2A route), 14 drugs

Test ID: T2-NONCHOICE-01, batch B3
Agent: nc-eval-b3
Pre-registration: `PRE_REG_NONCHOICES.md`, sha256
`ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4`, verified against the file
before this evaluation began. Drug list: `BATCHES.md`, sha256
`61c1fca70c2f8b046677397352e0d53aa81d57181b75360910d64a107f64da30`, Section 5 Batch 3.
Criterion C3 rule: `PRE_REG_R2B_EXPOSURE.md`, sha256
`338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534`, verified.
Neither pre-registration was amended. No threshold was changed after seeing evidence.

Non-clinical clause, repeated from the pre-registration: this is a hypothesis-screening document
about published mechanism, label and database facts. It is not clinical advice, it proposes no
dose or regimen for any person, and nothing in it may be read as a recommendation to administer
anything. No patient-derived data is used. Every query leaving this machine carried a drug name,
a gene symbol, a mechanism term or a PMID, and nothing else.

VERIFIED means read at source this run (PubMed abstract, FDA label text, EMA medicine page) or
computed here from the public DepMap file. UNVERIFIED means anything else and is labelled inline.

---

## 1. Counts

| Outcome | n | Drugs |
|---|---|---|
| REMOVED | 2 | maduramicin (C3 direction), ataluren (C1 regulatory class) |
| KEPT AS CANDIDATE | 0 | none |
| UNRESOLVED | 12 | azithromycin, bortezomib, cantharidin, carfilzomib, cyclophosphamide, docetaxel, epirubicin, fluorouracil, ixazomib, pembrolizumab, regorafenib, thonzonium |

## 2. The batch's main result, stated as a negative finding about the instrument

Twelve of fourteen rows end UNRESOLVED, and they end there for one shared reason. For those
twelve the "claimed target or mechanism" carried by the universe is a curated database
annotation (a DGIdb interaction string such as "targets PPP2R5D" or "targets FBXW7"), not a
published rationale that measures anything on BUBR1. Criterion C3 needs C_demo, the
concentration at which the proposed mechanism was demonstrated in its cited source. Where no
source demonstrates the mechanism on BUBR1 at all, C_demo does not exist, the ratio R cannot be
formed, and the frozen rule returns E-UNRESOLVED, which never removes.

So the honest reading of this batch is: the frozen C3 instrument has almost no removal power
against rows whose mechanism is an annotation. Both removals below came from reading a primary
source or a regulator's page directly, and neither came from the annotation that put the drug
in the universe. This is reported, not worked around, and it is the same shape of finding the
universe file already recorded about its own literature arm.

## 3. Verdict table

C1 class from openFDA (drug/label.json and drug/drugsfda.json, queried by
`openfda.generic_name` then `openfda.substance_name`) and, for ataluren, the EMA medicine page.
C2 computed here (Section 5). C3 per the frozen R2-B rule. C4 reported only and removes nothing
(pre-registration Section 5.4). C5 per RANKING-RULE-T2.

| Drug | C1 class | C2 flagged targets | C3 direction | C3 outcome | C5 | Outcome |
|---|---|---|---|---|---|---|
| ataluren | **no authorised medicinal product** (EU authorisation expired 28 Mar 2025; no US product) [V] | no human gene target measured | UNKNOWN for BUBR1 | E-UNRESOLVED | G4, with a published contradiction to the discovery assay | **REMOVED (C1)** |
| maduramicin | no human authorised drug product; veterinary anticoccidial [V] | PPP2CA 0.826 YES | **AGAINST** (activates PP2A) [V] | **E-FAIL limb (i)** | G4 | **REMOVED (C3 direction)** |
| azithromycin | Rx, oral [V] | no human gene target measured | UNKNOWN for BUBR1 | E-UNRESOLVED | G4 | UNRESOLVED |
| bortezomib | Rx, IV/SC [V] | PSMB1 0.997, PSMB2 1.000, PSMB5 0.947 all YES | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| carfilzomib | Rx, IV [V] | PSMB1, PSMB2, PSMB5 all YES | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| ixazomib | Rx, oral [V] | PSMB1, PSMB2, PSMB5 all YES | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| cantharidin | Rx, topical only [V] | PPP2CA 0.826 YES | UNKNOWN (node rule) | E-UNRESOLVED | G4 | UNRESOLVED |
| thonzonium | Rx, otic only, as a product component [V] | PSMB5 0.947 YES (claimed target) | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| cyclophosphamide | Rx, IV/oral [V] | PPP2R5D 0.000 no | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| epirubicin | Rx, IV [V] | PPP2R5D 0.000 no | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| fluorouracil | Rx, IV and topical [V] | PPP2R5D no; TYMS 0.468 YES (true target) | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| docetaxel | Rx, IV [V] | FBXW7 0.041 no; TUBB 0.964 YES (true target) | UNKNOWN, AGAINST risk recorded | E-UNRESOLVED | G4 | UNRESOLVED |
| pembrolizumab | Rx, IV/SC [V] | FBXW7 no; PDCD1 0.001 no (true target) | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |
| regorafenib | Rx, oral [V] | FBXW7 no; KDR 0.005 no (true target) | UNKNOWN | E-UNRESOLVED | G4 | UNRESOLVED |

## 4. The two removals, with the sentences that decide them

### 4.1 maduramicin. REMOVED on mechanism direction

Deciding source, PMID 29241734 (Chen, Jiang, Huang, Toxicol Lett 2018), title verbatim:

> "**Maduramicin-activated protein phosphatase 2A** results in extracellular signal-regulated
> kinase 1/2 inhibition, leading to cytotoxicity in myocardial H9c2 cells."

Same abstract, verbatim, on what the compound is:

> "Maduramicin, a polyether ionophore antibiotic used as an **anticoccidial agent in poultry
> industry**, has been reported to be toxic to animals and humans if improperly used or by
> accident, resulting in heart failure, skeletal muscle degeneration and even death."

The universe's own claim for this entrant was "targets PPP2CA" (ChEMBL CHEMBL1909065), and the
primary source resolves the sign of that interaction as activation. PP2A activation is the
direction already scored AGAINST under the frozen node rule of PRE-REG-R2B-EXPOSURE Section 4,
on sources read at abstract in that test: PP2A-B56 is recruited to the KARD of BUBR1 and
"extinguishing the checkpoint" (PMID 33207204), and removal of BUBR1 "reduces PP2A-B56alpha
kinetochore binding" (PMID 23079597). In a BUBR1-deficient cell the limiting quantity is the
scaffold, so raising bulk PP2A activity drives the silencing step rather than restoring BUBR1.
E-FAIL limb (i), the candidate has one arm, so the candidate is REMOVED.

This is a removal on mechanism direction. It is not a safety finding and is not stated as one.

Reported, and NOT used as the deciding test: maduramicin has no authorised human drug product.
openFDA returned zero results for `openfda.generic_name:"maduramicin"` and
`openfda.substance_name:"maduramicin"` on both the label and drugsfda endpoints [V].

Falsifier, fixed by the pre-registration's falsifier clause: a primary source showing
maduramicin inhibits rather than activates PP2A, or a primary source showing PP2A activation
raises BUBR1 protein or preserves checkpoint function. Neither was found this run.

### 4.2 ataluren. REMOVED on regulatory class

Deciding source, the EMA medicine page for Translarna (ataluren), verbatim:

> "On 28 March 2025, the European Commission issued a decision to **not renew the conditional
> marketing authorisation for Translarna (ataluren) in the European Union** (EU)."

and, on the same page:

> "This medicine's authorisation has **expired**"

with the stated ground:

> "CHMP, which recommended to not renew the authorisation because the **effectiveness of the
> medicine has not been confirmed**."

Authorisation details on that page: marketing authorisation issued 31 July 2014, "Expiry of
marketing authorisation 28/03/2025" [V]. United States: openFDA returned zero results for
ataluren on both the label and drugsfda endpoints, by generic name and by substance name [V].
Ataluren is not a dietary supplement.

RANKING-RULE-T2's scope is market-approved prescription drugs, OTC drugs and dietary supplements.
As of 2026-10-20 ataluren is none of these in the two jurisdictions checked, so it is removed on
regulatory class under pre-registration Section 5.7.

Stated plainly so the removal is not over-read: this is a regulatory-status finding. It is not a
claim about the molecule's biology, and it is not a safety finding.

Falsifier: a current marketing authorisation for ataluren in a jurisdiction not checked here. US
and EU were checked; no other register was queried, and that is a coverage limit of this row.

Reported separately, because the removal does not rest on it: the mechanism arm is ribosomal
readthrough of premature termination codons, PMID 17450125 verbatim, "a new chemical entity that
selectively induces ribosomal readthrough of premature but not normal termination codons" [V].
No source tests ataluren, or any readthrough agent, on BUB1B or BubR1: PubMed
`(BUB1B[tiab] OR BubR1[tiab]) AND (nonsense[tiab] OR readthrough[tiab] OR "premature
termination"[tiab])` returns 7 records, none of which concerns readthrough therapy of BUB1B [V,
searched and the 7 titles read]. The discovery assay for this molecule also carries a published
contradiction, PMID 20194791 verbatim: "PTC124 (Ataluren ...) discovered in an FLuc-based assay
targeting nonsense codon suppression, is an unusually potent FLuc-inhibitor", with the paper
showing the apparent gain in signal is posttranslational stabilisation of the reporter. Under
RANKING-RULE-T2 that keeps the grade at G4.

## 5. C2, DepMap dependency flags, computed here

Method identical to the T2-P5 script `p5_depmap_safety.py` and therefore to the T2-P4 method:
DepMap 24Q4 `CRISPRGeneEffect.csv` and `Model.csv` at
`~/Documents/HACKATON/_private/public_data/depmap_24Q4/`; column matched on the symbol before
" ("; blood lineage is OncotreeLineage in {Myeloid, Lymphoid}; per gene the fraction of lines
with Chronos gene effect < -0.5 over all lines with a value, plus the blood-lineage median. Flag
if fraction >= 0.25. Script written for this batch at
`~/Documents/HACKATON/_private/agent_out/nonchoices/eval_B3/b3_depmap.py`, output
`b3_depmap.tsv`. 1,178 cell lines, 135 blood-lineage lines. No gene was absent from the file.

| Gene | n lines | fraction Chronos < -0.5 | flag (>= 0.25) | blood median | which rows use it |
|---|---|---|---|---|---|
| PSMB1 | 1178 | 0.997 | YES | -1.804 | bortezomib, carfilzomib, ixazomib |
| PSMB2 | 1178 | 1.000 | YES | -2.050 | bortezomib, carfilzomib, ixazomib |
| PSMB5 | 1178 | 0.947 | YES | -0.939 | carfilzomib, ixazomib, thonzonium (claimed) |
| PPP2CA | 1178 | 0.826 | YES | -1.166 | cantharidin, maduramicin |
| PPP2R1A | 1178 | 0.779 | YES | -0.510 | reported, re-measured as the check against T2-P5 |
| PPP2R5D | 1178 | 0.000 | no | 0.041 | cyclophosphamide, epirubicin, fluorouracil (claimed) |
| FBXW7 | 1178 | 0.041 | no | -0.039 | docetaxel, pembrolizumab, regorafenib (claimed) |
| TUBB | 1178 | 0.964 | YES | -1.881 | docetaxel (true pharmacological target) |
| TYMS | 1178 | 0.468 | YES | -0.783 | fluorouracil (true pharmacological target) |
| PDCD1 | 1178 | 0.001 | no | -0.063 | pembrolizumab (true pharmacological target) |
| KDR | 1178 | 0.005 | no | -0.100 | regorafenib (true pharmacological target) |
| TUBB1 | 1178 | 0.001 | no | -0.070 | reported alongside TUBB |
| ATP6V0C | 1178 | 0.996 | YES | -2.309 | reported; see the thonzonium note in Section 7 |

Four of the genes above (TUBB, TYMS, PDCD1, KDR) are not the targets the universe claimed. They
were added because for those four drugs the claimed gene is a database annotation rather than
the molecule's pharmacological target, and reporting only the annotation would have produced a
"no flag" line that means nothing. Adding them is reporting, not a new rule: C2 removes nothing
either way.

Carried caveats, unchanged and not used to re-flag anything. A DepMap flag alone does not remove
a drug here (pre-registration Section 5.2); it is the RANKING-RULE-T2 safety tie-break input. A
CRISPR knockout is a loss-of-function proxy in cancer lines, never normal marrow. No flag is a
safety verdict and no absent flag is a safety clearance.

## 6. C3, the twelve UNRESOLVED rows, each with the datum that is missing

The frozen rule returns E-UNRESOLVED when the achieved free concentration or C_demo cannot be
established. Per pre-registration Section 5.7 the missing datum and the failed search route are
both named.

**Proteasome inhibitors: bortezomib, carfilzomib, ixazomib.** This is the one group in the batch
with a real published link to BubR1 abundance, and it still cannot be scored. PMID 21441410
(Riffell, Jänicke, Roberge, Mol Cancer Ther 2011), verbatim:

> "Mitotic slippage induced by SU6656 or geraldol was blocked by the **proteasome inhibitor
> MG-132** and involved proteasome-dependent degradation of cyclin B1 and the mitotic checkpoint
> proteins budding uninhibited by benzimidazole related 1 (**BubR1**) and cell division cycle 20
> (Cdc20) in T98G cells."

So BubR1 is degraded by the proteasome and a proteasome inhibitor blocks that degradation. The
demonstration uses MG-132, a tool compound, not any of the three approved molecules, and the
abstract gives no concentration. This is exactly the situation the frozen rule already met on
the 4-PBA HDAC arm, where the BubR1 effect was shown with trichostatin A and not with the drug:
direction was scored UNKNOWN, not TOWARD, and the arm was E-UNRESOLVED. The same reading is
applied here, symmetrically. Missing datum: a C_demo for a BubR1 endpoint with the approved
molecule. Failed routes: PubMed
`(bortezomib[tiab] OR MG132[tiab] OR "proteasome inhibitor"[tiab]) AND (BubR1[tiab] OR
BUB1B[tiab])` returned 8 records, titles read, none reports BubR1 protein after an approved
proteasome inhibitor; `(BubR1[tiab] OR BUB1B[tiab]) AND proteasome[tiab]` returned 18, titles
read, same result [V].

Exposure, recorded because for bortezomib it can be computed and because a reader will ask.
Label, verbatim: "the mean maximum plasma concentrations of bortezomib (C max) after the first
dose (Day 1) were 57 and 112 ng/mL" (1.0 and 1.3 mg/m2 IV) and "The binding of bortezomib to
human plasma proteins averaged 83%" [V]. MW 384.24 g/mol, so 112 ng/mL = 2.92e-7 M total and
free = 2.92e-7 x 0.17 = **4.96e-8 M, about 50 nM**. No ratio is claimed, because there is no
C_demo to divide into. Carfilzomib: label gives dose-dependent Cmax in a table and "Carfilzomib
is 97% bound to human plasma proteins" [V]; ixazomib is oral and the label states a high-fat
meal "decreased ixazomib AUC by 28% and C max by 69%" [V]; neither is scored, for the same
missing-C_demo reason.

**cantharidin.** Target identity is established at source, PMID 1334551 (Li and Casida, PNAS
1992), title verbatim: "Cantharidin-binding protein: identification as protein phosphatase 2A",
with "Inhibition of PP2A activity may account for the diverse effects and toxicity of
cantharidin and its analogs" [V]. No IC50 appears in that abstract, so C_demo is NOT ESTABLISHED
(full text not retrieved; named failed route). Direction is UNKNOWN, not TOWARD: under the
frozen node rule a mechanism acting on a node downstream of BUBR1 "is NOT scored as helpful
merely because it perturbs a node that BUBR1 also touches", and no source shows cantharidin
raising BUBR1 protein or preserving checkpoint function. Exposure, from the YCANTH label
verbatim: "Cantharidin was **not detectable in 15 out of 16 subjects**. Only one subject had a
detectable cantharidin plasma level of **3.391 ng/mL** at the 2-hour post-dose" after a single
dermal application [V]. MW 196.20 g/mol, so that single detectable value is 1.73e-8 M, about
17 nM, and for the other fifteen subjects the achieved concentration is below the assay limit
and therefore not established. E-UNRESOLVED on both limbs.

**azithromycin.** The published rationale for this entrant is nonsense readthrough, not a
ubiquitin-proteasome action: PMID 37276642, title verbatim, "Azithromycin induces read-through
of the nonsense Apc allele and prevents intestinal tumorigenesis in C3B6F1 Apc(Min/+) mice" [V].
That is a different gene in a mouse model. Missing datum: any source measuring BUBR1 or the
checkpoint after azithromycin. Failed route, named: PubMed `azithromycin[tiab] AND (BubR1[tiab]
OR BUB1B[tiab] OR aneuploidy[tiab] OR "spindle assembly checkpoint"[tiab])` returns **0 records**
[V]. Direction UNKNOWN, C_demo not established, E-UNRESOLVED.

**cyclophosphamide, epirubicin, fluorouracil, docetaxel, pembrolizumab, regorafenib,
thonzonium.** For all seven the universe's claimed mechanism is a DGIdb annotation string and no
cited source demonstrates any action on BUBR1 or the checkpoint. Missing datum in every case:
C_demo for a BUBR1 endpoint. Failed routes, named and run this run: `docetaxel[tiab] AND
("spindle assembly checkpoint"[tiab] OR "mitotic slippage"[tiab] OR BubR1[tiab])` 27 records,
titles read, none measures BubR1 protein after docetaxel; `(epirubicin[tiab] OR
doxorubicin[tiab]) AND (BubR1[tiab] OR "mitotic slippage"[tiab])` 12 records, titles read, none
on BubR1 abundance; `fluorouracil[tiab] AND (BubR1[tiab] OR "spindle assembly checkpoint"[tiab])`
5 records; `regorafenib[tiab] AND (BubR1[tiab] OR "spindle assembly checkpoint"[tiab] OR
FBXW7[tiab])` 1 record; `pembrolizumab[tiab] AND FBXW7[tiab]` 5 records, all biomarker-response
associations, not a mechanism on BUBR1; `thonzonium[tiab]` 20 records, none on PSMB5 or the
checkpoint [V for every count and for the titles read].

**AGAINST risk recorded and not scored, docetaxel.** Two sources, read at abstract, make a
two-step chain that is worth recording but is not a single primary source and so does not meet
the frozen bar for direction AGAINST. PMID 33504817 verbatim: "Survivin depletion protects HeLa
cells against **docetaxel-induced apoptosis by facilitating mitotic slippage**", with "The
anticancer effects of taxanes are attributed to the induction of mitotic arrest through
activation of the spindle assembly checkpoint". PMID 21441410, already quoted, shows mitotic
slippage proceeds through proteasome-dependent degradation of BubR1. Chaining the two would
predict that a taxane lowers BubR1 in cells that slip. No source measured that after docetaxel.
Recorded as a risk attached to the row, exactly as the 4-PBA AGAINST risk was recorded, and not
used to remove.

## 7. C4 and C5

**C4.** Not computed for any row in this batch, and by pre-registration Section 5.4 it removes
nothing regardless. C4 is the plasma-concentration-versus-enzyme-IC50 instrument, declared
NON-DISCRIMINATING by RESULT-R2D-R2E before this universe was known. No row here supplies both
halves of that comparison for a BUBR1-relevant enzyme, so there is nothing to report beyond the
exposure figures already given in Section 6.

**C5, RANKING-RULE-T2 grade.** Every row in this batch is **G4**: mechanism or pathway evidence
only. No row reaches G3, because G3 needs mouse or cell-line data on BUBR1 protein or checkpoint
endpoints for the molecule itself, and the only BubR1-direct source in the batch (PMID 21441410)
used a tool compound. Ataluren's G4 additionally carries the published contradiction to its
discovery assay (PMID 20194791). Since no row is KEPT, no grade enters the ranked list, and
RANKING-RULE-T2 is not applied to anything here.

**Thonzonium note.** The universe's claim for thonzonium is "targets PSMB5". No source found this
run supports it, and the compound is a cationic surfactant authorised only as a component of a
prescription otic product. ATP6V0C is reported in the C2 table because the published activity
for this compound concerns vacuolar ATPase rather than the proteasome; that is recorded as an
observation about the annotation, is UNVERIFIED as a claim about thonzonium's target, and
changes no outcome.

## 8. Falsifiers for this batch's own outcomes

| Outcome reached here | What would falsify it |
|---|---|
| maduramicin REMOVED on direction | a primary source showing maduramicin inhibits PP2A, or showing PP2A activation raises BUBR1 protein or preserves checkpoint function |
| ataluren REMOVED on regulatory class | a current marketing authorisation in a jurisdiction not checked (US and EU were checked on 2026-10-20) |
| twelve rows UNRESOLVED | any primary source that measures BUBR1 protein or a checkpoint endpoint after one of those twelve molecules at a stated concentration; that single source would convert the row to E-PASS, E-WEAK or E-FAIL |
| zero drugs KEPT AS CANDIDATE | the same; this batch does not claim the twelve were tested and failed, only that they could not be scored |
| C2 values | a re-run of `b3_depmap.py` on DepMap 24Q4 returning different fractions |

## 9. Limitations of this batch evaluation

- Nothing here establishes that any molecule works, and surviving as UNRESOLVED is not evidence
  of benefit. UNRESOLVED is never read as safety, and no removal here is a safety statement.
- Only abstracts were read. Where a C_demo might exist in a full text, this evaluation did not
  reach it, and the row is UNRESOLVED rather than scored on a guess.
- C1 used openFDA and, for one row, the EMA medicine page. No other national register was
  queried, which bounds every regulatory-class statement above.
- The DGIdb annotations that populated this batch were not corrected, only read. Where the
  annotation is not the molecule's pharmacological target, that is said in the row.
- One deviation is disclosed, in the C2 direction only: four genes (TUBB, TYMS, PDCD1, KDR) were
  measured that the universe did not name, so that the four affected rows carry a meaningful
  dependency reading. C2 removes nothing, so the deviation cannot change an outcome.

## 10. Files

Mac: `scratchpad/agent_out/nonchoices/RESULT_B3.md` (this file).
Box: `~/Documents/HACKATON/_private/agent_out/nonchoices/eval_B3/RESULT_B3.md`, plus
`b3_depmap.py` and `b3_depmap.tsv` written there this run. No existing file was edited and
nothing was deleted.

WRITTEN: 2026-10-20
