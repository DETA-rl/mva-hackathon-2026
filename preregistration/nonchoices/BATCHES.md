# BATCHES: the candidate universe for the "Non-choices" section, and its evaluation batches

Governed by `PRE_REG_NONCHOICES.md`, sha256
`ed19c9360d3089c0084f4b61492bb30ba7b5edd2e462007bd94987544281dde4`, frozen 2026-10-20T11:42:00Z
(Mac), box copy verified by checksum at 2026-10-20T11:41:20Z. Every count and every name below
was produced after that freeze, except the four endpoint-syntax probes disclosed in Section 1.3
of the pre-registration. No section of the pre-registration was amended.

Agent: nonchoice-prereg-2. Public data only. No patient-derived data. Only gene symbols, drug
names, mechanism terms and PMIDs left this machine. No existing file was edited and nothing was
deleted.

Non-clinical clause, repeated: this is a hypothesis-screening document about published mechanism
and database facts. It is not clinical advice, proposes no dose or regimen for any person, and
must not be read as a recommendation to administer anything. Nothing in this file disposes of
any drug: the evaluation runs later, under the frozen criteria of pre-registration Section 5.

VERIFIED means retrieved from the named API this run or computed here from a public file.
UNVERIFIED means anything else and is labelled inline.

---

## 1. What the stated procedure returned

| Arm | What ran | Result | Calls |
|---|---|---|---|
| A1 DGIdb | GraphQL, 46 gene symbols in 5 batches, kept `drug.approved == true` | 163 approved interactions, **124 distinct drugs** | 5 |
| A2 ChEMBL | UniProt accession per symbol, then human SINGLE PROTEIN targets, then mechanisms, then `max_phase == 4` | 47 accessions, 46 of 46 genes mapped, 33 targets, 45 mechanism records, **1 approved drug** | 10 |
| B PubMed | L1 to L4 verbatim, retmax 200, extraction against the Drugs@FDA `Products.txt` lexicon (6,846 names) | L1 451 (truncated at 200), L2 10, L3 3, L4 129. **118 distinct names** | 10 |

Call budget: 25 of the 100 fixed in pre-registration Section 2.1. No gene exceeded the 50-drug
class bound, so no gene was carried as a class for that reason.

**Universe: 217 distinct molecules.** 200 new, 9 already evaluated, 8 excluded as non-specific
chemical names (oxygen, sodium, calcium, potassium, amino acids, nitric oxide, cysteine,
adenosine: lexicon artefacts, not drug proposals). Reached by both arms independently: 20.
Arm A only: 101. Arm B only: 96.

With the 26 in-scope names added by the completeness check of Section 3, the evaluation set is
**226 new drugs**.

## 2. Three findings about the procedure itself, reported because they are negative

**2.1 The ChEMBL arm returned almost nothing, and that is a property of the frozen filter.**
Pre-registration Section 2.1 step 2 fixed `target_type == "SINGLE PROTEIN"` before the run.
ChEMBL attaches many approved-drug mechanisms to PROTEIN COMPLEX or PROTEIN FAMILY targets
instead. Checked directly: the human mTOR single-protein target CHEMBL2842 carries 26 mechanism
records of which exactly one molecule is `max_phase 4` (perhexiline maleate), while the
FKBP12A/mTOR complex target CHEMBL2221341 carries zero mechanism records, so the rapalogs are
reached by neither. This was verified as a filter property, not an implementation bug, before
being written down. The consequence is that arm A rests almost entirely on DGIdb, which is a
single point of failure the pre-registration did not anticipate.

**2.2 The literature arm is mechanism-neutral and mostly returned chemo-sensitivity
co-occurrence.** The top names by PMID count are paclitaxel (35), cisplatin (31), doxorubicin
(17), docetaxel (12). These come from papers in which BubR1 or the checkpoint modulates
sensitivity to a cytotoxic, not from papers proposing a treatment for this disease. The frozen
queries L1 to L4 cannot separate the two, and no filter was added afterwards to make the output
look better. These drugs are in the universe and are carried to evaluation in Batch 4.

