# RESULT-B4c: evaluation of Batch 4 items 99 to 147 under PRE-REG-NONCHOICES

Test ID: T2-NONCHOICE-01, batch B4 part C
Agent: nc-eval-b4c
Pre-registration: `PRE_REG_NONCHOICES.md`, sha256
`ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4`, verified against the file
before any evaluation call was made this run. Not amended.
Criterion C3 rule: `PRE_REG_R2B_EXPOSURE.md`, sha256
`338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534`, verified the same way.
Criterion C5 rule: RANKING-RULE-T2 as recorded in `HYPOTHESIS_REGISTER.md`, unchanged.
Written: 2026-10-20.

Non-clinical clause, repeated from the pre-registration: this is a hypothesis-screening document
about published mechanism, label and database facts. It is not clinical advice, it proposes no
dose or regimen for any person, and nothing here may be read as a recommendation to administer
anything. No patient-derived data was used. Every query leaving this machine carried a drug name,
a gene symbol, a mechanism term or a PMID, and nothing else.

VERIFIED [V] means read at the named source this run, or computed this run from the public file
named. UNVERIFIED [U] means anything else.

No criterion removes anything on a safety claim. No removal below is a safety finding about any
drug, and no unresolved row is a safety clearance.

## 1. Scope actually evaluated, and the scope question I did not decide for myself

My assigned slice is Batch 4 items 99 to 147 in the order listed in `BATCHES.md`, which is 49
drugs. Eight of them carry the "also considered, reached outside the stated screen" tag:
potassium citrate, pralsetinib, propranolol, rilmenidine, ruxolitinib, somatropin, tocilizumab,
trametinib. Each of those eight was evaluated individually, not grouped.

The brief also asked for every "also considered" entry if `BATCHES.md` listed them outside
B1 to B4. It does not: all 26 are listed inside the four batches (7 in B1, 4 in B2, 2 in B3,
13 in B4). Of the 13 in B4, the 8 named above fall inside my item range and are evaluated here;
the other 5 (digoxin, hydroxychloroquine, irinotecan, levetiracetam, mesalamine) fall at items 1
to 98 of B4, and the 13 in B1 to B3 belong to those batches. So 18 of the 26 "also considered"
rows are outside my slice and are not covered by this file. I did not evaluate rows outside my
slice and I did not edit any existing file. Flagged so the gap is visible rather than assumed
covered.

## 2. Counts

| Outcome | Count |
|---|---|
| REMOVED | 5 |
| KEPT AS CANDIDATE | 0 |
| UNRESOLVED | 44 |
| Total | 49 |

Of the 44 UNRESOLVED, 24 are rows the frozen literature arm reached as chemo-sensitivity or
bioinformatic co-occurrence (`BATCHES.md` findings 2.2 and 2.3), 12 are rows admitted by a
curated gene-to-drug interaction claim that is not the drug's label mechanism, and 8 are the
"also considered" rows of Section 6. For the co-occurrence rows, no source anywhere
proposes the drug as a way to raise BUBR1, so criterion C3 has no arm to score: there is no
claimed mechanism, hence no C_demo, hence no ratio. Under the frozen rule that is UNRESOLVED,
not REMOVED. The honest consequence for the write-up: the largest group this screen returned
cannot be disposed of by the frozen criteria at all. That is a property of the screen, not a
judgement about those drugs.

## 3. What was run, with sources

**C1, regulatory class.** Offline join of the public Drugs@FDA bulk files already on the box
(`dl_fda/Products.txt`, `MarketingStatus.txt`, `MarketingStatus_Lookup.txt`) by application and
product number, matching on `ActiveIngredient` or `DrugName`, 49 names [V, computed this run,
script `c1_fda_bulk.py`, output `c1_b4c.tsv`]. Six names returned zero product rows and were
re-checked against openFDA `drugsfda` and `label` and against DailyMed by drug name [V]:
terfenadine (0, 0, 0 SPLs), quinacrine (0, 0, one SPL which is an aquarium product from a
laboratory supplier), perhexiline (0, 0, 0), rilmenidine (0, 0, 0), sapanisertib (0, 0, two SPLs
which are bulk-powder listings from chemical suppliers), zotarolimus (0, 0, 0). Per
pre-registration Section 2.1, a drug whose approval cannot be confirmed in these registers is
resolved UNRESOLVED on C1, never silently kept and never silently dropped. The EMA register was
not queried this run, so the EU limb of C1 is [U] for all 49 rows. Paediatric label statements
were retrieved verbatim only for the eight "also considered" rows (Section 6), because C1's
paediatric limb is reported and never exclusionary and the brief fixed depth at "only where a
drug could plausibly pass".

