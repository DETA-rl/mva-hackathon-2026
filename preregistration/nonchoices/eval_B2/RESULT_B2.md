# RESULT B2: NAD+, sirtuin and acetyltransferase route (20 drugs)

Governed by `PRE_REG_NONCHOICES.md`, sha256
`ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4`, and by the R2-B exposure
rule `PRE_REG_R2B_EXPOSURE.md`, sha256
`338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534`. Both hashes were verified
against the files before this evaluation started. No criterion was amended and no threshold is
new. No existing file was edited and nothing was deleted outside the work directory.

Non-clinical clause, repeated from the governing documents: this is a hypothesis-screening
document about published mechanism and database facts. It is not clinical advice, proposes no
dose or regimen for any person, and must not be read as a recommendation to administer
anything. No removal below is a safety finding about any drug, and no absent flag is a safety
clearance.

Public data only. Only drug names, gene symbols, mechanism terms and PMIDs left this machine.

VERIFIED means retrieved this run from the named API or computed here from a public file.
UNVERIFIED is labelled inline.

---

## 1. Direction anchors, retrieved at source before any drug was scored

Two primary sources fix the sign of this route, and they point in opposite directions at two
different lysines. Both were read at source this run.

**K668 limb, PMID 24825348** (North BJ et al., EMBO J 2014;33(13):1438-53), VERIFIED:

> the loss of BubR1 levels with age is due to a decline in NAD(+) and the ability of SIRT2 to
> maintain lysine-668 of BubR1 in a deacetylated state, which is counteracted by the
> acetyltransferase CBP

So on this limb: SIRT2 activity raises BubR1, sirtuin inhibition lowers it, and **CBP
(CREBBP) inhibition is the TOWARD direction**.

**K250 limb, PMID 19407811** (Choi E et al., EMBO J 2009;28(14):2077-89), VERIFIED:

> BubR1 forms a complex with PCAF and is acetylated at lysine 250 ... BubR1 acetylation was
> required for checkpoint function, through the inhibition of ubiquitin-dependent BubR1
> degradation ... the acetylation-deficient mutant, BubR1-K250R, was unstable

So on this limb: **PCAF (KAT2B) inhibition is the AGAINST direction**, because it removes an
acetylation that protects BubR1 from degradation.

This split is the deciding instrument for the acetyltransferase entrants in this batch. An
acetyltransferase inhibitor is not helpful as a class. It is helpful only if it spares PCAF.
The briefing note that "acetyltransferase inhibitors push the other way" holds for the K668
limb only, and checking each drug against source rather than against the class is what
separates curcumin from epigallocatechin gallate below.

---

## 2. Criteria as applied

- **C1** regulatory class, from the Drugs@FDA `Products.txt` lexicon shipped with this batch
  (6,846 names), matched on `ActiveIngredient`. Reported, never exclusionary. Limitation
  declared: the DailyMed and EMA limbs of C1 were not run this run, so "no authorised drug
  product" below means no US product in Drugs@FDA, not absence of any authorisation anywhere.
  This matters for idebenone, suramin and papaverine and is flagged on their rows.
- **C2** DepMap 24Q4, method copied verbatim from `p5_depmap_safety.py`: fraction of lines with
  Chronos < -0.5 over all lines with a value, flag at >= 0.25, blood lineage median over
  OncotreeLineage in {Myeloid, Lymphoid}, absent genes "not measured" and never 0. Run on the
  box over 1,178 lines, 348 blood lineage. A flag does not remove a drug here; it is the
  RANKING-RULE-T2 safety tie-break input.
- **C3** the frozen R2-B rule, verbatim, including the node rule, the transcriptional override
  and the stress-dependence clause. E-UNRESOLVED never removes.
- **C4** computed where computable and removes nothing, per Section 5.4.
- **C5** RANKING-RULE-T2 grades G1 to G4.

### C2 table, all named targets measured