**2.3 Disclosed deviation: the extraction implementation is looser than the frozen rule.**
Pre-registration Section 2.2 requires that a name be extracted only if it appears "as a named
molecule given to cells, animals or people". The implementation tests for the name's presence in
the title or abstract and does not verify administration. The deviation is one-directional: it
can only ADD names to the universe, never remove one, so it cannot cause a false removal. It is
the main cause of finding 2.2. Recorded, not corrected after the fact.

## 3. Completeness check against the internal list

Read at the level of drug names only, per pre-registration Section 3. No source, no count, no
attribution, and the report never names or counts anyone.

- Names checked: 62. **Reached by the stated screen: 20** (amikacin, amlexanox, arimoclomol,
  aspirin, baricitinib, bortezomib, carbamazepine, chloroquine, dasatinib, entrectinib,
  etoposide, everolimus, gentamicin, metformin, niacin, quercetin, resveratrol, simvastatin,
  sirolimus, sorafenib).
- Already evaluated by this project, so not new whether or not the screen reached them:
  fingolimod, nicotinamide, NMN, NR, sodium phenylbutyrate, glycerol phenylbutyrate.
- **Not reached and in scope: 26.** These enter tagged "also considered, reached outside the
  stated screen": acetylcysteine, ambroxol, ataluren, azithromycin, digoxin, escin, fisetin,
  hydroxychloroquine, idebenone, irinotecan, isotretinoin, L-glutamine, levetiracetam,
  mesalamine, potassium citrate, pralsetinib, propranolol, rilmenidine, ruxolitinib, somatropin,
  spermidine, tauroursodeoxycholic acid, teprenone, tocilizumab, trametinib, trehalose.
- Not reached and out of scope under the Section 2 inclusion rule, because they are
  investigational rather than market-approved: adavosertib, AICAR, alisertib, bimoclomol,
  CFI-402257, defosbarasertib, DT-061, ELX-02, pimitespib, sovilnesib. Recorded for completeness
  and not evaluated.

**Falsifier check, as pre-registered.** "'Also considered' rows are a small residue" would have
been falsified by the internal list contributing more names than arms A and B together. It
contributes 26 against 200. **Not falsified**, so the stated procedure stands as the universe's
source. The honest other half: the screen reached only 20 of 62 internal names, so it is a
usable instrument and not a complete one, and Section 2.3 of the pre-registration already said
it would not reach a drug whose rationale has never been written down.

**Positive control, not pre-registered and therefore reported as an observation only.** The
screen independently re-found 9 drugs this project had already disposed of: arimoclomol and
niacin (carried candidates), everolimus, sirolimus and temsirolimus (removed by T2-P4), and
belinostat, panobinostat, valproic acid and vorinostat (excluded by RESULT-R2C-HDAC). It did not
re-find nicotinamide, NMN, NR, phenylbutyrate or fingolimod. Both halves are stated.

## 4. Expectations recorded in advance, and how they came out

Pre-registration Section 1.2 recorded, before the run, that NAD+ precursors, proteostasis
agents, mTOR inhibitors, senolytic combinations, readthrough agents, proteasome inhibitors,
chloroquine-class antimalarials, metformin and HSP90 inhibitors were expected to appear. Outcome:
confirmed for mTOR inhibitors, proteasome inhibitors (bortezomib, carfilzomib, ixazomib),
chloroquine, metformin, HSP90 inhibitors and the senolytic components dasatinib and quercetin;
reached only through the completeness check for the readthrough agents. These are **confirmed
expectations, not discoveries**, and the report must present them as such.

---

## 5. The batches

Four batches, grouped by the mechanism block of the gene that returned the drug. A drug returned
by more than one block is placed in its lowest-numbered block. The grouping is an evaluation
unit only: it carries no ranking, no priority and no judgement about any drug.

