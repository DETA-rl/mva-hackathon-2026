# RESULT-B4b: evaluation of Batch 4 items 50 to 98 (49 molecules). Outcome: zero kept

Governed by `PRE_REG_NONCHOICES.md`, sha256
`ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4`, verified against the file
before this evaluation started, and by `BATCHES.md`, sha256
`61c1fca70c2f8b046677397352e0d53aa81d57181b75360910d64a107f64da30`, verified the same way. The
C3 rule is `PRE_REG_R2B_EXPOSURE.md`, sha256
`338b0d6078d91f9fee7a4c0aaca516ca48a1bf1c3a39c9ac5f025a10ba1a1534`, also verified. No criterion
was altered, no threshold is new, and no existing file was edited.

Scope: the 49 rows of Batch 4 at positions 50 to 98 in the order printed in `BATCHES.md`, from
etoposide to osimertinib. Items 1 to 49 and 99 to the end are other agents' work and nothing
here disposes of them.

Non-clinical clause, repeated: this is a hypothesis-screening document about published
mechanism, label and database facts. It is not clinical advice, it proposes no dose or regimen
for any person, and nothing in it may be read as a recommendation to administer anything. No
patient-derived data was used. Every query that left this machine carried a drug name, a gene
symbol, a mechanism term or a PMID, and nothing else.

VERIFIED means retrieved from the named API this run or computed here from the public DepMap
files on the box. UNVERIFIED means anything else and is labelled inline.

---

## 1. Headline

| Outcome | Count |
|---|---|
| REMOVED, on C3 mechanism direction | 10 |
| UNRESOLVED | 39 |
| KEPT AS CANDIDATE | **0** |

No row in this slice was removed on C1, because no row's regulatory class could be positively
established as excluded: pre-registration Section 2.1 fixes that a molecule whose approval
cannot be confirmed at C1 is resolved UNRESOLVED, never dropped. No row was removed on C2: a
DepMap flag removes nothing here, by Section 5.2 decided before the universe was known.

The 39 UNRESOLVED rows split into three kinds, and the write-up must not merge them:

- **22 rows have no mechanism arm at all.** No source proposes any route by which the molecule
  raises BUBR1 or preserves the checkpoint. They are in the universe because the mechanism
  neutral literature queries L1 to L4 returned them as names co-occurring with BUB1B, under the
  extraction deviation that `BATCHES.md` Section 2.3 disclosed in advance. C3 has no C_demo to
  compute and C5 returns no grade. These are not candidates that we rejected. They are names
  the instrument returned, and the honest disposal is UNRESOLVED.
- **16 rows carry a database target claim that C3 cannot score**, because the claim is an
  untyped association or a curation record rather than a pharmacology measurement. Section 2.4
  sets out the check that established this.
- **1 row carries a real mechanism-class arm that could not be scored**: gentamicin, on
  aminoglycoside readthrough. Section 5.1.

Gentamicin, metformin and hesperidin are each set out in full in Section 5: the first because
its arm matches the variant class, the second because it was an expectation recorded in advance,
the third because its claim carries the highest interaction score in the slice.

## 2. What the deciding evidence was, per mechanism class

Every direction verdict below rests on primary records retrieved from PubMed this run and is
scored under the frozen R2-B definitions of its Section 4, where AGAINST means that at clinical
exposure the net predicted effect per a primary source is to lower BUBR1 protein, or to silence,
weaken or override the mitotic checkpoint.

**2.1 Class-level ground for cytotoxic DNA-damaging agents, BUBR1-specific [VERIFIED].**
PMID 16449973 (BubR1 is involved in regulation of DNA damage responses), verbatim: "Following
treatment with doxorubicin, BubR1(+/-) murine fibroblast cells (MEF) were defective in
undergoing G(2)/M arrest" and "whereas in the presence of DNA damage BubR1(+/+) MEF cells
remained arrested in mitosis, BubR1(+/-) MEFs rapidly exited from mitosis and divided". The
paper's claim is about the DNA damage response in BubR1 insufficiency, which is the setting this
project is about, so the ground is class-level rather than drug-level: an agent whose approved
action is to damage DNA is, in BubR1 insufficiency, met by a cell that exits mitosis and divides
instead of arresting. Direction AGAINST for the endpoint of preserving checkpoint function.