| Gene | Group | n lines | frac Chronos < -0.5 | Flag >= 0.25 | Blood median | Blood n |
|---|---|---|---|---|---|---|
| SIRT1 | named | 1178 | 0.004 | no | 0.089 | 135 |
| SIRT2 | named | 1178 | 0.006 | no | -0.036 | 135 |
| CREBBP | named | 1178 | 0.076 | no | -0.070 | 135 |
| EP300 | named | 1178 | **0.284** | **YES** | -0.761 | 135 |
| KAT2B | named | 1178 | 0.000 | no | -0.042 | 135 |
| FDPS | context | 1178 | 0.582 | YES | -0.840 | 135 |
| EGFR | context | 1178 | 0.190 | no | -0.146 | 135 |
| TUBB | context | 1178 | 0.964 | YES | -1.881 | 135 |
| GABRA1 | context | 1178 | 0.000 | no | 0.038 | 135 |
| SLC6A3 | context | 1178 | 0.001 | no | 0.031 | 135 |
| PDE10A | context | 1178 | 0.001 | no | 0.026 | 135 |

The context rows are the real pharmacological targets of the artefact rows of Section 4. They
are reported beyond criterion C2, which asks only for the named targets, because they are the
genes a reader would otherwise assume were tested. EP300 is the only flagged named target.
Carried caveat, unchanged: a CRISPR knockout is a loss-of-function proxy in cancer lines, never
normal marrow.

---

## 3. Verdict table