Reading the columns: "Claimed target or mechanism" is the DGIdb interaction type or the ChEMBL
mechanism-of-action string as served by the API, or the target gene where no mechanism string
exists; it is the database's claim, not ours, and it is UNVERIFIED until the evaluation checks
it. "Source record" is the DGIdb `conceptId`, the ChEMBL molecule ID, or PMIDs for arm B.
"Arm" is A1 (DGIdb), A2 (ChEMBL), B (PubMed).

Batch 4 is large because it absorbs both the mitotic block and the unassigned literature
co-occurrence of finding 2.2. At evaluation, pre-registration Section 5.6 permits class-level
disposal only where the deciding evidence is itself class-level; each drug outside such a class
is evaluated individually.

### Batch 1. Proteostasis, chaperone and heat-shock route (45 drugs)

| Drug (INN or common name) | Claimed target or mechanism | Source record | Arm |
|---|---|---|---|
| acetylcysteine | not assigned by the screen | also considered | - |
| ambroxol | not assigned by the screen | also considered | - |
| amlexanox | targets HSP90AA1 | rxcui:46307 | A1 |
| bevacizumab | targets HSP90AB1 | rxcui:253337 | A1 |
| bicyclol | targets HSPA1A | ncit:C221873 | A1 |
| bifonazole | targets HSP90AA1 | rxcui:19295 | A1 |
| butoconazole | targets HSP90AA1 | chembl:CHEMBL1200398 | A1 |
| cabazitaxel | targets HSPA1A, MTOR | rxcui:996051 | A1 |
| carbamazepine | targets HSPA1A | rxcui:2002 | A1 |
| carmofur | targets HSPA1A | ncit:C955 | A1 |
| chloroxine | targets HSP90AA1 | rxcui:20875 | A1 |
| clioquinol | targets HSP90AA1 | rxcui:5942 | A1 |
| clotrimazole | targets HSP90AA1 | rxcui:2623 | A1 |
| daunorubicin | targets HSP90AA1, HSP90AB1 | chembl:CHEMBL1563 | A1+B |
| diacetylrhein | targets HSP90AA1, HSP90AB1 | rxcui:22759 | A1 |
| dipyridamole | targets HSP90AA1, HSP90AB1 | rxcui:3521 | A1 |
| disulfiram | targets HSP90AA1, MTOR | rxcui:3554 | A1+B |
| doxorubicin | targets HSP90AA1, HSP90AB1 | rxcui:142433 | A1+B |
| econazole | targets HSP90AA1 | chembl:CHEMBL1201049 | A1 |
| escin | not assigned by the screen | also considered | - |
| fluconazole | targets HSP90AA1 | rxcui:4450 | A1 |
| halofantrine | targets HSP90AA1 | chembl:CHEMBL1200901 | A1 |
| hexachlorophene | targets HSP90AA1 | rxcui:5293 | A1 |
| iodoquinol | targets HSP90AA1 | rxcui:3435 | A1 |
| itraconazole | targets HSP90AA1 | chembl:CHEMBL64391 | A1 |
| l-glutamine | not assigned by the screen | also considered | - |
| levoketoconazole | targets HSP90AA1 | rxcui:2588846 | A1 |
| masoprocol | targets HSP90AA1, HSP90AB1 | rxcui:227239 | A1 |
| miconazole | targets HSP90AA1 | chembl:CHEMBL1559, rxcui:42790 | A1 |
| nedocromil | targets HSP90AA1 | rxcui:31563 | A1 |
| nitroxoline | targets HSP90AA1, SIRT1 | rxcui:31901 | A1 |
| novobiocin | targets HSP90AA1, HSP90AB1 | rxcui:7538 | A1 |
| o-phenanthroline | targets HSP90AA1, MTOR | rxcui:1872047 | A1 |
| ponatinib | targets HSP90AA1 | rxcui:1364347 | A1 |
| quercetin | targets HSF1, SIRT1 | rxcui:9060 | A1 |
| sertaconazole | targets HSP90AA1 | chembl:CHEMBL1200725 | A1 |
| silibinin | targets HSP90AA1, HSP90AB1 | ncit:C152359 | A1 |
| sulconazole | targets HSP90AA1 | chembl:CHEMBL1200348 | A1 |
| tauroursodeoxycholic acid | not assigned by the screen | also considered | - |
| teprenone | not assigned by the screen | also considered | - |
| terconazole | targets HSP90AA1 | rxcui:37806 | A1 |
| tetracycline | targets HSP90AA1, HSP90AB1 | rxcui:10395 | A1 |
| trehalose | not assigned by the screen | also considered | - |
| triclabendazole | targets HSP90AA1 | rxcui:2118525 | A1 |
| triclosan | targets HSP90AA1 | rxcui:10795 | A1 |