**2.2 Per-drug and per-subclass chromosome-level confirmation [VERIFIED where named].**
- Topoisomerase II poisons as an MN-inducing class: PMID 24297155, verbatim, lists mechanisms
  "including aneugens and clastogens (DNA cross-linkers, topoisomerase II inhibitors, minor
  groove binders)".
- Etoposide: PMID 8050416, verbatim: "An unusually potent response was observed for etoposide in
  the mouse bone marrow micronucleus assay (63.1 +/- 18 MPE/1,000 PE 24 hours after an oral dose
  of 1 mg/kg)". Marrow, at a dose far below clinical oral dosing.
- Mitomycin: PMID 40682297, verbatim, names "DNA-reactive clastogens (mitomycin C and methyl
  methanesulfonate)" as reference clastogens of the micronucleus assay.
- Methotrexate: PMID 9485540, verbatim: "A significant increase in percent micronucleated
  binucleated cells (MNBN) and percent aberrant cells (Abs) was observed".
- Melphalan: PMID 35961530, verbatim: "A single cycle of exposure at high dose (1.5 mg/kg)
  produced significant effect on micronuclei formation".
- Griseofulvin: PMID 3277037, verbatim: "A positive response has been obtained in the assays on
  numerical chromosome changes in all the systems analyzed", with aneuploidy among the listed
  endpoints; PMID 36752776, verbatim: griseofulvin "resulted in a significant increase in the
  number of NSCLC cells with multipolar spindles" and "Both GF and radiation treatment also
  induced the generation of micronuclei (MN) in vitro and in vivo". PMID 42330849 adds that
  norlichexanthone, a shunt product of griseofulvin, "disrupts spindle assembly checkpoint and
  nucleocytoplasmic transport by targeting TPR". Griseofulvin is scored on its own aneugen
  record, not on the shunt product.
- Gemcitabine, idarubicin, ifosfamide, irinotecan and mitoxantrone carry the Section 2.1
  class-level ground; no chromosome-level record for the individual molecule was retrieved this
  run, and that is marked per row.

**2.3 The direction of the literature that attached these drugs to BUB1B is the inverse of this
project's endpoint [VERIFIED].** PMID 34545188: "Increased BUB1B/BUBR1 expression contributes to
aberrant DNA repair activity leading to resistance to DNA-damaging agents". PMID 39043653:
"BUB1b impairs chemotherapy sensitivity via resistance to ferroptosis in lung adenocarcinoma".
PMID 39115587: "Doxorubicin downregulates cell cycle regulatory hub genes in breast cancer
cells", with BUB1B among the named hub genes. In these sources the therapeutic goal is to LOWER
BubR1 in order to sensitise a tumour. That is the opposite of raising residual BUBR1, and it is
why so many cytotoxics co-occur with BUB1B in the frozen queries.

**2.4 The database target claims in this slice are untyped associations [VERIFIED].** DGIdb was
re-queried for 16 of the rows whose claimed target is MTOR or AURKB. Of the returns, 14 carry an
empty `interactionTypes` list, that is no mechanism and no directionality, with interaction
scores from 0.003 to 0.236, sourced to DTC, PRISM, Drug Repurposing Hub or TTD. Only two carry a
type: metformin ("inhibitor", INHIBITORY, sourced to MyCancerGenomeClinicalTrial) and
infigratinib ("inhibitor", INHIBITORY, sourced to MyCancerGenome), both curation records rather
than a pharmacology measurement. An untyped association gives C3 no mechanism to locate a C_demo
for, so those arms are E-UNRESOLVED and not scorable either way. This is a finding about the
instrument, and it is the reason the A1 rows of this slice do not resolve.

## 3. C2, DepMap 24Q4 dependency for the claimed targets [VERIFIED, computed here]

Method identical to the T2-P5 script: 1,178 lines, 348 blood-lineage lines in `Model.csv`,
fraction of lines with Chronos gene effect below -0.5, flag at or above 0.25.

| gene | frac Chronos < -0.5 | flag | blood-lineage median | n lines |
|---|---|---|---|---|
| MTOR | 0.986 | YES | -1.130 | 1178 |
| AURKB | 1.000 | YES | -2.420 | 1178 |
| PLK4 | 0.982 | YES | -1.281 | 1178 |
| KIF18A | 0.885 | YES | -0.839 | 1178 |

