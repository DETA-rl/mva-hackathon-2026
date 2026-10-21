# RESULT-B4a: evaluation of Batch 4, part A (items 1 to 49) of the non-choices universe

Governed by `PRE_REG_NONCHOICES.md`, sha256
`ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4` (verified against the file
before this evaluation started), and by the batch list `BATCHES.md`. Criterion C3 applies
`PRE_REG_R2B_EXPOSURE.md`, sha256
`338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534` (verified). No criterion was
amended and no threshold is new.

Agent: nc-eval-b4a. Scope: the first 49 rows of Batch 4 in the order listed in BATCHES.md.
Items 50 to 98 and 99 to 147 are evaluated separately.

Non-clinical clause: this is a hypothesis-screening document about published mechanism, label
and database facts. It is not clinical advice, it proposes no dose or regimen for any person,
and nothing here may be read as a recommendation to administer anything. No patient-derived
data was used. Every query that left this machine carried a drug name, a gene symbol, a
mechanism term or a PMID, and nothing else. No existing file was edited and nothing was deleted
outside the work directory.

VERIFIED [V] means read at the named source this run or computed here from the public file on
the box. UNVERIFIED [U] means anything else and is marked inline.

---

## 1. Headline

| Outcome | Count |
|---|---|
| REMOVED | 9 |
| KEPT AS CANDIDATE | 0 |
| UNRESOLVED | 40 |

No drug in this third passed C1, C3 and C5 with a reading on each, so none joins the ranked
list. The pre-registered falsifier of "every new drug is REMOVED" is not reached either: 40 of
49 rows are UNRESOLVED, which under the frozen rule removes nothing and is not read as safety.

The substantive finding is about the universe, not about any drug. Forty of these 49 rows have
no mechanism arm at all: the record that put the drug into the universe measures BubR1 or the
checkpoint as a marker of sensitivity to the drug, or names the drug only in a gene-list
bioinformatics paper, or names it as a laboratory tool. Nothing proposes the drug for raising
BUBR1. Under the frozen C3 that is E-UNRESOLVED, exactly as the NR arm was scored
E-UNRESOLVED in RESULT-R2B-EXPOSURE for the same reason ("no source tests the arm"). It is not
a removal, and this file does not dress it up as one.

## 2. What was run, per criterion

**C1, regulatory class** [V]. Source: the public Drugs@FDA bulk download already on the box
(`dl_fda/`, downloaded 2026-10-16), tables `Products.txt`, `MarketingStatus.txt`,
`MarketingStatus_Lookup.txt`. Reading per pre-registration Section 5.1. No API call was needed.
Script `b4a_c1_class.py`. Disclosed implementation detail: an ingredient matches a query name
if it equals the name or begins with the name followed by a space, so salt and ester forms
("amikacin sulfate" for amikacin) are caught, matching the pre-registration Section 4
normalisation that collapses salts to the parent. The first pass without that rule returned
zero products for 15 names that do have authorised products; both passes are kept on the box
(`c1_drugsatfda.json`, `c1_drugsatfda_salts.json`) so the rule is auditable.
Result: 45 of 49 names have authorised US single-agent systemic products. Every one of those
reads Rx except aspirin and epinephrine, which also have authorised non-prescription products
and therefore read OTC. Four names have no authorised US drug product under this source:
amsacrine, beta-hydroxy-beta-methylbutyrate, dequalinium, ebastine. Of those, HMB is a dietary
supplement, which is the class the rule assigns when no authorised drug product exists; for
amsacrine, dequalinium and ebastine the EMA route named in Section 5.1 was not run, so their
C1 is UNRESOLVED rather than silently kept or silently dropped. This changes nothing
downstream, because C3 returns no arm for any of the three.
Paediatric label statements were not retrieved for this third. Section 5.1 reports them and
never excludes on them, and no row here turns on one. Recorded as a gap, not worked around.

**C2, DepMap dependency flags** [V]. Method identical to `p5_depmap_safety.py` (T2-P5): DepMap
24Q4 `CRISPRGeneEffect.csv` and `Model.csv`, column matched on the symbol before " (", fraction
of lines with Chronos gene effect < -0.5 over all lines with a value, blood-lineage median over
OncotreeLineage in {Myeloid, Lymphoid}, flag at fraction >= 0.25. Script `b4a_c2_depmap.py`,
output `c2_depmap_b4a.tsv`, 1178 cell lines, 135 blood-lineage lines.