### Batch 2. NAD+, sirtuin and acetyltransferase route (20 drugs)

| Drug (INN or common name) | Claimed target or mechanism | Source record | Arm |
|---|---|---|---|
| alendronate | targets SIRT1 | rxcui:203152 | A1 |
| alprazolam | targets CREBBP | rxcui:596 | A1 |
| colchicine | targets CREBBP | rxcui:2683 | A1+B |
| curcumin | targets EP300 | rxcui:2955 | A1 |
| epigallocatechin gallate | EP300 inhibitor; KAT2B inhibitor | rxcui:24246 | A1 |
| estazolam | targets CREBBP | rxcui:4077 | A1 |
| fisetin | not assigned by the screen | also considered | - |
| gefitinib | targets SIRT2 | rxcui:328134 | A1+B |
| ibandronic acid | targets SIRT1 | rxcui:115264 | A1 |
| idebenone | not assigned by the screen | also considered | - |
| isotretinoin | not assigned by the screen | also considered | - |
| methylphenidate | targets CREBBP, EP300 | rxcui:203188 | A1 |
| midazolam | targets CREBBP | rxcui:203128 | A1 |
| papaverine | targets CREBBP | rxcui:7895 | A1 |
| resveratrol | targets SIRT1 | rxcui:1000492 | A1 |
| risedronic acid | targets SIRT1 | rxcui:55685 | A1 |
| spermidine | not assigned by the screen | also considered | - |
| suramin | targets SIRT1 | rxcui:10256 | A1 |
| triazolam | targets CREBBP, KAT2B | rxcui:10767 | A1 |
| zoledronic acid | targets SIRT1 | rxcui:1546014 | A1+B |

### Batch 3. Ubiquitin-proteasome, APC/C and PP2A route (14 drugs)

| Drug (INN or common name) | Claimed target or mechanism | Source record | Arm |
|---|---|---|---|
| ataluren | not assigned by the screen | also considered | - |
| azithromycin | not assigned by the screen | also considered | - |
| bortezomib | PSMB1 inhibitor; PSMB1 inhibitor,other/unknown; PSMB2 inhibitor | chembl:CHEMBL5315122, rxcui:358258 | A1+B |
| cantharidin | PPP2CA inhibitor | rxcui:1984 | A1 |
| carfilzomib | PSMB1 inhibitor,other/unknown; PSMB2 other/unknown,inhibitor; PSMB5 other/unknown,inhibitor | rxcui:1302966 | A1 |
| cyclophosphamide | targets PPP2R5D | rxcui:1545988 | A1+B |
| docetaxel | targets FBXW7 | rxcui:1299922 | A1+B |
| epirubicin | targets PPP2R5D | rxcui:3995 | A1+B |
| fluorouracil | targets PPP2R5D | rxcui:4492 | A1+B |
| ixazomib | PSMB1 inhibitor; PSMB2 inhibitor; PSMB5 inhibitor | chembl:CHEMBL3545432, rxcui:1723734, rxcui:1723735 | A1 |
| maduramicin | targets PPP2CA | chembl:CHEMBL1909065 | A1 |
| pembrolizumab | targets FBXW7 | rxcui:1547545 | A1 |
| regorafenib | targets FBXW7 | rxcui:1312397 | A1+B |
| thonzonium | targets PSMB5 | rxcui:237058 | A1 |