Reproduction check: MTOR 0.986, PLK4 0.982 and KIF18A 0.885 reproduce the T2-P4 values exactly.
AURKB at 1.000 is new in this slice and is the most extreme fraction seen anywhere in this
project so far.

Carried caveat, unchanged and not used to re-flag or to remove anything: a CRISPR knockout is a
loss-of-function proxy in cancer lines, never normal marrow. No flag is a safety verdict and no
absent flag is a safety clearance. The T2-P4 removals of the mTOR, PLK4 and KIF18A routes stand
on the register for the drugs they named and are not extended here to new drugs, because
extending them would be a new rule.

## 4. C4, reported and removing nothing

C4 is the plasma-concentration-against-enzyme-IC50 instrument, declared NON-DISCRIMINATING by
RESULT-R2D-R2E, and pre-registration Section 5.4 fixed before the universe was known that it is
reported and removes nothing. For this slice it is not computable for any row: no row has an
enzyme IC50 that the project's C4 instrument acts on, because the untyped database associations
of Section 2.4 supply no mechanism and the literature co-occurrence rows supply none either.
Recorded as not computable, and it changes no outcome.

## 5. The three rows with a claimed arm, in full

**5.1 Gentamicin. UNRESOLVED, and the most testable gap in this slice.**
The child's BUB1B pair includes a truncating allele, so the one mechanistically on-point idea
reachable in this batch is aminoglycoside-induced readthrough of a premature termination codon,
which would raise full-length protein from that allele. Readings:

- C1 [VERIFIED]: prescription. US authorised products are injection, ophthalmic and topical
  (openFDA drugsfda, 11 applications, all Prescription); no oral systemic product. Paediatric
  limb: no `pediatric_use` section was returned in the two intravenous labels retrieved, so the
  statement is recorded as not retrieved. Reported, never exclusionary.
- C3 exposure [VERIFIED from the label]: "the peak concentration (at 30 to 60 minutes after IM
  injection) is expected to be in the range of 4 to 6 mcg/mL", and "the degree of gentamicin
  binding is low; depending upon the methods used for testing, this may be between 0 and 30%",
  giving a free peak of about 2.8 to 6 mcg/mL [computed here from those two label figures].
- C3 direction: **NOT ESTABLISHED.** The decisive datum is missing in a specific and checkable
  way: a PubMed search for `(BUB1B[tiab] OR BubR1[tiab]) AND (readthrough[tiab] OR
  read-through[tiab] OR nonsense suppression[tiab])` returns **count 0** [VERIFIED]. No source
  applies readthrough to a BUB1B premature termination codon, so no primary source establishes
  the sign of the effect on BUBR1 protein at any exposure. C_demo is also not retrievable: the
  readthrough records reached at abstract level (PMID 40342992, 41210582, 42504002) report
  readthrough activity and clinical use in epidermolysis bullosa without a concentration in
  units commensurable with the label figure. R is therefore not computed, and under R2-B
  Section 5 the arm is **E-UNRESOLVED**.
- C5: no grade. No source tests any readthrough agent on BUBR1 protein or on a mitotic endpoint,
  so not even G4 mechanism evidence for this gene exists.
- Outcome: **UNRESOLVED.** It is not removed, and absence of exposure or direction data is not
  read as safety. The honest statement for the report is that the readthrough route is the one
  idea in this slice that matches the variant class, and the published record contains no test
  of it on this gene.
- Note for reconciliation: amikacin sits at item 2 of this batch, in another agent's slice, and
  is the same mechanism class. The count-0 finding above applies to the class, not to gentamicin
  alone.

**5.2 Metformin. UNRESOLVED at clinical exposure, with an AGAINST arm reported as a risk at
supra-therapeutic concentration.**
- C1 [VERIFIED]: prescription, 70 drugsfda applications, oral.
- Claimed arm: MTOR inhibitor (ChEMBL CHEMBL1703; DGIdb typed inhibitor from
  MyCancerGenomeClinicalTrial). C2 on MTOR: flagged, 0.986.