| Gene | n lines | fraction Chronos < -0.5 | flag | blood median |
|---|---|---|---|---|
| MTOR | 1178 | 0.986 | YES | -1.130 |
| AURKB | 1178 | 1.000 | YES | -2.420 |
| PLK4 | 1178 | 0.982 | YES | -1.281 |
| CDC20 | 1178 | 1.000 | YES | -1.894 |
| KIF18A | 1178 | 0.885 | YES | -0.839 |

MTOR 0.986, PLK4 0.982, KIF18A 0.885 and CDC20 1.000 reproduce the T2-P4 values recorded in the
register to three decimals, which is the method check. AURKB is measured here for the first
time. Per pre-registration Section 5.2 no DepMap flag removed any drug in this file, AURKB
included, and the caveat travels unchanged: a CRISPR knockout is a loss-of-function proxy in
cancer lines, never normal marrow, so no flag is a safety verdict and no absent flag is a
safety clearance.

**C3, exposure and mechanism direction** [V for the searches and the quoted sources]. The
frozen R2-B rule. Direction was searched before it was judged, with one query shape fixed for
every row so that no drug got a friendlier search:

`<drug>[tiab] AND (BUB1B[tiab] OR BubR1[tiab] OR "spindle assembly checkpoint"[tiab] OR "mitotic checkpoint"[tiab] OR "chromosome missegregation"[tiab])`

Script `b4a_c3_search.py`, counts and PMIDs in `c3_direction_search.json`; titles for every
returned record in `c3_titles.tsv`; the deciding abstracts in `b4a_abstracts.txt`. Twenty-four
of the 49 rows return zero records. For the 25 rows with records, every record was read at
title level and the candidates for a direction were read at abstract level. No achieved free
concentration or C_demo could be computed for any row in this third, because no row has a
mechanism arm with a demonstrated concentration; where a direction was established it was
established on the direction limb, which is how FIN-1 was decided in RESULT-R2B-EXPOSURE.

**C4** is computed and reported where it can be computed and removes nothing, fixed by
pre-registration Section 5.4 before the universe was known. For every row in this third it
cannot be computed: none has an enzyme IC50 plus a mechanism claim of the C4 type. Reported as
"not computable", and this is not a finding about any drug.

**C5, evidence grade** under RANKING-RULE-T2. Every row in this third is G4 at best (mechanism
or pathway evidence only). For the 24 rows with zero records and for the rows whose only
records are gene-list bioinformatics papers, there is no BUBR1-directed evidence at any grade,
which is weaker than G4 rather than equal to it. No row reaches G3, because no source reports
mouse or cell-line data on BUBR1 protein or checkpoint endpoints produced by the drug in the
direction of the endpoint.

## 3. Mechanism classes and the primary source that decided each

Grouped for evidence, applied per drug. Each source was read at abstract level this run.

**Class AURKB-inhibition claim.** Deciding source PMID 12719470 (Ditchfield 2003, J Cell Biol)
[V, verbatim]: with the Aurora kinase inhibitor ZM447439, "ZM447439-treated cells exit mitosis
with normal kinetics, indicating that the spindle checkpoint is compromised", "ZM447439 prevents
mitotic arrest after exposure to paclitaxel", and "In the absence of Aurora B function,
kinetochore localization of the spindle checkpoint components BubR1, Mad2, and Cenp-E is
diminished", with Aurora B activity also required for "the rebinding of BubR1 to metaphase
kinetochores after a reduction in centromeric tension". Both limbs of the R2-B AGAINST
definition are met: BUBR1 at kinetochores is lowered and the checkpoint is compromised.
Supporting current source PMID 37443114 (Mol Cancer 2023) [V]: "abrogation of the spindle
assembly checkpoint by AURKB or TTK inhibitors", stated as the class effect of drugs in
clinical development. Applies to belumosudil, copanlisib, dasatinib, entrectinib, erlotinib,
whose claimed mechanism in the screen is AURKB.