**C2, DepMap flags for the claimed targets.** Method identical to `p5_depmap_safety.py`: DepMap
24Q4 `CRISPRGeneEffect.csv` and `Model.csv`, column matched on the symbol before " (", fraction
of the 1,178 lines with Chronos gene effect below -0.5, blood-lineage median over OncotreeLineage
in {Myeloid, Lymphoid}, flag at fraction at or above 0.25. Computed this run [V], script
`c2_depmap_b4c.py`, output `c2_b4c.tsv`:

| gene | lines with a value | fraction below -0.5 | blood median | flag |
|---|---|---|---|---|
| MTOR | 1178 | 0.986 | -1.130 | FLAG |
| AURKB | 1178 | 1.000 | -2.420 | FLAG |
| PLK4 | 1178 | 0.982 | -1.281 | FLAG |
| FBXW7 | 1178 | 0.041 | -0.039 | no |
| SIRT1 | 1178 | 0.004 | 0.089 | no |
| HSP90AA1 | 1178 | 0.052 | -0.275 | no |

MTOR 0.986 and PLK4 0.982 reproduce the T2-P4 values exactly, which is the method check. Per
pre-registration Section 5.2 a flag alone removes nothing here, and the carried caveat travels
with it: a CRISPR knockout is a loss-of-function proxy in cancer lines, never normal marrow, so
no flag is a safety verdict and no absent flag is a safety clearance.

**C3, direction and exposure.** The frozen R2-B rule. Eight PubMed searches were run verbatim
and are reproduced in Section 8 with their counts, then four abstracts were read at source. The
decisive readings are in Sections 4 and 5.

**C4.** Not computable for any row in this slice: none of the 49 has a published enzyme arm with
both an IC50 and an achieved concentration for a BUBR1-raising mechanism, because none has such
a mechanism claimed. Reported as not computable, and in any case RESULT-R2D-R2E declared the C4
instrument NON-DISCRIMINATING, which pre-registration Section 5.4 fixed before this universe was
known. C4 removes nothing here.

**C5.** No row in this slice reaches the G4 floor on the endpoint. G4 is "mechanism or pathway
evidence only" for the BUBR1 mechanism; these rows have no mechanism or pathway evidence pointing
toward raising BUBR1. Recorded as "no grade on the endpoint" rather than as G4, so that the grade
ladder is not quietly widened. Where evidence on BUBR1 exists it points away from the endpoint,
and that is handled under C3, not C5.

## 4. The five removals, with the deciding value named

**Mechanism direction, C3 limb (i), AGAINST per a primary source read at source this run.**

1. **vincristine** (item 144). PMID 32850387, verbatim: "sildenafil amplified vincristine-induced
   phosphorylation and **cleavage of BUBR1**, a protein kinase in spindle assembly checkpoint
   (SAC) function and chromosome segregation" [V, abstract]. The endpoint fixed in the C3 rule is
   raising residual BUBR1 protein. A source showing the drug drives cleavage of BUBR1 reports a
   net loss of intact BUBR1, so direction is AGAINST and the arm is E-FAIL(i). Marked qualifiers:
   the cleavage is reported in an apoptotic context, and the in vitro concentration is not stated
   in the abstract [U]. Mitotic arrest at labelled doses is the drug's own clinical mechanism, so
   the "at clinical exposure" clause is satisfied for the arrest step [V, label class].
2. **vinorelbine** (item 145). PMID 32764382, verbatim: "Vinorelbine induced tubulin acetylation
   and Bub1-related kinase (BUBR1) phosphorylation ... These effects, as well as **BUBR1
   cleavage**, were substantially enhanced in co-treatment" [V, abstract]. Same reading, same
   outcome. Concentration not stated in the abstract [U].