- C3 direction [VERIFIED at abstract]: the frozen-style query `metformin AND (BubR1 OR BUB1B OR
  spindle assembly checkpoint)` returns 2 records, and neither proposes raising BUBR1. PMID
  35568294, verbatim: "Metformin induced a dose-dependent increase of genotoxic stress
  (including micronucleus, nucleoplasmic bridge and nuclear bud)"; "Metformin deregulated the
  expression of BUBR1 and MAD2, two core genes of spindle assembly checkpoint (SAC) that
  surveillances chromosome segregation"; "metformin significantly increased genotoxicity in
  non-cancer cells (NCM460 and HUVECs)". The concentrations there are 1 to 16 mM. PMID 33161761
  reports, in human peripheral lymphocytes at 12.5 to 125 mcg/mL, that "MET significantly
  increased the frequency of CAs at 48 h exposure" and concludes "MET had a mild genotoxic
  effect, especially at a long treatment period and higher concentrations".
- Both figures are above ordinary therapeutic plasma concentrations, so under R2-B the direction
  AGAINST is NOT established **at clinical exposure**, and the arm is E-UNRESOLVED. Per R2-B
  Section 5 the AGAINST reading is reported as a risk attached to the molecule and is not
  silently dropped.
- C5: no grade. No source proposes metformin raising BUBR1.
- Outcome: **UNRESOLVED.** Stated plainly for the report: the most-expected repurposing name in
  this universe has no published BUBR1-raising rationale, and the only primary records that
  touch BUBR1 at all point away from the endpoint at high concentration.

**5.3 Hesperidin. UNRESOLVED.**
- C1 [VERIFIED]: no authorised drug product. No drugsfda record on generic, substance or brand
  fields; one openFDA label record exists for a marketed product ("Bruselix Bruising") with no
  application number. Under the frozen C1 reading the class for the rule is dietary supplement,
  which is in scope and is not a removal ground.
- Claimed arm: AURKB, from the Drug Repurposing Hub, untyped, interaction score 0.236
  [VERIFIED at DGIdb this run]. C2 on AURKB: flagged, 1.000.
- C3: a PubMed query pairing hesperidin with aurora, BubR1, spindle or mitotic terms returned 11
  records, none of which reports hesperidin acting on Aurora B or on BubR1; the returns are
  bioinformatics and unrelated pharmacology. No direction, no C_demo, E-UNRESOLVED.
- C5: no grade. Outcome: **UNRESOLVED.**

## 6. The per-row table

C1 is the openFDA reading this run. "Claimed arm" is the claim `BATCHES.md` carries, which is
the database's or the query's, not ours. C3 is the deciding column. C4 is not computable for any
row, per Section 4, and removes nothing. C5 is the RANKING-RULE-T2 grade, where "none" means the
criterion returned no grade because no source supplies mechanism evidence for this gene.