**Class mTOR-inhibition claim and PLK4-inhibition claim.** These two classes already carry a
frozen class-level disposal by T2-P4 (register: MTOR fraction 0.986, PLK4 0.982), and
pre-registration Section 5.6 carries a class disposal to every member of the class. Applies to
alpelisib and copanlisib (explicit "MTOR inhibitor" strings) and axitinib (explicit "PLK4
inhibitor" string). Stated plainly because it matters: no new DepMap measurement removed
anything here. Section 5.2 forbids extending the T2-P4 dependency precedent to a new drug as a
new rule, and Section 5.6 carries an existing class disposal to class members; these three rows
rest on the second. Under the stricter reading of Section 5.2 they would be labelled "already
evaluated at class level" instead of REMOVED. The label changes, the disposition does not, and
a reader may prefer the stricter label.

**Bare target annotations are not inhibitor claims.** For amiodarone, amsacrine,
beta-hydroxy-beta-methylbutyrate, capivasertib, dequalinium, doxazosin, ebastine and
epinephrine the screen carries a bare "targets MTOR" annotation from DGIdb with no mechanism
string, and each drug's label mechanism is unrelated to mTOR. The class disposal was NOT
applied to them, because the deciding evidence for the class is about mTOR inhibition and the
annotation does not claim it. They are UNRESOLVED. The alternative reading is recorded for
honesty: if the annotation were read as mTOR modulation, the class disposal would apply and
those rows would be REMOVED, so neither reading carries them forward.

**The AURKB rows carry the same dual reading.** The DGIdb target claim for belumosudil
(a ROCK2 inhibitor by label), dasatinib, entrectinib and erlotinib is UNVERIFIED [U] and is not
their label mechanism. Evaluated on the claimed mechanism, as C3 requires, the direction is
AGAINST and the row is REMOVED. Discount the claim and the row has no mechanism arm at all,
which is E-UNRESOLVED. Neither reading keeps the drug, and the removal is reported on the
claimed mechanism because that claim is what put the drug in the universe.

**Genotoxic and cytotoxic agents, the honest limit.** One agent in this third has a primary
source on the direction of its own mitotic effect: bleomycin, PMID 18723675 (Anantha 2008, PNAS)
[V, verbatim], where mitotic DNA damage caused by bleomycin treatment is followed by "mitotic
release into a 2N G(1) phase", and cells unable to phosphorylate RPA2 showed "a significant
defect in mitotic release" and were "positive initially for cyclin B expression and BubR1
chromatin staining, indicative of an extended spindle assembly checkpoint". Read on the R2-B
definition, the drug's own damage is followed by exit from a checkpoint-associated arrest rather
than by preserving it, which is AGAINST. That reading is stated so a reviewer can reject the
label while seeing the same sentences. It is NOT extended to the other genotoxic agents in this
third: carboplatin, cisplatin, capecitabine, cytarabine, cladribine, decitabine, bendamustine,
dexrazoxane and azathioprine stay UNRESOLVED, each with the direction risk reported, because no
source read this run establishes the sign of their effect on BUBR1 or on checkpoint function.
Removing nine drugs on one bleomycin paper would have been the convenient result and is not
supported.

**Arsenic trioxide is decided individually** [V, verbatim], PMID 19397590 (Cell Prolif 2009):
"As(2)O(3) significantly blocked phosphorylation of BubR1, Cdc20, and Cdc27 in cells treated
with paclitaxel, suggesting that arsenic compromised the activation of the spindle checkpoint",
in a paper that also records that it inhibits tubulin polymerization and "greatly attenuated
paclitaxel-induced mitotic arrest". AGAINST on the checkpoint limb.

## 4. The table

Columns: C1 is the regulatory class read from the bulk Drugs@FDA tables. C2 is the DepMap flag
for the gene the screen named, which removes nothing. C3 is the direction limb of the frozen
R2-B rule with the record count returned by the fixed query. C4 is not computable for any row.
C5 is the RANKING-RULE-T2 grade. "Source record" is abbreviated from BATCHES.md.

| # | Drug | Claimed mechanism in the screen | C1 | C2 | C3 direction, records returned, deciding evidence | C5 | Outcome and deciding test |
|---|---|---|---|---|---|---|---|
| 1 | afatinib | none, literature co-occurrence (PMID 36605099 and 2 others) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm; C3 route returned nothing |
| 2 | alpelisib | "MTOR inhibitor" (rxcui:2169285) | Rx [V] | MTOR 0.986 flagged | not reached | G4 | REMOVED, T2-P4 class disposal for mTOR inhibitors carried under Section 5.6, MTOR 0.986 |
| 3 | amikacin | none, co-occurrence (PMID 41579174) | Rx [V] | no target named | UNKNOWN, 1 record, a yeast aminoglycoside-sensitivity paper (36708127) | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 4 | amiodarone | bare "targets MTOR" (rxcui:203114) | Rx [V] | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, bare annotation is not an inhibitor claim; see Section 3 |
| 5 | amsacrine | bare "targets MTOR" (rxcui:739) | no authorised US product; EMA route not run | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED on C1 and C3 |
| 6 | arsenic trioxide | none, co-occurrence (PMID 18501396 and 3 others) | Rx [V] | no target named | **AGAINST** [V], 6 records, PMID 19397590 blocks BubR1, Cdc20 and Cdc27 phosphorylation and compromises checkpoint activation | G4 | **REMOVED**, C3 direction AGAINST, E-FAIL (i) |
| 7 | ascorbic acid | none, co-occurrence (PMID 31478449, 40595080) | Rx products exist [V]; also a dietary supplement | no target named | UNKNOWN, 2 records; PMID 39845481 is the closest signal in this third, see Section 5 | G4 at best | UNRESOLVED, stress-dependence clause; BUBR1 not measured after the agent |
| 8 | aspirin | none, co-occurrence (PMID 40702150) | OTC products exist [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 9 | atorvastatin | none, co-occurrence (PMID 42146413) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 10 | axitinib | "PLK4 inhibitor" (rxcui:1242999) | Rx [V] | PLK4 0.982 flagged | not reached | G4 | REMOVED, T2-P4 class disposal for PLK4 inhibitors carried under Section 5.6, PLK4 0.982 |
| 11 | azathioprine | none, co-occurrence (PMID 33767726) | Rx [V] | no target named | UNKNOWN, 1 record, a hub-gene bioinformatics paper | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 12 | baricitinib | none, co-occurrence (PMID 42278672) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 13 | belumosudil | bare "targets AURKB" (rxcui:2564025) | Rx [V] | AURKB 1.000 flagged, removes nothing | **AGAINST** [V] on the claimed mechanism, 0 records for the drug itself, class source PMID 12719470 | G4 | **REMOVED**, C3 direction AGAINST on the AURKB claim, E-FAIL (i); dual reading in Section 3 |
| 14 | bendamustine | none, co-occurrence (PMID 40068082) | Rx [V] | no target named | UNKNOWN, 2 records, both myeloma sensitivity studies | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 15 | beta-hydroxy-beta-methylbutyrate | bare "targets MTOR" (drugbank:DB15344) | no authorised drug product, so dietary supplement [V] | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, bare annotation is not an inhibitor claim |
| 16 | bleomycin | none, co-occurrence (PMID 25483095) | Rx [V] | no target named | **AGAINST** [V], 7 records, PMID 18723675 mitotic DNA damage followed by release into 2N G1, extended checkpoint only when the RPA2 sites are mutated | G4 | **REMOVED**, C3 direction AGAINST, E-FAIL (i); reading stated in Section 3 and not extended to other genotoxics |
| 17 | cabozantinib | none, co-occurrence (PMID 39911278, 41545558) | Rx [V] | no target named | UNKNOWN, 1 record, a hub-gene bioinformatics paper | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 18 | calcitriol | none, co-occurrence (PMID 36389792, 40286596) | Rx [V] | no target named | UNKNOWN, 2 records, both gene-list bioinformatics papers | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 19 | canagliflozin | none, co-occurrence (PMID 38513740) | Rx [V] | no target named | UNKNOWN, 1 record, sensitisation of cancer cells to a microtubule poison | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 20 | capecitabine | none, co-occurrence (PMID 24519527) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 21 | capivasertib | bare "targets MTOR" (rxcui:2669967) | Rx [V] | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, bare annotation is not an inhibitor claim |
| 22 | carbon dioxide | none, co-occurrence (PMID 37274003) | Rx medical gas products exist [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, lexicon artefact of the extraction deviation recorded in BATCHES.md Section 2.3, not a drug proposal |
| 23 | carboplatin | none, co-occurrence (PMID 31987036 and 3 others) | Rx [V] | no target named | UNKNOWN, 8 records, all biomarker or sensitivity studies | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 24 | chloroquine | none, co-occurrence (PMID 35847923) | Rx [V] | no target named | UNKNOWN, 1 record; PMID 32573315 uses chloroquine as a lysosomal inhibitor tool and reports that lysosome impairment increases mitotic timing, causes mitotic errors and promotes chromosomal instability [V] | G4 at best | UNRESOLVED on the frozen direction definition; chromosomal-instability risk reported, not used to remove |
| 25 | chlorpromazine | none, co-occurrence (PMID 33708237, 37808164) | Rx [V] | no target named | UNKNOWN, 1 record; PMID 19713760 identifies it as an inhibitor of mitotic slippage in cells arrested by a spindle poison, with increased cancer-cell survival and proliferation reported as the outcome [V] | G4 at best | UNRESOLVED, stress-dependence clause: the action is shown only under an applied spindle poison and no BUBR1 endpoint is measured |
| 26 | cisplatin | none, co-occurrence (PMID 24519527 and 3 others) | Rx [V] | no target named | UNKNOWN, 50 records, none showing an effect of the drug on BUBR1; the closest, PMID 38048028, lowers BUBR1 by shRNA and reads out drug sensitivity, which is the reverse inference | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 27 | cladribine | none, co-occurrence (PMID 33083112, 37808164) | Rx [V] | no target named | UNKNOWN, 2 records, a myeloma sensitivity study and a hub-gene paper | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 28 | copanlisib | "MTOR inhibitor" plus "targets AURKB" (rxcui:1945077) | authorised US product discontinued [V] | MTOR 0.986 and AURKB 1.000 flagged | **AGAINST** [V] on the AURKB claim, class source PMID 12719470 | G4 | **REMOVED** on two independent grounds: C3 direction AGAINST, and the T2-P4 mTOR class disposal under Section 5.6 |
| 29 | cyclosporine | none, co-occurrence (PMID 40286596, 41381790) | Rx [V] | no target named | UNKNOWN, 2 records, both gene-list bioinformatics papers | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 30 | cytarabine | none, co-occurrence (PMID 37808164) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 31 | dasatinib | bare "targets AURKB, PLK4" (rxcui:1546019) | Rx [V] | AURKB 1.000 and PLK4 0.982 flagged | **AGAINST** [V] on the AURKB claim, class source PMID 12719470; its own 4 records include an in silico paper proposing BUB1B inhibitors, the opposite goal | G4 | **REMOVED**, C3 direction AGAINST, plus the T2-P4 PLK4 class disposal |
| 32 | decitabine | none, co-occurrence (PMID 37002311) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm; genotoxic-class risk reported |
| 33 | dequalinium | bare "targets MTOR" (rxcui:3226) | no authorised US product; EMA route not run | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED on C1 and C3 |
| 34 | dexamethasone | none, co-occurrence (PMID 32850387 and 3 others) | Rx [V] | no target named | UNKNOWN, 4 records, none on the direction of a dexamethasone effect on BUBR1 | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 35 | dexrazoxane | none, co-occurrence (PMID 37808164, 42483440) | Rx [V] | no target named | UNKNOWN, 1 record, a gene-signature paper | no BUBR1 evidence | UNRESOLVED, no mechanism arm; topoisomerase-class risk reported |
| 36 | digoxin | "also considered, reached outside the stated screen" | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 37 | donepezil | none, co-occurrence (PMID 32764382, 32850387) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 38 | doxazosin | bare "targets MTOR" (rxcui:39173) | Rx [V] | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, bare annotation is not an inhibitor claim |
| 39 | doxycycline | none, co-occurrence (PMID 16227576) | Rx [V] | no target named | UNKNOWN, 6 records; in the only BubR1 record, PMID 16227576, doxycycline is the inducer of a tetracycline-inducible construct, not the agent under study [V] | no BUBR1 evidence | UNRESOLVED, co-occurrence is an inducible-expression-system artefact |
| 40 | ebastine | bare "targets MTOR" (rxcui:23796) | no authorised US product; EMA route not run | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED on C1 and C3 |
| 41 | eltrombopag | none, co-occurrence (PMID 41439111) | Rx [V] | no target named | UNKNOWN, 1 record, a drug-repositioning gene-list paper | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 42 | entrectinib | bare "targets AURKB, PLK4" (rxcui:2197862) | Rx [V] | AURKB 1.000 and PLK4 0.982 flagged | **AGAINST** [V] on the AURKB claim, class source PMID 12719470 | G4 | **REMOVED**, C3 direction AGAINST, plus the T2-P4 PLK4 class disposal |
| 43 | enzalutamide | none, co-occurrence (PMID 42757823) | Rx [V] | no target named | UNKNOWN, 1 record; PMID 42757823 proposes inhibiting the BUB1B to CENP-E axis in resistant prostate cancer, the opposite of this project's endpoint, and reports no enzalutamide effect on BUBR1 [V] | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 44 | epinephrine | bare "targets MTOR" (rxcui:3992) | OTC products exist [V] | MTOR 0.986 flagged | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, bare annotation is not an inhibitor claim |
| 45 | erlotinib | bare "targets AURKB" (rxcui:337525) | Rx [V] | AURKB 1.000 flagged | **AGAINST** [V] on the AURKB claim, class source PMID 12719470; its own 2 records are a glioma PARP study and a pharmacogenomics review | G4 | **REMOVED**, C3 direction AGAINST on the AURKB claim, E-FAIL (i) |
| 46 | estradiol | none, co-occurrence (PMID 32151056, 36389792) | Rx [V] | no target named | UNKNOWN, 7 records, none on an estradiol effect on BUBR1; PMID 17234781 concerns 2-methoxyestradiol, a different molecule | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 47 | estradiol and progesterone | none, co-occurrence (PMID 36389792) | Rx [V] | no target named | UNKNOWN, 14 records for progesterone, none on a progesterone effect on BUBR1; PMID 21340479 concerns unliganded progesterone receptors attenuating taxane-induced death | no BUBR1 evidence | UNRESOLVED, no mechanism arm; combination product row kept as the screen returned it |
| 48 | etomidate | none, co-occurrence (PMID 40565600) | Rx [V] | no target named | UNKNOWN, 0 records | no BUBR1 evidence | UNRESOLVED, no mechanism arm |
| 49 | dapagliflozin | none, co-occurrence (PMID 38513740) | Rx [V] | no target named | UNKNOWN, 1 record, the canagliflozin paclitaxel-sensitisation paper | no BUBR1 evidence | UNRESOLVED, no mechanism arm |

Row order follows BATCHES.md with one correction: dapagliflozin is row 31 in the BATCHES.md
alphabetical listing and appears here as row 49. The set of 49 drugs evaluated is unchanged;
only the printed position differs, and the three parts of this batch were split on the
BATCHES.md order, so no drug is evaluated twice and none is skipped.

## 5. The one signal worth reporting, and why it still does not pass

Ascorbic acid, PMID 39845481 (Reprod Med Biol 2025) [V, read at abstract]. In oocytes from
Sod1-deficient mice matured in vitro at 21 percent oxygen, chromosome misalignment and
segregation errors rose, and this "was associated with a decrease in the recruitment of BUBR1 to
kinetochores at M I stage"; the authors conclude that oxidative stress "impairs the spindle
assembly checkpoint function due to a decrease in the recruitment of BUBR1". Adding L-ascorbic
acid or N-acetyl-L-cysteine during maturation "reduced the frequency of chromosome segregation
errors in Sod1KO oocytes".

This is the only record in this third in which an agent moves a segregation endpoint in the
direction this project wants. It still does not pass C3, for two reasons fixed before the
universe was known:

1. BUBR1 was not measured after the agent. The paper reports the segregation-error rate after
   ascorbic acid, not a BUBR1 protein or kinetochore-recruitment value, so there is no C_demo
   for the BUBR1 endpoint and no R can be computed.
2. The R2-B stress-dependence clause. The effect is demonstrated only under an applied stress
   (Sod1 knockout plus 21 percent oxygen in vitro maturation) and the arm would require action
   in cells without that applied oxidative stress, so first-step competence is NOT ESTABLISHED
   and direction cannot be TOWARD. This is the same clause that held the arimoclomol arm at
   E-UNRESOLVED in RESULT-R2B-EXPOSURE, applied identically here.

Outcome UNRESOLVED, not REMOVED and not KEPT. Reported because the pre-registration requires
that a drug which could plausibly pass be identified as such even when it does not pass, and
because the companion finding is a mechanism statement a later test could use: an independent
source outside this project's prior reading reports that oxidative stress lowers BUBR1 at
kinetochores and impairs checkpoint function in a mammalian model. Noted as a lead, with the
limits stated: mouse oocytes, in vitro maturation, a knockout-driven stress, no human data, no
BUBR1 readout after the agent, and N-acetylcysteine already sits in the universe as an
"also considered" row in Batch 1 rather than in this third.

## 6. Negative results and limits, recorded as required

1. **Nothing in this third was kept.** Zero of 49 rows pass C1, C3 and C5 with a reading on
   each, so the ranked list is unchanged by this file.
2. **Most rows are not removed either.** Forty of 49 are UNRESOLVED. UNRESOLVED never removes
   and is never read as safety. A reader who wants a shorter non-choices section will not get
   one from this third without a new rule, and no new rule was written.
3. **The deciding evidence is thin where it exists.** Five of the nine removals rest on a single
   2003 primary source for the Aurora B class, applied to drugs whose AURKB target claim is an
   UNVERIFIED database annotation rather than their label mechanism. Both halves of that are
   stated in Section 3. Two more removals carry an existing class disposal rather than new
   evidence. Only two removals, arsenic trioxide and bleomycin, rest on a primary source about
   that drug itself.
4. **The genotoxic class was not disposed of as a class.** The convenient result was available
   and is not supported by a source read this run. Nine genotoxic or cytotoxic agents stay
   UNRESOLVED with their direction risk reported.
5. **BATCHES.md finding 2.2 is confirmed from the other side.** The literature arm's top names
   are in this third, and reading their records one by one shows the co-occurrence is
   sensitivity-marker work, gene-list bioinformatics, or a laboratory tool use. Doxycycline is
   the clearest single case: its only BubR1 record uses it to induce a transgene.
6. **Coverage limits of this evaluation.** C1 paediatric label statements were not retrieved for
   this third; the EMA route was not run for the three names without a US product; no full text
   was read, only titles and abstracts, so a direction stated only in a full text is missed; the
   fixed C3 query is title and abstract only and will miss a drug discussed under a synonym it
   does not contain; and the progesterone row was searched under "progesterone" rather than the
   combination name, which is recorded as a deviation in favour of finding more records.
7. **No row's outcome was decided by C2 or C4.** C4 is not computable anywhere in this third and
   C2 removed nothing, as fixed in advance.

## 7. Falsifier check, as pre-registered

| Pre-registered falsifier | Status after this third |
|---|---|
| "Every new drug is REMOVED" would be falsified by any drug passing C1, C3 and C5 with a reading on each | Not reached, and not the outcome either: 9 removed, 40 unresolved, 0 passing |
| A class disposal is sound unless a primary source shows a member acting oppositely at an achievable exposure | No such source was found this run for the mTOR or PLK4 class rows; the Aurora B class source was read and supports the class direction |
| The procedure is reproducible if counts reconcile on a re-run | The DepMap check reproduces the register's T2-P4 values for MTOR, PLK4, KIF18A and CDC20 to three decimals; the C1 and C3 counts are in the JSON and TSV files on the box and re-run from the scripts named below |

## 8. Files and reproducibility

Box, `~/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4a/`: `b4a_c1_class.py`,
`b4a_c2_depmap.py`, `b4a_c3_search.py`, `b4a_c3_titles.py`, `b4a_abstracts.py`,
`c1_drugsatfda.json`, `c1_drugsatfda_salts.json`, `c2_depmap_b4a.tsv`,
`c3_direction_search.json`, `c3_titles.tsv`, `c3_titles.json`, `b4a_abstracts.xml`,
`b4a_abstracts.txt`, and this file as `RESULT_B4a.md`.
Mac: `scratchpad/agent_out/nonchoices/RESULT_B4a.md`.

Inputs: DepMap 24Q4 `CRISPRGeneEffect.csv` and `Model.csv` at
`~/Documents/HACKATON/_private/public_data/depmap_24Q4/`; the public Drugs@FDA bulk tables at
`~/Documents/HACKATON/_private/agent_out/nonchoices/dl_fda/` (downloaded 2026-10-16); PubMed
E-utilities esearch, esummary and efetch, queried by drug name, mechanism term and PMID only.

Amendment policy: this file is not amended. A correction is a separate addendum with its own
hash, stating what changed and why, with this file left in place.