3. **vinblastine** (item 143). Class-level disposal under pre-registration Section 5.6: the
   deciding evidence is class-level across the vinca alkaloids, demonstrated for two of the three
   marketed members (vincristine, vinorelbine) with the same molecular target and the same
   mitotic-arrest mechanism. Vinblastine itself was not tested in either source, and that is
   marked [U] for this drug specifically.

**Class-level disposal, mTOR-inhibitor class, already removed on the register by T2-P4.**

4. **sapanisertib** (item 125). A TORC1/TORC2 inhibitor, that is, a member of the class
   pre-registration Section 4 lists as already evaluated, deciding test T2-P4, MTOR fraction
   0.986 (recomputed here as 0.986 [V]). Independently, C1 found no authorised drug product in
   Drugs@FDA, openFDA `drugsfda` or openFDA `label`; the two DailyMed hits are bulk-powder
   supplier listings [V]. So the DGIdb `approved == true` flag that admitted it to the universe is
   contradicted by the registers. Disclosed as an admission-ticket error in the screen, exactly
   the failure mode pre-registration Section 2.3 said the approval flags can produce.
5. **zotarolimus** (item 147). A sirolimus analogue, so a member of the same already-evaluated
   class, deciding test T2-P4. C1: no authorised systemic drug product in any register queried
   [V]; its marketed use is as a component of a coated coronary device, which is not a drug
   product in these registers.

For 4 and 5 the ground is class membership established from the drug's own pharmacological class,
never from a DepMap flag computed here for a new gene. Pre-registration Section 5.2 forbids
extending the T2-P4 DepMap precedent to new drugs and that prohibition is respected: no drug in
this slice is removed because a gene scored above the flag threshold.

## 5. Risks recorded, which are not removals

Three findings point away from the endpoint but do not meet the frozen AGAINST definition for the
drug as used alone. They are recorded and attached to the drugs, following the precedent in
RESULT-R2B-EXPOSURE Section 4, where AGAINST evidence obtained with a different molecule was
reported as a risk and the arm left E-UNRESOLVED.

- **PDE5 inhibitors (sildenafil item 127, tadalafil 131, vardenafil 142).** PMID 32850387,
  verbatim: "Sildenafil also significantly **decreased kinetochore tension during SAC
  activation**" and "Sildenafil-mediated synergistic effects were mimicked by other PDE5
  inhibitors including vardenafil and tadalafil, and also by PDE5A knockdown in cells" [V]. The
  BUBR1 cleavage was amplified in co-treatment with an antimitotic, and the effect of a PDE5
  inhibitor alone on BUBR1 is not established in that source. Direction is therefore UNKNOWN for
  the drug alone, the arm is E-UNRESOLVED, and the AGAINST evidence is carried as a material risk
  for a mitotic-checkpoint indication. This is the one place in this slice where a removal was
  available on a looser reading and was not taken.
- **Microtubule-targeted agents (paclitaxel item 100, and the vinca rows above).** PMID 37883329,
  title verbatim: "Diverse microtubule-targeted anticancer agents kill cells by inducing
  chromosome missegregation on multipolar spindles"; PMID 24670687 for paclitaxel specifically
  [V, titles]. Induced chromosome missegregation is the phenotype this disease already has, so the
  risk is material. It is not scored AGAINST, because the frozen definition requires lowering
  BUBR1 protein or silencing, weakening or overriding the checkpoint, and missegregation on
  multipolar spindles occurs through a geometry the checkpoint does not sense rather than through
  a weakened checkpoint. Paclitaxel stays UNRESOLVED with the risk attached. The vinca removals do
  not rest on this source.
- **JAK inhibition (ruxolitinib item 124).** PMID 20703093, verbatim: "JAK inhibition also
  increased nuclear BubR1 phosphorylation" and "inhibiting RAF with GW5074 blocked the pan-JAK
  inhibitor-induced **endoreduplication**", with the authors' own framing "a JAK/RAF/MEK/BubR1
  axis that can regulate genomic stability" [V]. The source used a pan-JAK inhibitor, not
  ruxolitinib, and the endpoint is endoreduplication rather than BUBR1 abundance. Drug identity
  mismatch, so direction is UNKNOWN and the arm is E-UNRESOLVED with the ploidy risk recorded.