### Batch 4. Mitotic-checkpoint, aneuploidy-tolerance and unassigned literature co-occurrence (147 drugs)

| Drug (INN or common name) | Claimed target or mechanism | Source record | Arm |
|---|---|---|---|
| afatinib | not assigned by the screen (literature co-occurrence only) | PMID 36605099, 39169044, 41184881 | B |
| alpelisib | MTOR inhibitor | rxcui:2169285 | A1 |
| amikacin | not assigned by the screen (literature co-occurrence only) | PMID 41579174 | B |
| amiodarone | targets MTOR | rxcui:203114 | A1 |
| amsacrine | targets MTOR | rxcui:739 | A1 |
| arsenic trioxide | not assigned by the screen (literature co-occurrence only) | PMID 18501396, 24519527, 30899418, 33767726 | B |
| ascorbic | not assigned by the screen (literature co-occurrence only) | PMID 31478449, 40595080 | B |
| aspirin | not assigned by the screen (literature co-occurrence only) | PMID 40702150 | B |
| atorvastatin | not assigned by the screen (literature co-occurrence only) | PMID 42146413 | B |
| axitinib | PLK4 inhibitor | rxcui:1242999 | A1 |
| azathioprine | not assigned by the screen (literature co-occurrence only) | PMID 33767726 | B |
| baricitinib | not assigned by the screen (literature co-occurrence only) | PMID 42278672 | B |
| belumosudil | targets AURKB | rxcui:2564025 | A1 |
| bendamustine | not assigned by the screen (literature co-occurrence only) | PMID 40068082 | B |
| beta-hydroxyisovaleric | targets MTOR | drugbank:DB15344 | A1 |
| bleomycin | not assigned by the screen (literature co-occurrence only) | PMID 25483095 | B |
| cabozantinib | not assigned by the screen (literature co-occurrence only) | PMID 39911278, 41545558 | B |
| calcitriol | not assigned by the screen (literature co-occurrence only) | PMID 36389792, 40286596 | B |
| canagliflozin | not assigned by the screen (literature co-occurrence only) | PMID 38513740 | B |
| capecitabine | not assigned by the screen (literature co-occurrence only) | PMID 24519527 | B |
| capivasertib | targets MTOR | rxcui:2669967 | A1 |
| carbon dioxide | not assigned by the screen (literature co-occurrence only) | PMID 37274003 | B |
| carboplatin | not assigned by the screen (literature co-occurrence only) | PMID 31987036, 34386075, 37657029, 37808164 | B |
| chloroquine | not assigned by the screen (literature co-occurrence only) | PMID 35847923 | B |
| chlorpromazine | not assigned by the screen (literature co-occurrence only) | PMID 33708237, 37808164 | B |
| cisplatin | not assigned by the screen (literature co-occurrence only) | PMID 24519527, 25483095, 31478449, 31853539 | B |
| cladribine | not assigned by the screen (literature co-occurrence only) | PMID 33083112, 37808164 | B |
| copanlisib | MTOR inhibitor | rxcui:1945077 | A1 |
| cyclosporine | not assigned by the screen (literature co-occurrence only) | PMID 40286596, 41381790 | B |
| cytarabine | not assigned by the screen (literature co-occurrence only) | PMID 37808164 | B |
| dapagliflozin | not assigned by the screen (literature co-occurrence only) | PMID 38513740 | B |
| dasatinib | targets AURKB, PLK4 | rxcui:1546019 | A1+B |
| decitabine | not assigned by the screen (literature co-occurrence only) | PMID 37002311 | B |
| dequalinium | targets MTOR | rxcui:3226 | A1 |
| dexamethasone | not assigned by the screen (literature co-occurrence only) | PMID 32850387, 34919076, 37808164, 40068082 | B |
| dexrazoxane | not assigned by the screen (literature co-occurrence only) | PMID 37808164, 42483440 | B |
| digoxin | not assigned by the screen | also considered | - |
| donepezil | not assigned by the screen (literature co-occurrence only) | PMID 32764382, 32850387 | B |
| doxazosin | targets MTOR | rxcui:39173 | A1 |
| doxycycline | not assigned by the screen (literature co-occurrence only) | PMID 16227576 | B |
| ebastine | targets MTOR | rxcui:23796 | A1 |
| eltrombopag | not assigned by the screen (literature co-occurrence only) | PMID 41439111 | B |
| entrectinib | targets AURKB, PLK4 | rxcui:2197862 | A1 |
| enzalutamide | not assigned by the screen (literature co-occurrence only) | PMID 42757823 | B |
| epinephrine | targets MTOR | rxcui:3992 | A1 |
| erlotinib | targets AURKB | rxcui:337525 | A1+B |
| estradiol | not assigned by the screen (literature co-occurrence only) | PMID 32151056, 36389792 | B |
| estradiol and progesterone | not assigned by the screen (literature co-occurrence only) | PMID 36389792 | B |
| etomidate | not assigned by the screen (literature co-occurrence only) | PMID 40565600 | B |
| etoposide | not assigned by the screen (literature co-occurrence only) | PMID 33186389, 34304612, 36245843, 36389792 | B |
| fasudil | targets AURKB | ncit:C65624 | A1 |
| fenretinide | targets MTOR | ncit:C1098 | A1 |
| fentanyl | not assigned by the screen (literature co-occurrence only) | PMID 40273626 | B |
| ferric | not assigned by the screen (literature co-occurrence only) | PMID 40595080 | B |
| ferrous | not assigned by the screen (literature co-occurrence only) | PMID 39949372 | B |
| fluvastatin | not assigned by the screen (literature co-occurrence only) | PMID 41053901 | B |
| gemcitabine | not assigned by the screen (literature co-occurrence only) | PMID 33708237, 34147108, 38410481, 38987356 | B |
| gentamicin | not assigned by the screen (literature co-occurrence only) | PMID 41579174 | B |
| glasdegib | targets MTOR | rxcui:2105845 | A1 |
| glucagon | not assigned by the screen (literature co-occurrence only) | PMID 39949372 | B |
| griseofulvin | not assigned by the screen (literature co-occurrence only) | PMID 42330849 | B |
| haloperidol decanoate | targets MTOR | rxcui:26420 | A1 |
| heather | not assigned by the screen (literature co-occurrence only) | PMID 41381790 | B |
| herceptin | not assigned by the screen (literature co-occurrence only) | PMID 34035233 | B |
| hesperidin | targets AURKB | rxcui:5281 | A1 |
| hydroxychloroquine | not assigned by the screen | also considered | - |
| idarubicin | targets MTOR | rxcui:5650 | A1+B |
| ifenprodil | targets MTOR | rxcui:27403 | A1 |
| ifosfamide | not assigned by the screen (literature co-occurrence only) | PMID 37808164 | B |
| imatinib | not assigned by the screen (literature co-occurrence only) | PMID 20442314, 36567949, 40565600, 41169944 | B |
| infigratinib | MTOR inhibitor | rxcui:2550729 | A1 |
| irinotecan | not assigned by the screen | also considered | - |
| isoniazid | not assigned by the screen (literature co-occurrence only) | PMID 33244299 | B |
| isoproterenol | targets MTOR | rxcui:6054 | A1 |
| lapatinib | targets AURKB | rxcui:480167 | A1 |
| lenvatinib | not assigned by the screen (literature co-occurrence only) | PMID 33922244, 39911278 | B |
| letrozole | not assigned by the screen (literature co-occurrence only) | PMID 31942195, 42168250 | B |
| levetiracetam | not assigned by the screen | also considered | - |
| levocetirizine | targets MTOR | rxcui:356887 | A1 |
| levonorgestrel | not assigned by the screen (literature co-occurrence only) | PMID 42483440 | B |
| levophed | not assigned by the screen (literature co-occurrence only) | PMID 40209578 | B |
| loperamide | targets MTOR | rxcui:6468 | A1 |
| lovastatin | not assigned by the screen (literature co-occurrence only) | PMID 41516135, 42146413 | B |
| maprotiline | targets MTOR | rxcui:6646 | A1 |
| melphalan | not assigned by the screen (literature co-occurrence only) | PMID 40068082 | B |
| mesalamine | not assigned by the screen | also considered | - |
| metformin | MTOR inhibitor | chembl:CHEMBL1703, rxcui:6809 | A1+B |
| methotrexate | not assigned by the screen (literature co-occurrence only) | PMID 37808164, 39045407, 40750410 | B |
| mifepristone | targets MTOR | rxcui:6964 | A1+B |
| minocycline | not assigned by the screen (literature co-occurrence only) | PMID 31987036, 32121037 | B |
| mitomycin | not assigned by the screen (literature co-occurrence only) | PMID 41169944 | B |
| mitoxantrone | not assigned by the screen (literature co-occurrence only) | PMID 32850387 | B |
| nicardipine | targets MTOR | rxcui:7396 | A1 |
| niclosamide | targets MTOR | rxcui:7402 | A1 |
| nicotine | not assigned by the screen (literature co-occurrence only) | PMID 31853539, 34919076 | B |
| nikita | not assigned by the screen (literature co-occurrence only) | PMID 32154490 | B |
| olaparib | not assigned by the screen (literature co-occurrence only) | PMID 34545188 | B |
| osimertinib | not assigned by the screen (literature co-occurrence only) | PMID 31877723, 41184881 | B |
| oxaliplatin | not assigned by the screen (literature co-occurrence only) | PMID 31987036, 33767726, 39733078, 40056529 | B |
| paclitaxel | not assigned by the screen (literature co-occurrence only) | PMID 11451998, 16227576, 16639080, 17234259 | B |
| palbociclib | not assigned by the screen (literature co-occurrence only) | PMID 34257537, 42168250 | B |
| paroxetine hydrochloride, hemihydrate | targets MTOR | rxcui:1298842 | A1 |
| pazopanib | targets AURKB, MTOR | rxcui:714438 | A1+B |
| pentamidine isethionate | targets MTOR | chembl:CHEMBL361506 | A1 |
| pentostatin | not assigned by the screen (literature co-occurrence only) | PMID 39169044 | B |
| perhexiline | MTOR inhibitor; Serine/threonine-protein kinase mTOR inhibitor | CHEMBL1334033, chembl:CHEMBL1334033 | A1+A2 |
| perphenazine | targets MTOR | rxcui:8076 | A1 |
| pimecrolimus | targets MTOR | rxcui:321952 | A1 |
| pimozide | targets MTOR | rxcui:8331 | A1 |
| pitavastatin | not assigned by the screen (literature co-occurrence only) | PMID 40565600 | B |
| polymyxin b | not assigned by the screen (literature co-occurrence only) | PMID 35326770 | B |
| potassium citrate | not assigned by the screen | also considered | - |
| potassium iodide | not assigned by the screen (literature co-occurrence only) | PMID 41439111 | B |
| pralsetinib | not assigned by the screen | also considered | - |
| prednisone | not assigned by the screen (literature co-occurrence only) | PMID 32850387 | B |
| progesterone | not assigned by the screen (literature co-occurrence only) | PMID 26312894, 33902659, 35719392, 36389792 | B |
| propafenone | targets MTOR | rxcui:8754 | A1 |
| propofol | not assigned by the screen (literature co-occurrence only) | PMID 40470792 | B |
| propranolol | not assigned by the screen | also considered | - |
| quinacrine | targets MTOR | rxcui:9061 | A1 |
| ribociclib | not assigned by the screen (literature co-occurrence only) | PMID 42726806 | B |
| rilmenidine | not assigned by the screen | also considered | - |
| rimegepant | not assigned by the screen (literature co-occurrence only) | PMID 41439111 | B |
| ruxolitinib | not assigned by the screen | also considered | - |
| sapanisertib | MTOR inhibitor | rxcui:2395271 | A1 |
| sevoflurane | not assigned by the screen (literature co-occurrence only) | PMID 40273626 | B |
| sildenafil | not assigned by the screen (literature co-occurrence only) | PMID 32764382, 32850387 | B |
| simvastatin | not assigned by the screen (literature co-occurrence only) | PMID 38604342, 42146413 | B |
| somatropin | not assigned by the screen | also considered | - |
| sorafenib | targets AURKB, PLK4 | rxcui:495881 | A1 |
| tadalafil | not assigned by the screen (literature co-occurrence only) | PMID 32850387 | B |
| tamoxifen | not assigned by the screen (literature co-occurrence only) | PMID 31942195, 32724412, 33083112, 33186389 | B |
| temozolomide | not assigned by the screen (literature co-occurrence only) | PMID 32121037, 39911278, 42211827 | B |
| terfenadine | targets MTOR | rxcui:42330 | A1 |
| testosterone | not assigned by the screen (literature co-occurrence only) | PMID 36389792 | B |
| tocilizumab | not assigned by the screen | also considered | - |
| topotecan | not assigned by the screen (literature co-occurrence only) | PMID 33186389, 33767726 | B |
| trabectedin | not assigned by the screen (literature co-occurrence only) | PMID 42726806 | B |
| trametinib | not assigned by the screen | also considered | - |
| trifluoperazine | not assigned by the screen (literature co-occurrence only) | PMID 33708237 | B |
| vandetanib | targets AURKB, MTOR | rxcui:1098413 | A1 |
| vardenafil | not assigned by the screen (literature co-occurrence only) | PMID 32850387 | B |
| vinblastine | not assigned by the screen (literature co-occurrence only) | PMID 20646066, 32764382, 32765860 | B |
| vincristine | not assigned by the screen (literature co-occurrence only) | PMID 23812934, 32850387, 37808164, 38410481 | B |
| vinorelbine | not assigned by the screen (literature co-occurrence only) | PMID 23812934, 32764382, 32850387, 41169944 | B |
| vitamin d | not assigned by the screen (literature co-occurrence only) | PMID 36389792, 40595080 | B |
| zotarolimus | targets MTOR | ncit:C82294 | A1 |
---