| Drug | C1 | C2 flags | C3 outcome, direction and R | C5 | Outcome | Deciding evidence |
|---|---|---|---|---|---|---|
| curcumin | no authorised drug product (supplement for the rule) | EP300 flagged 0.284, blood median -0.761; CREBBP no | **TOWARD**, E-UNRESOLVED; C_free < 0.14 uM, C_demo not numerically sourced so R not computable | G4 | **KEPT AS CANDIDATE** | PMID 15383533 inhibits p300/CBP HAT "but not of p300/CBP-associated factor"; anchor PMID 24825348 |
| epigallocatechin gallate | no authorised drug product (supplement) | EP300 flagged 0.284; KAT2B no | **AGAINST**, E-FAIL; C_demo 100 uM | G4 | **REMOVED** | PMID 19147572 global HAT inhibition, with PMID 19407811 K250 protection |
| fisetin | no authorised drug product (supplement) | no named target assigned | **AGAINST**, E-FAIL, in unperturbed cells | G3 against | **REMOVED** | PMID 19395653 BubR1 lost from kinetochores, forced mitotic exit |
| suramin | no authorised US drug product | SIRT1 no, SIRT2 no | **AGAINST**, E-FAIL; sirtuin IC50 22 uM | G4 | **REMOVED** | PMID 17355872 sirtuin deacetylase inhibition at the NAD+ site, against anchor PMID 24825348 |
| alendronate | Rx | SIRT1 no (FDPS 0.582 flagged, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | claimed SIRT1 target unsupported; route named in Section 4 |
| ibandronic acid | Rx | SIRT1 no (FDPS flagged, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | as above |
| risedronic acid | Rx | SIRT1 no (FDPS flagged, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | as above |
| zoledronic acid | Rx | SIRT1 no (FDPS flagged, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | as above |
| alprazolam | Rx | CREBBP no (GABRA1 no, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | claimed CREBBP target unsupported; route named in Section 4 |
| estazolam | Rx | CREBBP no | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | as above |
| midazolam | Rx | CREBBP no | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | as above |
| triazolam | Rx | CREBBP no, KAT2B no | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | as above |
| methylphenidate | Rx | CREBBP no, EP300 flagged 0.284 | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | `methylphenidate AND (CREBBP OR EP300)` returned 0 |
| papaverine | no authorised US drug product | CREBBP no (PDE10A no, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | claimed CREBBP target unsupported |
| colchicine | Rx | CREBBP no (TUBB 0.964 flagged, context) | UNKNOWN on the claimed arm, E-UNRESOLVED; aneugenicity reported as a risk | G4 | UNRESOLVED | see Section 5, the rule's limit is stated rather than stretched |
| gefitinib | Rx | SIRT2 no (EGFR 0.190 no, context) | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | `gefitinib AND SIRT2` returned 0 |
| resveratrol | no authorised drug product (supplement) | SIRT1 no | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | `resveratrol AND BubR1` returned 1, an analog paper, PMID 19293634 |
| spermidine | no authorised drug product (supplement) | EP300 flagged 0.284 | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | PMID 25526088 inhibits EP300, but the anchor names CBP and no source measures net BubR1 |
| idebenone | no authorised US drug product; EU limb not run | no named target assigned | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | no primary source links it to BubR1 or the checkpoint |
| isotretinoin | Rx | no named target assigned | UNKNOWN, E-UNRESOLVED | G4 | UNRESOLVED | `isotretinoin AND (BUB1B OR BubR1)` returned 0 |

**Counts: 3 REMOVED, 1 KEPT AS CANDIDATE, 16 UNRESOLVED.**

---

## 4. The removals, with the deciding quote

### fisetin, REMOVED on mechanism direction

PMID 19395653 (Salmela AL et al., Carcinogenesis 2009), VERIFIED:

> in unperturbed human cancer cells fisetin caused premature initiation of chromosome
> segregation and exit from mitosis without normal cytokinesis ... Aurora B, Bub1, BubR1 and
> Cenp-F rapidly lost their kinetochore/centromere localization ... our data propose that
> fisetin perturbs spindle checkpoint signaling

This is AGAINST on both halves of the R2-B direction definition at once: it displaces BubR1
from the kinetochore and it overrides the checkpoint. The stress-dependence clause does not
rescue it, because the effect is reported in unperturbed cells, not only under applied stress.
Every arm is AGAINST, so the candidate is REMOVED under Section 5 of the exposure rule.
Falsifier: a primary source measuring net BubR1 protein or checkpoint function after fisetin at
an achievable free exposure and finding either preserved.

### epigallocatechin gallate, REMOVED on mechanism direction

PMID 19147572 (Choi KC et al., Cancer Res 2009), VERIFIED:

> we identified epigallocatechin-3-gallate (EGCG) as a novel HATi with global specificity for
> the majority of HAT enzymes ... At a dose of 100 micromol/L, EGCG abrogates p300-induced p65
> acetylation in vitro and in vivo

Global HAT inhibition does not spare PCAF, and PCAF acetylation of BubR1 at K250 is what holds
BubR1 back from ubiquitin-dependent degradation (PMID 19407811, quoted in Section 1). No source
measures net BubR1 protein after EGCG and finds it raised, so the transcriptional override
clause applies in its general form: an arm shown to lower BubR1 by any route is AGAINST unless
a source measures the net effect and finds it positive. C_demo is 100 uM, which is far above
any reported human free concentration, so the arm also fails on exposure. Falsifier: a primary
source measuring net BubR1 protein after EGCG at an achievable free exposure and finding it
raised, or a source showing EGCG spares KAT2B.

### suramin, REMOVED on mechanism direction

PMID 17355872 (Schuetz A et al., Structure 2007), VERIFIED:

> We identified suramin as a compound that binds to human SIRT5 and showed that it inhibits
> SIRT5 NAD(+)-dependent deacetylase activity with an IC(50) value of 22 microM ... suramin
> binds into the NAD(+), the product, and the substrate-binding site

Sirtuin inhibition is the AGAINST direction against the anchor, which makes sirtuin
deacetylation of K668 the thing that maintains BubR1. **Marked UNVERIFIED:** the demonstration
is on SIRT5, and the step from SIRT5 to SIRT2 is an isoform extrapolation, supported by the
binding site being the shared NAD+ and substrate pocket rather than an isoform-specific surface,
but not itself measured. Falsifier, and it is a real one: a primary source showing suramin
spares SIRT2 at achievable free exposure would return this drug to UNRESOLVED.

---

## 5. The one KEPT AS CANDIDATE, and why it is fragile

**curcumin.** Direction is TOWARD, and it is the only entrant in this batch whose
acetyltransferase selectivity points the right way on both limbs at once.

PMID 15383533 (Balasubramanyam K et al., J Biol Chem 2004), VERIFIED:

> curcumin (diferuloylmethane), a major curcumanoid in the spice turmeric, is a specific
> inhibitor of the p300/CREB-binding protein (CBP) HAT activity but not of p300/CBP-associated
> factor, in vitro and in vivo

CBP is the exact enzyme the anchor names as the one that acetylates BubR1 K668 and drives its
loss, and p300/CBP-associated factor is PCAF, the exact enzyme whose K250 acetylation protects
BubR1. Curcumin inhibits the first and spares the second. That is the asymmetry that separates
it from epigallocatechin gallate, which inhibits both and is removed above. This distinction
came from reading each drug against source rather than scoring the class, which the briefing
note asked for and which would have given the wrong answer for one of these two drugs either way.

Three things keep this a weak candidate and they are stated rather than buried:

1. **Exposure is probably fatal to it, and is recorded as unresolved only because C_demo has no
   number at source.** PMID 18559556 (Vareed SK et al., Cancer Epidemiol Biomarkers Prev 2008),
   VERIFIED, at 10 g and 12 g oral doses with a 50 ng/mL limit of detection:

   > only one subject had detectable free curcumin at any of the 14 time points assayed, but
   > curcumin glucuronides and sulfates were detected in all subjects

   So achieved free curcumin is below about 0.14 uM in five of six subjects at 10 to 12 g daily.
   PMID 15383533 states the p300/CBP HAT inhibition but its abstract carries no IC50, and no
   abstract-level primary source found this run supplies one, so R is not computable and the arm
   is E-UNRESOLVED, which under Section 5.3 never removes. **Stated plainly: if C_demo is taken
   at the ~25 uM order used in the primary HAT literature, which is UNVERIFIED for this
   endpoint, then R < 0.006 and the arm becomes E-FAIL and curcumin is REMOVED.** Retrieving the
   p300/CBP HAT IC50 from the full text of PMID 15383533 is the single cheapest action that
   would resolve this row, and it should be done before curcumin is reported as a candidate.
2. **A counter-directional arm, reported as a risk and not dropped.** PMID 17927689 reports
   curcumin as an HDAC inhibitor with decreases in HDAC1 and HDAC3. The class I HDAC route is
   excluded on direction by the frozen class-level result RESULT-R2C-HDAC. I did **not** apply
   the Section 5.6 class disposal, because that disposal is for members of the class I HDAC
   inhibitor drug class and curcumin is a polypharmacology natural product whose HDAC activity
   is incidental and contested, not a class member. That judgement is recorded here so it can be
   overturned. If the team reads the class disposal as covering it, curcumin is REMOVED instead,
   and the outcome of this batch becomes 4 REMOVED and 0 KEPT.
3. **C2 tie-break input, not a removal.** EP300 is the one flagged named target in this batch,
   fraction 0.284, blood lineage median -0.761. Under Section 5.2 this does not remove curcumin.
   It is the safety tie-break input and it will push curcumin down, not out.

C5 grade is **G4**: there is no measurement of BubR1 protein after curcumin anywhere in what was
retrieved. The evidence is mechanism and pathway only, two inferential steps from the endpoint.
Under RANKING-RULE-T2 a supplement sits above a prescription drug only on a strictly higher
grade, so a G4 supplement enters the ranked list at the bottom and cannot displace anything.

This row also discharges the pre-registered falsifier "Every new drug is REMOVED", whose
falsifier was "any single drug passing C1, C3 and C5 with a reading on each". One drug did.

---

## 6. A negative finding about the screening instrument itself

**Twelve of the twenty rows in this batch rest on a claimed target that no primary source
supports.** This is reported because it bears on how the candidate universe should be read, and
because it is the kind of result that would otherwise be silently absorbed.

| Rows | Claimed target | What the search returned |
|---|---|---|
| alendronate, ibandronic acid, risedronic acid, zoledronic acid | SIRT1 | `("alendronate" OR "zoledronic") AND SIRT1` returned 5, none a pharmacological demonstration; all were bone or osteonecrosis papers about other compounds. Real target is FDPS |
| alprazolam, estazolam, midazolam, triazolam | CREBBP | `midazolam AND CREBBP` returned 1, an unrelated propofol and bumetanide paper. Real target is the GABA-A receptor |
| methylphenidate | CREBBP, EP300 | `methylphenidate AND (CREBBP OR EP300)` returned 0 |
| papaverine | CREBBP | no primary source; real target is PDE10A |
| colchicine | CREBBP | no primary source; real target is tubulin |
| gefitinib | SIRT2 | `gefitinib AND SIRT2` returned 0. Real target is EGFR |

All searches were PubMed esearch this run, VERIFIED. The pattern is consistent with arm A
returning chemical and gene association records, including expression-change and co-occurrence
annotations, under a field a reader naturally reads as "drug target". The consequence for the
report is narrow and should be stated in exactly these terms: for these twelve rows the frozen
criteria return UNRESOLVED rather than REMOVED, because C_demo cannot be established for a
mechanism that was never demonstrated, and E-UNRESOLVED never removes. **UNRESOLVED here means
the claimed mechanism has no source, not that the drug was examined and cleared.**

---

## 7. Colchicine, where the frozen rule does not reach

Recorded separately because collapsing it into the table would misreport it.

Colchicine's claimed arm in this screen is CREBBP, which has no primary source, so that arm is
E-UNRESOLVED like the other eleven. Its actual pharmacology is tubulin directed, and TUBB is the
most strongly flagged gene examined in this batch (fraction 0.964, blood lineage median -1.881).
Tubulin-directed agents induce whole-chromosome loss, which is the disease endpoint itself.

But the frozen R2-B definition of AGAINST is "to LOWER BUBR1 protein, or to SILENCE, WEAKEN or
OVERRIDE the mitotic checkpoint", and colchicine does the opposite of the second: it engages the
checkpoint rather than silencing it. Scoring it AGAINST would require reading the definition more
loosely than it was frozen, and doing that after seeing the drug is exactly what pre-registration
is for preventing. So the outcome stays UNRESOLVED and the aneugenicity is recorded here as a
reported risk.

This is a gap in the frozen rule, not a property of colchicine, and it is flagged for the
register: the direction definition has no limb for an agent that activates the checkpoint while
still causing missegregation. Any future amendment should be made as an amendment, on the record,
and not inside this evaluation.

---

## 8. What this batch did not do

- The DailyMed and EMA limbs of C1 were not run. Three rows are affected and are flagged on their
  rows: idebenone holds an EU authorisation that a US-only lexicon does not see, and suramin and
  papaverine are not US-authorised but are not dietary supplements either.
- C4 was not separately computed per drug. It removes nothing under Section 5.4, and for this
  batch no entrant reached a plasma-versus-IC50 comparison that C4 would have changed.
- No full texts were retrieved. Every quote above is from a PubMed abstract read at source this
  run. The one place this bites is the curcumin C_demo, and that is called out in Section 5.
- Our own existing NAD route candidates were not re-decided, per the brief. Nothing here touches
  them.

## 9. Files

- This file.
- `b2_depmap.py` and `b2_c2_depmap.tsv`, in the box work directory
  `~/Documents/HACKATON/_private/agent_out/nonchoices/eval_B2/`. The script is new and copies the
  method of `p5_depmap_safety.py` without modifying it.
