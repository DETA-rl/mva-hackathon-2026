import re
T="/private/tmp/[redacted]/scratchpad/t2/evidence/checkA_txt/"
SRC_PMC_XML="fulltext PMC (XML)"
SRC_PMC_WEB="fulltext PMC (web page; XML blocked by publisher)"
SRC_ABS="abstract (no PMC full text)"
# (pmid, draft_line, source, sections, quotes, verdict, note)  quotes/sections joined by ' || '
R = [
("15475955","13",SRC_ABS,"Title || Abstract || Abstract",
 "Constitutional aneuploidy and cancer predisposition caused by biallelic mutations in BUB1B || truncating and missense mutations of BUB1B, which encodes BUBR1 || a key protein in the mitotic spindle checkpoint",
 "PARTLY",
 "Draft sentence 1: MVA linked to biallelic loss-of-function variants in BUB1B, the gene encoding the checkpoint kinase BubR1. Supported: biallelic BUB1B mutations (title) and BUB1B encodes BUBR1. Not stated: loss-of-function (abstract says truncating and missense mutations) and checkpoint kinase (abstract says key protein in the spindle checkpoint). Drop loss-of-function or cite a source that shows it."),
("15475955","13",SRC_ABS,"Abstract",
 "In five families with mosaic variegated aneuploidy, including two with embryonal rhabdomyosarcoma",
 "PARTLY",
 "Draft sentence 2: two of the originally reported patients developed rhabdomyosarcoma. Paper: two of five families had (embryonal) rhabdomyosarcoma. Unit is families, not patients. Fix to families or check the full paper's case table."),
("15475955","29",SRC_ABS,"Title || Abstract || Abstract",
 "Constitutional aneuploidy and cancer predisposition caused by biallelic mutations in BUB1B || These data are the first to relate germline mutations in a spindle checkpoint gene with a human disorder || strongly support a causal link between aneuploidy and cancer development",
 "SUPPORTED",
 "Draft: biallelic BUB1B mutations were first shown to cause MVA with a cancer predisposition. Paper claims first link of germline spindle-checkpoint gene mutations to a human disorder and says it strongly supports (does not prove) an aneuploidy-cancer link."),
("15475955","29",SRC_ABS,"Abstract",
 "In five families with mosaic variegated aneuploidy, including two with embryonal rhabdomyosarcoma",
 "PARTLY",
 "Draft: two of the reported patients developed RMS. Same unit issue as L13 row: paper says two of five families."),
("15475955","62",SRC_ABS,"Title || Abstract",
 "Mosaic variegated aneuploidy is a rare recessive condition characterized by growth retardation, microcephaly, childhood cancer || strongly support a causal link between aneuploidy and cancer development",
 "SUPPORTED",
 "Draft: MVA with a documented cancer predisposition in the reference cohort. Childhood cancer is in the abstract. Reference cohort wording is the draft's own."),
("15475955","184",SRC_ABS,"Title || Abstract",
 "Constitutional aneuploidy and cancer predisposition caused by biallelic mutations in BUB1B || strongly support a causal link between aneuploidy and cancer development",
 "SUPPORTED",
 "Draft: the MVA cohort has a documented cancer predisposition. Same support as L62."),
("18932004","13",SRC_ABS,"Abstract || Abstract",
 "Aneuploidy was clearly detected in cells with residual BUBR1 below 50%. || the function of the human BUBR1 protein in the spindle checkpoint is remarkably dosage-dependent",
 "SUPPORTED",
 "Draft: residual BUBR1 level appears to govern the aneuploidy phenotype, with aneuploidy below roughly 50%. Data are from shRNA knockdown HeLa cells, not patient cells; the draft should say so if it is read as patient data."),
("18932004","37",SRC_ABS,"Abstract || Abstract",
 "We obtained stable shRNA-transduced HeLa cells displaying a gradient of residual BUBR1 protein || Aneuploidy was clearly detected in cells with residual BUBR1 below 50%.",
 "SUPPORTED",
 "Draft: graded reduction of BUBR1 gives a graded aneuploidy phenotype below roughly 50%. Gradient of 8.5 to 77 percent residual BUBR1 in HeLa cells. Model is cell culture only."),
("18932004","72",SRC_ABS,"Abstract",
 "Aneuploidy was clearly detected in cells with residual BUBR1 below 50%.",
 "SUPPORTED",
 "Draft: BUBR1 level is associated with the aneuploidy threshold. Supported in HeLa model only."),
("18932004","160",SRC_ABS,"Abstract || Abstract",
 "Aneuploidy was clearly detected in cells with residual BUBR1 below 50%. || We obtained stable shRNA-transduced HeLa cells displaying a gradient of residual BUBR1 protein",
 "SUPPORTED",
 "Draft: the roughly 50 percent threshold from PMID 18932004 is the reference point for the expected curve. Fine as a reference point; threshold is from one HeLa shRNA series, not a validated patient threshold."),
("24825348","17",SRC_PMC_WEB,"Abstract || Results",
 "Overexpression of SIRT2 or treatment of mice with the NAD+ precursor nicotinamide mononucleotide (NMN) increases BubR1 abundance in vivo. || BubR1 protein levels were clearly increased in testes following NMN treatment",
 "SUPPORTED",
 "Draft H1 sentence, claim (a): NMN raised BubR1 in vivo. Supported; in vivo increase shown in testes. Heart in aged mice could not be assessed (Results)."),
("24825348","17",SRC_PMC_WEB,"Introduction || Results || Results || Results",
 "SIRT2 overexpression extends both mean and maximum lifespan of BubR1H/H mice. || they experienced a 58%increase in median lifespan and 21%increase in maximal lifespan || Lifespan extension was observed preferentially in male mice, with a 123%increase in median lifespan || There was no change in median lifespan for females",
 "SUPPORTED",
 "Draft H1 sentence, claim (b): SIRT2 overexpression extended median lifespan in BubR1 H/H mice. Supported for the pooled group (+58 percent median). Caveat the draft omits: the median gain was male-only (+123 percent); females showed no change. Source text writes 58%increase without a space."),
("24825348","17",SRC_PMC_WEB,"Results || Results",
 "NMN treatment of wild-type MEFs induced BubR1 protein abundance, and this induction was almost completely absent in the Sirt2−/− MEFs || Together, these results are consistent with a model in which NAD+ levels dictate the level of BubR1 via SIRT2",
 "NOT SUPPORTED",
 "Draft H1 sentence, claim (c): The NMN to SIRT2 link is not shown in that paper and remains a hypothesis. The paper tests it in Sirt2-null MEFs (Fig 6G): NMN-induced BubR1 is almost completely absent without SIRT2, and the authors conclude NAD+ levels dictate BubR1 via SIRT2. Correct to: the link is shown in MEFs (Sirt2-/-), not in vivo."),
("24825348","47",SRC_PMC_WEB,"Abstract || Results",
 "Overexpression of SIRT2 or treatment of mice with the NAD+ precursor nicotinamide mononucleotide (NMN) increases BubR1 abundance in vivo. || they experienced a 58%increase in median lifespan and 21%increase in maximal lifespan",
 "SUPPORTED",
 "Draft L47: in mice NMN raised BubR1 in vivo; SIRT2 overexpression extended median lifespan in H/H mice. Supported (pooled median; male-only caveat as above). The draft's claim that this is the only cited NAD+/BUBR1 link is a statement about the draft's own citation set, not checkable from this paper; the paper also reports NAD+ decline with age (Fig 6A) and nicotinamide, used as a sirtuin inhibitor, lowering BubR1 (Fig 1A-B)."),
("24825348","47",SRC_PMC_WEB,"(none: absence claim)",
 "(none: absence claim)",
 "SUPPORTED",
 "Draft: the paper did not test niacin or nicotinamide riboside. Full-text search: 0 hits for niacin, 0 for riboside. Nicotinamide appears 16 times, used as a sirtuin inhibitor (Fig 1A-B), not as an NAD+ precursor, so the draft wording is correct for niacin and NR but should say nicotinamide was used as an inhibitor. verbatim_check N/A (absence claim)."),
("24825348","72",SRC_PMC_WEB,"Abstract || Results",
 "Overexpression of SIRT2 or treatment of mice with the NAD+ precursor nicotinamide mononucleotide (NMN) increases BubR1 abundance in vivo. || they experienced a 58%increase in median lifespan and 21%increase in maximal lifespan",
 "SUPPORTED",
 "Draft Basis: NMN raised BubR1 in mice and SIRT2 overexpression extended lifespan in H/H mice. Supported; see male-only caveat."),
("25285631","17",SRC_ABS,"Abstract",
 "this increase is not substantial to elevate the levels of total BubR1 or delay the transition from prometaphase to anaphase",
 "SUPPORTED",
 "Draft: SIRT2 knockdown did not change total BubR1 levels or prometaphase timing. Paper says the knockdown raised BubR1 acetylation at prometaphase but the increase was not substantial enough to change total levels or delay the transition. Use not substantially changed rather than did not change."),
("25285631","49",SRC_ABS,"Abstract || Abstract",
 "SIRT2 deacetylates BubR1 K250 both in vitro and in vivo. || this increase is not substantial to elevate the levels of total BubR1 or delay the transition from prometaphase to anaphase",
 "SUPPORTED",
 "Draft: SIRT2 deacetylates BubR1 at K250, but knockdown did not change total BubR1 or prometaphase timing. Both halves supported. Same wording caveat as L17."),
("25285631","76",SRC_ABS,"Abstract",
 "The present study shows that SIRT2 is a deacetylase for BubR1 K250, although the abnormally prolonged SAC activation observed in SIRT2 knockdown cells is not accompanied by a change in BubR1 levels",
 "SUPPORTED",
 "Draft limitation: SIRT2 deacetylates BubR1 K250, knockdown did not change total BubR1 levels or prometaphase timing. Both supported. The inference that SIRT2 acts on BubR1 function rather than abundance is the draft's, not the paper's; it is labelled as a possibility in the draft."),
("25285631","149",SRC_ABS,"Abstract",
 "this increase is not substantial to elevate the levels of total BubR1 or delay the transition from prometaphase to anaphase",
 "SUPPORTED",
 "Draft: Suematsu 2014 found SIRT2 knockdown did not change total BubR1 levels. Journal year 2014 (BBRC, Oct 2014) matches. Same wording caveat as L17."),
("20516114","18",SRC_PMC_XML,"Abstract || Results || Results",
 "Ectopic expression of BUBR1 restored mitotic checkpoint activity, proving that BUBR1 dysfunction causes chromosome segregation errors in the patients. || Strikingly, restoration of high levels of BUBR1 by transient expression of Localization and Affinity Purification (LAP)-tagged BUB1B cDNA || mitotic checkpoint activity was almost fully restored to parental levels",
 "SUPPORTED",
 "Draft H3: re-expression of BUBR1 rescues MVA cells. Supported in patient-derived cell lines (checkpoint activity). Note for H3: this paper rescued patient cells by transient expression of a cDNA, which the draft does not mention, and it is relevant to the claim that transient dosing is untested."),
("20516114","38",SRC_PMC_XML,"Abstract",
 "Ectopic expression of BUBR1 restored mitotic checkpoint activity, proving that BUBR1 dysfunction causes chromosome segregation errors in the patients.",
 "SUPPORTED",
 "Draft: re-expressing BUBR1 rescues the checkpoint defect in MVA cells. Supported; the rescue readout is mitotic checkpoint activity."),
("20516114","82",SRC_PMC_XML,"Abstract",
 "Ectopic expression of BUBR1 restored mitotic checkpoint activity, proving that BUBR1 dysfunction causes chromosome segregation errors in the patients.",
 "SUPPORTED",
 "Draft: re-expression rescues MVA cells. Supported, same caveat as L18 about the checkpoint readout."),
("23242215","18",SRC_PMC_XML,"Abstract",
 "Using a transgenic approach in mice, we show that sustained high expression of BubR1 preserves genomic integrity and reduces tumorigenesis",
 "SUPPORTED",
 "Draft H3: the protective effect was shown with sustained transgenic expression, not transient dosing. Supported. Transient dosing was not tested in the paper, so the second half is an inference from the transgenic design."),
("23242215","39",SRC_PMC_XML,"Title || Abstract",
 "Increased expression of BubR1 protects against aneuploidy and cancer and extends healthy lifespan || Using a transgenic approach in mice, we show that sustained high expression of BubR1 preserves genomic integrity and reduces tumorigenesis",
 "SUPPORTED",
 "Draft: increased BubR1 expression protects against aneuploidy and cancer. Title matches. Aneuploidy evidence is in MEFs (Ras-induced aneuploidy, Fig 2d) and mice; not bolus or transient dosing is an inference, as above."),
("23242215","82",SRC_PMC_XML,"Abstract",
 "Using a transgenic approach in mice, we show that sustained high expression of BubR1 preserves genomic integrity and reduces tumorigenesis",
 "SUPPORTED",
 "Draft: higher BubR1 protects against aneuploidy in a study using sustained transgenic expression, which does not show transient delivery works. Supported; the paper does not test transient delivery."),
("23789096","41",SRC_PMC_XML,"Introduction || Summary (abstract) || Results || Results",
 "Failure to recruit B56-PP2A to BUBR1 also contributes to the chromosome congression defects found in MVA cell lines. || loss of the complex can be reverted by inhibiting Aurora B || the defect in chromosome congression is at least partly due to inefficient recruitment of B56-PP2A to the kinetochores by BUBR1 || artificially targeted PP2A-B56 to the kinetochores by transiently expressing LAP-MIS12-KARD-3D was able to efficiently restore chromosome alignment in both MVA cell lines",
 "PARTLY",
 "Draft L41, four claims. Supported: congression defect partly due to failure of B56 recruitment (paper: at least partly due to inefficient recruitment); Aurora B inhibition reverts loss of the complex (summary). Partly: MVA-patient cells fail to recruit B56-PP2A is the paper's inference from rescue experiments, not a direct measurement of recruitment in patient cells. Last sentence (not a demonstration of congression rescue) conflicts with Fig 4B: transient wild-type BUBR1 and artificially targeted B56-PP2A both restored alignment in MVA lines. Reword: rescue shown by targeted B56-PP2A recruitment, not by BUBR1 itself."),
("24344301","29",SRC_PMC_WEB,"Abstract || Results || Results",
 "A unique single nucleotide substitution, G > A at ss802470619, was identified in an intergenic region 44 kb upstream of a BUB1B transcription start site, which cosegregated with the disorder. || These results suggested that the nucleotide substitution identified was the causal mutation of PCS (MVA) syndrome. || Identification of a Single Nucleotide Substitution in an Intergenic Region Upstream of BUB1B by Deep Sequencing.",
 "PARTLY",
 "Draft: a second BUB1B allele can be an intergenic variant upstream of the gene, which was identified by targeted editing. Supported: intergenic variant 44 kb upstream, causal by editing. Not supported: identified by targeted editing. The variant was identified by haplotype analysis and deep sequencing of the candidate region with cosegregation; targeted editing tested causality. The need-not-be-coding inference follows from the intergenic location. Fix the identification clause."),
("15655110","83",SRC_PMC_WEB,"Abstract",
 "Here we show that depletion of Mad2 in meiosis I mouse oocytes induced an increased incidence of aneuploidy.",
 "SUPPORTED",
 "Draft: Mad2 depletion raises aneuploidy in mouse oocytes. Supported. Morpholino knockdown, at least 85 percent depletion (Results)."),
("25614443","18",SRC_PMC_WEB,"Abstract || Introduction",
 "delivery of modified mRNA encoding TERT to human fibroblasts and myoblasts increases telomerase activity transiently (24–48 h) and rapidly extends telomeres || avoids immortalization, yet transiently increases telomerase activity, rapidly extends telomeres, delays expression of senescence markers, and increases proliferative capacity",
 "PARTLY",
 "Draft H3: transient modified mRNA works in dividing human cells. Supported for one encoded protein (TERT) in fibroblasts and myoblasts, with telomere-extension and proliferation readouts. The draft generalises from TERT to transient modified mRNA in general. Name TERT and the two cell types."),
("25614443","84",SRC_PMC_WEB,"Abstract || Introduction",
 "delivery of modified mRNA encoding TERT to human fibroblasts and myoblasts increases telomerase activity transiently (24–48 h) and rapidly extends telomeres || avoids immortalization, yet transiently increases telomerase activity, rapidly extends telomeres, delays expression of senescence markers, and increases proliferative capacity",
 "PARTLY",
 "Draft: transient modified mRNA encoding a protein works in dividing human cells. Same as L18: only TERT was tested, so a protein generalises beyond the evidence. Name TERT."),
]
import csv, sys
rows=[]
bad=0
for pmid,line,src,secs,quotes,verdict,note in R:
    qs=[q.strip() for q in quotes.split(" || ")]
    ss=[s.strip() for s in secs.split(" || ")]
    checks=[]
    for q in qs:
        if q.startswith("(none"):
            checks.append("N/A"); continue
        s=re.sub(r"\s+"," ",open(T+pmid+".txt",encoding="utf-8").read())
        ok=q in s
        checks.append("PASS" if ok else "FAIL")
        if not ok: bad+=1; print("FAIL",pmid,line,q[:80],file=sys.stderr)
    chk = "PASS" if all(c in ("PASS","N/A") for c in checks) else "FAIL"
    if len(qs)!=len(ss): print("MISMATCH sections",pmid,line,file=sys.stderr); bad+=1
    qjoin=" || ".join(qs); sjoin=" || ".join(ss)
    rows.append([pmid,line,src,sjoin,qjoin,chk,verdict,note.replace("\t"," ").replace("\n"," ")])
out="/private/tmp/[redacted]/scratchpad/t2/evidence/checkA.tsv"
with open(out,"w",encoding="utf-8") as f:
    f.write("\t".join(["pmid","draft_line","source_used","section","verbatim_quote","verbatim_check","verdict","note"])+"\n")
    for r in rows: f.write("\t".join(r)+"\n")
from collections import Counter
print("rows",len(rows),"verbatim fails",bad)
print(Counter(r[6] for r in rows))
print(Counter(r[5] for r in rows))