| # | Molecule | C1 class [VERIFIED] | Claimed arm | C3 direction and basis | C5 | Outcome |
|---|---|---|---|---|---|---|
| 50 | etoposide | Rx, oral and injection | none (co-occurrence) | AGAINST. Topo II poison; PMID 8050416 marrow micronuclei at 1 mg/kg oral; class ground PMID 16449973, 24297155 | none | **REMOVED on C3** |
| 51 | fasudil | approval not confirmed; no drugsfda record on any field with controls passing; EMA route not run [UNVERIFIED limb] | AURKB, untyped, DTC, score 0.017 | E-UNRESOLVED. No source on BubR1 or the checkpoint; PMID 33278350 reports ROCK1/2 targeting causing mitotic catastrophe, which is not a BUBR1 reading | none | UNRESOLVED (C1 and C3) |
| 52 | fenretinide | approval not confirmed; no drugsfda record | MTOR, untyped, DTC, score 0.006 | E-UNRESOLVED, untyped association | none | UNRESOLVED (C1 and C3) |
| 53 | fentanyl | Rx | none (co-occurrence, PMID 40273626, a neonatal anaesthesia and analgesia animal study) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 54 | ferric | Rx and OTC iron products exist | none (co-occurrence, PMID 40595080, plant phytochemical screen) | E-UNRESOLVED, no arm | none | UNRESOLVED (name artefact, see Section 7.2) |
| 55 | ferrous | Rx and OTC iron products exist | none (co-occurrence, PMID 39949372, lncRNA bioinformatics) | E-UNRESOLVED, no arm | none | UNRESOLVED (name artefact) |
| 56 | fluvastatin | Rx | none (co-occurrence, PMID 41053901, aneurysm bioinformatics) | E-UNRESOLVED, no arm. Related observation: PMID 42146413 proposes statin-pathway inhibition because "Aneuploidy sensitizes cells to SREBP-pathway inhibition", which is the inverse use of the phenotype | none | UNRESOLVED (no mechanism arm) |
| 57 | gemcitabine | Rx, injection | none (co-occurrence, nab-paclitaxel resistance CRISPR screens) | AGAINST on the class ground PMID 16449973; no gemcitabine-specific chromosome-level record retrieved [per-drug limb UNVERIFIED] | none | **REMOVED on C3** |
| 58 | gentamicin | Rx, injection, ophthalmic, topical | aminoglycoside readthrough of a premature termination codon | E-UNRESOLVED. Free peak about 2.8 to 6 mcg/mL; BUB1B readthrough query count 0; C_demo not retrievable. Section 5.1 | none | UNRESOLVED |
| 59 | glasdegib | Rx, NDA210656 | MTOR, untyped, TTD, score 0.048 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 60 | glucagon | Rx | none (co-occurrence, PMID 39949372) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 61 | griseofulvin | Rx, oral | none (co-occurrence) | AGAINST. Aneugen: PMID 3277037 numerical chromosome changes positive in all systems; PMID 36752776 multipolar spindles and micronuclei in vitro and in vivo | none | **REMOVED on C3** |
| 62 | haloperidol decanoate | Rx | MTOR, untyped, DTC, score 0.003 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 63 | heather | brand HEATHER, ANDA090454, Rx | none (co-occurrence, PMID 41381790, osteoarthritis bioinformatics) | E-UNRESOLVED, no arm | none | UNRESOLVED (name artefact) |
| 64 | trastuzumab (listed as herceptin) | Rx biologic, BLA103792 | none (co-occurrence, PMID 34035233) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 65 | hesperidin | no authorised drug product; class for the rule is dietary supplement | AURKB, untyped, Drug Repurposing Hub, score 0.236 | E-UNRESOLVED. Section 5.3 | none | UNRESOLVED |
| 66 | hydroxychloroquine | Rx | none; entered as "also considered" | E-UNRESOLVED, no arm reaching BUBR1 | none | UNRESOLVED (no mechanism arm) |
| 67 | idarubicin | Rx, intravenous | MTOR, untyped, DTC, score 0.006 | AGAINST. Anthracycline topo II poison; class ground PMID 16449973 and 24297155; PMID 39115587 reports doxorubicin downregulating BUB1B among hub genes [anthracycline class limb] | none | **REMOVED on C3** |
| 68 | ifenprodil | approval not confirmed; no drugsfda record | MTOR, untyped, DTC, score 0.059 | E-UNRESOLVED, untyped association | none | UNRESOLVED (C1 and C3) |
| 69 | ifosfamide | Rx, injection | none (co-occurrence) | AGAINST. Oxazaphosphorine alkylator; class ground PMID 16449973; subclass clastogenicity PMID 35518717 (cyclophosphamide) [per-drug limb UNVERIFIED] | none | **REMOVED on C3** |
| 70 | imatinib | Rx, oral | none (co-occurrence). PMID 20442314 is about Bcr-Abl impairing the mitotic checkpoint, not about imatinib raising BubR1 | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 71 | infigratinib | approval confirmed historically, NDA214622; all US products Discontinued [VERIFIED] | MTOR inhibitor, typed, MyCancerGenome curation | E-UNRESOLVED, curation record only, no C_demo | none | UNRESOLVED |
| 72 | irinotecan | Rx, injection | none; entered as "also considered" | AGAINST. Topo I poison; class ground PMID 16449973; no irinotecan-specific chromosome-level record retrieved [per-drug limb UNVERIFIED] | none | **REMOVED on C3** |
| 73 | isoniazid | Rx | none (co-occurrence, PMID 33244299) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 74 | isoproterenol | Rx, injection | MTOR, untyped, DTC, score 0.010 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 75 | lapatinib | Rx, oral | AURKB, untyped, DTC, score 0.013 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 76 | lenvatinib | Rx, NDA206947 [VERIFIED on the brand field after the generic field missed] | none (co-occurrence, hub-gene bioinformatics) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 77 | letrozole | Rx, oral | none (co-occurrence) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 78 | levetiracetam | Rx, 60 applications | none; entered as "also considered" | E-UNRESOLVED, no arm reaching BUBR1 | none | UNRESOLVED (no mechanism arm) |
| 79 | levocetirizine | Rx and OTC | MTOR, untyped, PRISM viability screen, score 0.059 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 80 | levonorgestrel | Rx and OTC | none (co-occurrence) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 81 | norepinephrine (listed as levophed) | Rx, injection | none (co-occurrence, PMID 40209578, a docking and repurposing paper) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 82 | loperamide | OTC and Rx | MTOR, untyped, DTC, score 0.015 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 83 | lovastatin | Rx, oral | none (co-occurrence). Same inverse-rationale observation as row 56 | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 84 | maprotiline | approval confirmed historically, ANDA072129 to 072131; all US products Discontinued [VERIFIED] | MTOR, untyped, DTC, score 0.022 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 85 | melphalan | Rx, injection | none (co-occurrence) | AGAINST. Alkylator; PMID 35961530 micronuclei after 1.5 mg/kg; class ground PMID 16449973 | none | **REMOVED on C3** |
| 86 | mesalamine | Rx | none; entered as "also considered" | E-UNRESOLVED, no arm reaching BUBR1 | none | UNRESOLVED (no mechanism arm) |
| 87 | metformin | Rx, oral, 70 applications | MTOR inhibitor, typed, curation record | E-UNRESOLVED at clinical exposure, with an AGAINST arm at 1 to 16 mM and at 12.5 to 125 mcg/mL reported as a risk. Section 5.2 | none | UNRESOLVED |
| 88 | methotrexate | Rx, oral, injection, subcutaneous | none (co-occurrence) | AGAINST. PMID 9485540 significant increase in micronucleated binucleated cells and aberrant cells; class ground PMID 16449973 | none | **REMOVED on C3** |
| 89 | mifepristone | Rx, oral | MTOR, per the DGIdb row in BATCHES; not individually re-queried in the 16-drug spot check [UNVERIFIED claim] | E-UNRESOLVED, no scorable mechanism | none | UNRESOLVED |
| 90 | minocycline | Rx, oral | none (co-occurrence) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 91 | mitomycin | Rx, injection and topical | none (co-occurrence) | AGAINST. PMID 40682297 names mitomycin C a reference DNA-reactive clastogen; class ground PMID 16449973 | none | **REMOVED on C3** |
| 92 | mitoxantrone | Rx, injection | none (co-occurrence) | AGAINST. Topo II class, PMID 24297155; class ground PMID 16449973; no mitoxantrone-specific record retrieved [per-drug limb UNVERIFIED] | none | **REMOVED on C3** |
| 93 | nicardipine | Rx | MTOR, untyped, DTC, score 0.022 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 94 | niclosamide | approval confirmed historically, NDA018669; Discontinued [VERIFIED] | MTOR, untyped, DTC, score 0.008 | E-UNRESOLVED, untyped association | none | UNRESOLVED |
| 95 | nicotine | OTC, 606 OTC label records, 48 applications | none (co-occurrence) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |
| 96 | nikita | brand NIKITA, NDA209875, Discontinued [VERIFIED] | none (co-occurrence, PMID 32154490, a single case report) | E-UNRESOLVED, no arm | none | UNRESOLVED (name artefact) |
| 97 | olaparib | Rx, NDA208558 | none (co-occurrence, PMID 34545188) | E-UNRESOLVED, no arm raising BUBR1. Reported risk: PMID 16449973 finds BubR1 interacts with PARP-1 and that BubR1(+/-) cells handle PARP-1 poorly after damage, and PMID 34545188 proposes lowering BUBR1 to sensitise | none | UNRESOLVED (no mechanism arm) |
| 98 | osimertinib | Rx, NDA208065 [VERIFIED on the brand field after the generic field missed] | none (co-occurrence) | E-UNRESOLVED, no arm | none | UNRESOLVED (no mechanism arm) |