## 6. The eight "also considered" rows, evaluated individually

C1 paediatric statements below are quoted from the openFDA label endpoint this run [V], truncated
where long. Each drug was also searched in PubMed as `"<drug>"[tiab] AND (BubR1[tiab] OR
BUB1B[tiab] OR "mosaic variegated aneuploidy"[tiab])` [V, counts as stated].

| Drug | C1 | Paediatric statement | BUBR1 or disease source | Outcome |
|---|---|---|---|---|
| potassium citrate | Rx US, 29 products, 24 prescription [V]; also sold as a supplement [U] | not retrieved (no `pediatric_use` returned) | count 0 | UNRESOLVED, no mechanism arm |
| pralsetinib | Rx US, 2 products [V] | "established in pediatric patients aged 12 years and older for RET fusion-positive thyroid cancer" | count 0 | UNRESOLVED, no mechanism arm |
| propranolol | Rx US, 227 products, 79 prescription [V] | "Safety and effectiveness of propranolol in pediatric patients have not been established" | count 0 | UNRESOLVED, no mechanism arm |
| rilmenidine | no authorised product in Drugs@FDA, openFDA or DailyMed [V]; authorised nationally in Europe [U, not queried] | none in label | count 0 | UNRESOLVED on C1 and on C3 |
| ruxolitinib | Rx US, 23 products [V] | "established in non-immunocompromised pediatric patients ages 2 years and older" (topical indication quoted) | PMID 20703093, pan-JAK inhibitor, endoreduplication risk, Section 5 | UNRESOLVED, with risk recorded |
| somatropin | Rx US, 68 products, 45 prescription [V] | "established in growth failure due to inadequate secretion of endogenous growth hormone, short stature associated with Noonan syndrome ..." | count 0 | UNRESOLVED; the rationale is symptomatic and outside this test's endpoint |
| tocilizumab | Rx US, 19 products [V] | "indicated for the treatment of pediatric patients with: Active systemic juvenile idiopathic arthritis in patients 2 years of age and older ..." | count 0 | UNRESOLVED, no mechanism arm |
| trametinib | Rx US, 8 products, 5 prescription [V] | "established in pediatric patients 1 year of age and older with unresectable or metastatic solid tumors with BRAF V600E mutation" | count 2, both bioinformatic biomarker papers (PMID 41144123, 34849004), no mechanism source | UNRESOLVED, no mechanism arm |

None of the eight reached C5 above "no grade on the endpoint". None was removed. Three have a
paediatric label in a chronic indication, which is reported and is not a reason to keep or to
remove anything.

## 7. Full table, items 99 to 147

Columns: C1 class from the registers named in Section 3; C2 flags among the targets the screen
claimed for that drug, with the fraction; C3 the R2-B outcome with its ground; C5 grade on the
endpoint; outcome with the deciding test. C4 is not computable for every row (Section 3) and is
omitted as a column rather than filled with a repeated placeholder. "co-occurrence row" means the
drug entered the universe only through a sensitivity or bioinformatic paper, with no mechanism
claim for BUBR1.