## 6. What happens next, and what this file does not do

The evaluation of these 226 drugs runs under pre-registration Section 5 and nothing in this file
anticipates its outcome. In particular:

- No drug here is removed, kept or ranked by this file.
- C4 (plasma concentration against an enzyme IC50) will be reported and will remove nothing,
  per pre-registration Section 5.4, decided before this universe was known because
  RESULT-R2D-R2E declared that instrument NON-DISCRIMINATING.
- A drug that passes C1, C3 and C5 is KEPT AS A CANDIDATE and joins the ranked list under
  RANKING-RULE-T2 unchanged. The pre-registration forbids keeping a passing drug out of the
  ranking on the ground that we did not propose it first.
- A DepMap flag alone removes nothing here. It is the safety tie-break input, and the caveat
  travels with it: a CRISPR knockout is a loss-of-function proxy in cancer lines, never normal
  marrow, so no flag is a safety verdict and no absent flag is a safety clearance.

## 7. Files

Mac, all in `scratchpad/agent_out/nonchoices/`: `PRE_REG_NONCHOICES.md`,
`PRE_REG_NONCHOICES.sha256`, `armA_screen.py`, `armB_screen.py`, `assemble.py`, `batches.py`,
`armA_raw.json`, `armB_raw.json`, `universe.json`, `BATCHES.md`.
Box, `~/Documents/HACKATON/_private/agent_out/nonchoices/`: the same files, plus the
pre-existing public `dl_fda/` bulk Drugs@FDA download used as the name lexicon.