## 7. Findings about the procedure, reported because they are negative

**7.1 The openFDA generic-name field misses approved drugs, and the miss was caught by
controls.** Eleven names returned HTTP 404 on `openfda.generic_name`. Re-querying on
`products.brand_name` with lenvatinib and osimertinib as positive controls returned NDA206947
and NDA208065, so the 404s were a query-syntax property, not evidence of non-approval. Had the
first pass been trusted, this slice would have produced false C1 removals for at least
lenvatinib, osimertinib, infigratinib, maprotiline and niclosamide. Recorded because the next
batch's agent needs the same control.

**7.2 Four rows are lexicon artefacts of the disclosed extraction deviation.** ferric, ferrous,
heather and nikita are not drug proposals. They are strings that matched the Drugs@FDA name
lexicon inside abstracts about plant phytochemicals, lncRNA bioinformatics, osteoarthritis
palmitoylation and a single case report. Two of them do resolve to real products on openFDA
(HEATHER, ANDA090454; NIKITA, NDA209875), which is why they cannot simply be deleted as
non-molecules. They are the same kind of row as the eight names excluded at universe assembly,
and the lead may prefer to carry them as artefacts rather than as evaluated rows. Nothing here
removes them, and the choice is the lead's.

**7.3 The slice is dominated by sensitivity-biomarker papers, exactly as BATCHES Section 2.2
predicted.** Titles were retrieved for the 42 PMIDs behind the co-occurrence rows. The
overwhelming majority are cancer hub-gene or prognostic-biomarker studies in which BUB1B appears
as an upregulated hub gene and the drug is a cohort treatment or a connectivity-style
prediction. None proposes raising BUBR1. The prediction made before the universe was known is
confirmed, and this is the single largest reason the slice yields no candidate.