| # | Drug | C1 | C2 | C3 | C5 | Outcome, deciding test |
|---|---|---|---|---|---|---|
| 99 | oxaliplatin | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 100 | paclitaxel | Rx US [V] | no target claimed | E-UNRESOLVED, direction UNKNOWN; missegregation risk, PMID 37883329, 24670687 | no grade | UNRESOLVED, risk recorded |
| 101 | palbociclib | Rx US [V] | no target claimed | E-UNRESOLVED, no arm; search for a CDK4/6 link to BUB1B returned count 0 [V] | no grade | UNRESOLVED |
| 102 | paroxetine | Rx US [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm; mTOR is not this drug's label mechanism | no grade | UNRESOLVED |
| 103 | pazopanib | Rx US [V] | AURKB 1.000 FLAG, MTOR 0.986 FLAG, claims unverified | E-UNRESOLVED, no arm; neither gene is its label mechanism | no grade | UNRESOLVED |
| 104 | pentamidine | Rx US [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED |
| 105 | pentostatin | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 106 | perhexiline | no authorised product in the registers queried [V]; approved in Australia and New Zealand [U, not queried] | MTOR 0.986 FLAG, ChEMBL mechanism string not confirmed at a primary source [U] | E-UNRESOLVED, no arm | no grade | UNRESOLVED on C1 and C3 |
| 107 | perphenazine | Rx US [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED |
| 108 | pimecrolimus | Rx US, topical cream only [V] | MTOR 0.986 FLAG, claim unverified; its label mechanism is calcineurin inhibition, not mTOR | E-UNRESOLVED, no arm | no grade | UNRESOLVED |
| 109 | pimozide | Rx US [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED |
| 110 | pitavastatin | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 111 | polymyxin B | Rx US [V] | no target claimed | E-UNRESOLVED, no arm; its PMID is a transcriptomic perturbation list, not a direction source | no grade | UNRESOLVED |
| 112 | potassium citrate | Rx US [V] | no target claimed | E-UNRESOLVED, no arm | no grade | UNRESOLVED (also considered) |
| 113 | potassium iodide | OTC US, 5 over-the-counter products [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 114 | pralsetinib | Rx US [V] | no target claimed | E-UNRESOLVED, no arm | no grade | UNRESOLVED (also considered) |
| 115 | prednisone | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 116 | progesterone | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 117 | propafenone | Rx US [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED |
| 118 | propofol | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 119 | propranolol | Rx US [V] | no target claimed | E-UNRESOLVED, no arm | no grade | UNRESOLVED (also considered) |
| 120 | quinacrine | no human drug product in the registers queried; the single DailyMed SPL is an aquarium product [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED on C1 and C3 |
| 121 | ribociclib | Rx US [V] | no target claimed | E-UNRESOLVED, no arm; CDK4/6 to BUB1B search count 0 [V] | no grade | UNRESOLVED |
| 122 | rilmenidine | no authorised product in the registers queried [V] | no target claimed | E-UNRESOLVED, no arm; the autophagy rationale has no BUBR1 source, and the sign for a misfolded missense product under enhanced clearance is undetermined | no grade | UNRESOLVED (also considered) |
| 123 | rimegepant | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 124 | ruxolitinib | Rx US [V] | no target claimed | E-UNRESOLVED, direction UNKNOWN; endoreduplication risk, PMID 20703093, pan-JAK inhibitor not ruxolitinib | no grade | UNRESOLVED, risk recorded (also considered) |
| 125 | sapanisertib | no authorised product in the registers queried [V] | MTOR 0.986 FLAG | class member, mTOR inhibitor | no grade | **REMOVED**, class disposal, T2-P4, MTOR 0.986 |
| 126 | sevoflurane | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 127 | sildenafil | Rx US [V] | no target claimed | E-UNRESOLVED, direction UNKNOWN alone; AGAINST risk, PMID 32850387 | no grade | UNRESOLVED, risk recorded |
| 128 | simvastatin | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 129 | somatropin | Rx US [V] | no target claimed | E-UNRESOLVED, no arm; symptomatic rationale outside the endpoint | no grade | UNRESOLVED (also considered) |
| 130 | sorafenib | Rx US [V] | AURKB 1.000 FLAG, PLK4 0.982 FLAG, claims unverified | E-UNRESOLVED, no arm; neither gene is its label mechanism | no grade | UNRESOLVED |
| 131 | tadalafil | Rx US [V] | no target claimed | E-UNRESOLVED, direction UNKNOWN alone; AGAINST risk, PMID 32850387 (named as a mimic) | no grade | UNRESOLVED, risk recorded |
| 132 | tamoxifen | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 133 | temozolomide | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 134 | terfenadine | no authorised product in the registers queried [V] | MTOR 0.986 FLAG, claim unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED on C1 and C3 |
| 135 | testosterone | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 136 | tocilizumab | Rx US [V] | no target claimed | E-UNRESOLVED, no arm | no grade | UNRESOLVED (also considered) |
| 137 | topotecan | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 138 | trabectedin | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 139 | trametinib | Rx US [V] | no target claimed | E-UNRESOLVED, no arm; 2 hits, both bioinformatic | no grade | UNRESOLVED (also considered) |
| 140 | trifluoperazine | Rx US [V] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 141 | vandetanib | Rx US [V] | AURKB 1.000 FLAG, MTOR 0.986 FLAG, claims unverified | E-UNRESOLVED, no arm | no grade | UNRESOLVED |
| 142 | vardenafil | Rx US [V] | no target claimed | E-UNRESOLVED, direction UNKNOWN alone; AGAINST risk, PMID 32850387 (named as a mimic) | no grade | UNRESOLVED, risk recorded |
| 143 | vinblastine | Rx US [V] | no target claimed | AGAINST at class level, vinca alkaloids; drug itself not tested [U] | evidence points away | **REMOVED**, C3 direction, class disposal per Section 5.6 |
| 144 | vincristine | Rx US [V] | no target claimed | **AGAINST**, BUBR1 cleavage, PMID 32850387 [V] | evidence points away | **REMOVED**, C3 direction, E-FAIL(i) |
| 145 | vinorelbine | Rx US [V] | no target claimed | **AGAINST**, BUBR1 cleavage, PMID 32764382 [V] | evidence points away | **REMOVED**, C3 direction, E-FAIL(i) |
| 146 | vitamin D (ergocalciferol, cholecalciferol) | Rx US product exists (ergocalciferol) [V]; also sold as a supplement [U] | no target claimed | E-UNRESOLVED, no arm (co-occurrence row) | no grade | UNRESOLVED |
| 147 | zotarolimus | no authorised drug product in the registers queried [V] | MTOR 0.986 FLAG | class member, sirolimus analogue | no grade | **REMOVED**, class disposal, T2-P4, MTOR 0.986 |

## 8. Searches run verbatim, with counts

PubMed E-utilities, `db=pubmed`, no date or language filter, run 2026-10-20 [V]. Drug, gene and
mechanism terms only.

1. `(BubR1[tiab] OR BUB1B[tiab]) AND (degradation[tiab] OR degraded[tiab]) AND ("mitotic arrest"[tiab] OR slippage[tiab] OR adaptation[tiab])`, count 23.
2. `(BubR1[tiab] OR BUB1B[tiab]) AND (paclitaxel[tiab] OR taxol[tiab] OR nocodazole[tiab] OR vincristine[tiab] OR vinblastine[tiab]) AND (degradation[tiab] OR "protein level"[tiab] OR downregulat*[tiab] OR dephosphorylat*[tiab])`, count 29. Source of PMID 32850387 and 32764382.
3. `(BubR1[tiab] OR BUB1B[tiab]) AND (palbociclib[tiab] OR ribociclib[tiab] OR "CDK4/6"[tiab] OR abemaciclib[tiab])`, **count 0**. This is the failed search route for items 101 and 121, and it is why the transcriptional-override clause could not be applied to the CDK4/6 inhibitors: no primary source measures BUB1B after CDK4/6 inhibition.
4. `(BubR1[tiab] OR BUB1B[tiab]) AND ("DNA damage"[tiab] OR cisplatin[tiab] OR doxorubicin[tiab] OR etoposide[tiab]) AND (degradation[tiab] OR downregulat*[tiab] OR "protein level"[tiab] OR expression[tiab])`, count 49, all inspected titles are BUBR1-as-biomarker or BUBR1-drives-repair papers, none gives a drug-to-BUBR1 direction. This is the failed route for the DNA-damaging cytotoxics in this slice.
5. `(BubR1[tiab] OR BUB1B[tiab]) AND (autophagy[tiab] OR autophagic[tiab] OR lysosomal[tiab])`, count 10.
6. `(BubR1[tiab] OR BUB1B[tiab]) AND (mTOR[tiab] OR rapamycin[tiab] OR everolimus[tiab] OR sirolimus[tiab])`, count 10, all BUBR1-drives-mTOR-signalling or biomarker papers, none showing a rapalog raising BUBR1.
7. `(BubR1[tiab] OR BUB1B[tiab]) AND (ruxolitinib[tiab] OR tocilizumab[tiab] OR trametinib[tiab] OR "MEK inhibitor"[tiab] OR somatropin[tiab] OR "growth hormone"[tiab] OR propranolol[tiab] OR rilmenidine[tiab] OR JAK[tiab])`, count 9. Source of PMID 20703093.
8. `(BubR1[tiab] OR BUB1B[tiab]) AND ("Aurora B"[tiab] OR AURKB[tiab] OR hesperadin[tiab] OR ZM447439[tiab])`, count 130, not used: no drug in this slice is an Aurora B inhibitor by its label mechanism, so the class question did not arise here.
9. Per-drug checks for the eight "also considered" rows, Section 6, seven returned count 0 and trametinib returned count 2.
10. `paclitaxel[tiab] AND "chromosome missegregation"[tiab] AND multipolar[tiab]`, count 4, source of PMID 37883329 and 24670687.

## 9. Falsifier checks, as pre-registered in Section 5.8

| Pre-registered falsifier | Status in this slice |
|---|---|
| "Every new drug is REMOVED" is falsified by any drug passing C1, C3 and C5 with a reading on each | Not reached either way. No drug passed, and no drug in this slice has a C3 or C5 reading to pass with. The premise behind the outcome is not "all removed" but "mostly not evaluable", which is a different and weaker claim, and the write-up must say so |
| A class disposal is sound unless a primary source shows a member acting oppositely at an achievable exposure | For the vinca class I looked for a source showing any vinca alkaloid raising BUBR1 protein (search 2, count 29) and found none. For the mTOR-inhibitor class I looked for a rapalog raising BUBR1 (search 6, count 10) and found none. Neither disposal is falsified on the evidence reachable this run |
| "Also considered" rows are a small residue | Not my call to make: the count comparison is at universe level and `BATCHES.md` already recorded it as not falsified. My eight rows behaved like the rest of the slice, with no mechanism arm |
| The procedure is reproducible | C1 and C2 are reproducible from the box scripts and the public files, and the two re-measured DepMap genes reproduced T2-P4 exactly. The C3 readings are abstract-level and reproducible from the PMIDs and the verbatim queries |

## 10. Limitations of this evaluation, stated plainly

- Direction readings are from abstracts. No full text was obtained this run, so the concentration
  at which the vinca BUBR1 cleavage occurs is [U] for both removal sources. If a reader needs the
  removal to rest on a concentration comparison rather than on a sign, the removal is not
  supported at that standard and the honest fallback is E-UNRESOLVED with an AGAINST risk.
- The EU limb of C1 was not queried for any row. For the four rows with no authorised US product
  this matters most: perhexiline, rilmenidine, quinacrine and terfenadine are left UNRESOLVED on
  C1 rather than resolved, which is what pre-registration Section 2.1 directs.
- Paediatric label statements were retrieved for eight of 49 rows. Disclosed as a depth limit,
  permitted because C1's paediatric limb is reported and never exclusionary.
- Twenty-four rows are co-occurrence artefacts of the frozen extraction rule and its disclosed
  looser implementation. Calling them UNRESOLVED is correct under the frozen outcomes but it
  should not be read as "these drugs might work": nobody proposed them for this mechanism, and the
  screen reached them because a sensitivity paper mentioned both names.
- Nothing in this result says anything about benefit, and nothing says anything about any person.

## 11. Observation outside my slice, passed on rather than acted on

Search 5 returned PMID 35639235, verbatim: "ChIP analysis revealed that SIRT1 could bind to the
**promoter of BubR1** ... to upregulate its expression. Overexpression of BubR1 decreased MC
whereas knockdown of BubR1 increased it" [V, abstract]. That is a transcriptional route by which
SIRT1 raises BubR1 expression, in cancer lines. It bears on the SIRT1-targeting drugs in Batch 2
and on the NAD route, not on any row in my slice, so I did not evaluate it and I claim no verdict
from it. Recorded so it is not lost.

## 12. Files

Mac: `scratchpad/agent_out/nonchoices/RESULT_B4c.md` (this file).
Box, `~/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4c/`: this file,
`c1_fda_bulk.py`, `names_b4c.txt`, `c1_b4c.tsv`, `c2_depmap_b4c.py`, `c2_b4c.tsv`.
No existing file was edited, and nothing outside this work directory was deleted.