## 8. Falsifier checks, as pre-registered

| Pre-registered falsifier | Status in this slice |
|---|---|
| "Every new drug is REMOVED" is falsified by any single drug passing C1, C3 and C5 with a reading on each | Not reached either way. No drug in this slice passes, and no drug is removed on every criterion either: 39 of 49 are UNRESOLVED. The premise that the carried list was complete is therefore not supported by this slice and not refuted by it |
| A class disposal is sound unless a primary source shows a member acting oppositely at an achievable exposure | Checked for the cytotoxic class. No source was found showing any of the ten removed molecules raising BUBR1 protein or strengthening the checkpoint at any exposure. The class disposal stands, and it rests on class-level evidence as Section 5.6 requires |
| The procedure is reproducible | C2 reproduces T2-P4 to three decimals on three genes run independently here. The C1 arm is reproducible only with the brand-field fallback of Section 7.1, which the pre-registration did not specify |

## 9. Limits, stated plainly

- Ten removals rest on mechanism direction, not on any safety claim about any molecule, and none
  of them may be reported as a safety finding.
- The class-level ground of Section 2.1 is a mouse-genetics paper on BubR1 insufficiency plus
  human genotoxicity assays in cancer or lymphoblast lines. None of it is in BUB1B-mutant
  patient cells and none is in a child. It establishes direction for the class, not a
  quantitative prediction.
- Five of the ten removals (gemcitabine, idarubicin, ifosfamide, irinotecan, mitoxantrone) carry
  the class limb VERIFIED and the per-drug chromosome-level limb UNVERIFIED, as marked per row.
- Everything in Section 6 was read at abstract level or at the openFDA endpoint named. No
  paywalled full text was opened, and no number here is carried from a review.
- C3 for the untyped-association rows could change if a pharmacology source were found for the
  claimed target. The honest state is unresolved, not negative.

## 10. Files

Mac, `scratchpad/agent_out/nonchoices/`: `RESULT_B4b.md` (this file).
Box, `~/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/`: this file, plus
`c2_depmap_b4b.py` and `c2_depmap_b4b.tsv` (C2), `c1_openfda.py` and `c1_openfda.json`,
`c1_recheck.py`, `c1_recheck2.py` and their JSON (the C1 control of Section 7.1),
`c1_paed.py`, `c1_paed_gentamicin.json`, `lit_titles.py` and `lit_titles.json` (the 42
co-occurrence sources), `lit_mech.py` and `lit_mech.json`, `lit_class.py` and `lit_class.json`,
`lit_metformin.py` and `lit_metformin.json`, `c3_gentamicin.py` and `c3_gentamicin.json`,
`claim_provenance.py` and `claim_provenance.json` (the DGIdb typing check).

Agent: nc-eval-b4b. Public data only. No patient-derived data. No existing file was edited and
nothing was deleted outside this work directory. Run date 2026-10-20.
