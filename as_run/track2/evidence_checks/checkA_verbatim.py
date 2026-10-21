import json, re, sys
T = "/private/tmp/[redacted]/scratchpad/t2/evidence/checkA_txt/"
Q = [
 # pmid, source file, section, quote
 ("15475955","abs_15475955.txt","Abstract","truncating and missense mutations of BUB1B, which encodes BUBR1"),
 ("15475955","abs_15475955.txt","Abstract","In five families with mosaic variegated aneuploidy, including two with embryonal rhabdomyosarcoma"),
 ("15475955","abs_15475955.txt","Title","Constitutional aneuploidy and cancer predisposition caused by biallelic mutations in BUB1B"),
 ("15475955","abs_15475955.txt","Abstract","These data are the first to relate germline mutations in a spindle checkpoint gene with a human disorder"),
 ("15475955","abs_15475955.txt","Abstract","strongly support a causal link between aneuploidy and cancer development"),
 ("18932004","abs_18932004.txt","Abstract","Aneuploidy was clearly detected in cells with residual BUBR1 below 50%."),
 ("18932004","abs_18932004.txt","Abstract","We obtained stable shRNA-transduced HeLa cells displaying a gradient of residual BUBR1 protein"),
 ("18932004","abs_18932004.txt","Abstract","the function of the human BUBR1 protein in the spindle checkpoint is remarkably dosage-dependent"),
 ("25285631","abs_25285631.txt","Abstract","SIRT2 deacetylates BubR1 K250 both in vitro and in vivo."),
 ("25285631","abs_25285631.txt","Abstract","this increase is not substantial to elevate the levels of total BubR1 or delay the transition from prometaphase to anaphase"),
 ("25285631","abs_25285631.txt","Abstract","is not accompanied by a change in BubR1 levels or by delayed progression from prometaphase to anaphase"),
 ("24825348","web_PMC4194088.html.txt","Abstract","Overexpression of SIRT2 or treatment of mice with the NAD+ precursor nicotinamide mononucleotide (NMN) increases BubR1 abundance in vivo."),
 ("24825348","web_PMC4194088.html.txt","Abstract","SIRT2 overexpression extends both mean and maximum lifespan of BubR1H/H mice."),
 ("24825348","web_PMC4194088.html.txt","Results","they experienced a 58%increase in median lifespan and 21%increase in maximal lifespan"),
 ("24825348","web_PMC4194088.html.txt","Results","Lifespan extension was observed preferentially in male mice, with a 123%increase in median lifespan"),
 ("24825348","web_PMC4194088.html.txt","Results","There was no change in median lifespan for females"),
 ("24825348","web_PMC4194088.html.txt","Results","BubR1 protein levels were clearly increased in testes following NMN treatment"),
 ("24825348","web_PMC4194088.html.txt","Results","NMN treatment of wild-type MEFs induced BubR1 protein abundance, and this induction was almost completely absent in the Sirt2−/− MEFs"),
 ("24825348","web_PMC4194088.html.txt","Results","Together, these results are consistent with a model in which NAD+ levels dictate the level of BubR1 via SIRT2"),
 ("24825348","web_PMC4194088.html.txt","Results","we did see a slight increase of BubR1 following NMN treatment in Sirt2−/− MEFs"),
 ("20516114","xml.txt","Abstract","Ectopic expression of BUBR1 restored mitotic checkpoint activity, proving that BUBR1 dysfunction causes chromosome segregation errors in the patients."),
 ("20516114","xml.txt","Results","Strikingly, restoration of high levels of BUBR1 by transient expression of Localization and Affinity Purification (LAP)-tagged BUB1B cDNA"),
 ("20516114","xml.txt","Results","mitotic checkpoint activity was almost fully restored to parental levels"),
 ("23242215","xml.txt","Title","Increased expression of BubR1 protects against aneuploidy and cancer and extends healthy lifespan"),
 ("23242215","xml.txt","Abstract","Using a transgenic approach in mice, we show that sustained high expression of BubR1 preserves genomic integrity and reduces tumorigenesis"),
 ("23242215","xml.txt","Figure legend","Increased BubR1 expression protects against spontaneous tumors and extends lifespan."),
 ("23789096","xml.txt","Abstract","Failure to recruit B56-PP2A to BUBR1 also contributes to the chromosome congression defects found in MVA cell lines."),
 ("23789096","xml.txt","Abstract","loss of the complex can be reverted by inhibiting Aurora B"),
 ("23789096","xml.txt","Results","the defect in chromosome congression is at least partly due to inefficient recruitment of B56-PP2A to the kinetochores by BUBR1"),
 ("23789096","xml.txt","Results","artificially targeted PP2A-B56 to the kinetochores by transiently expressing LAP-MIS12-KARD-3D was able to efficiently restore chromosome alignment in both MVA cell lines"),
 ("24344301","web_PMC3910577.html.txt","Abstract","A single nucleotide substitution in an intergenic region upstream of BUB1B (encoding BUBR1) was identified as a candidate mutation"),
 ("24344301","web_PMC3910577.html.txt","Results heading","Identification of a Single Nucleotide Substitution in an Intergenic Region Upstream of BUB1B by Deep Sequencing."),
 ("24344301","web_PMC3910577.html.txt","Discussion","We identified a single nucleotide substitution (G > A, ss802470619) in an intergenic region 44-kb upstream of BUB1B as a unique causative mutation of PCS (MVA) syndrome."),
 ("15655110","web_PMC545877.html.txt","Abstract","Here we show that depletion of Mad2 in meiosis I mouse oocytes induced an increased incidence of aneuploidy."),
 ("25614443","web_PMC4415018.html.txt","Abstract","delivery of modified mRNA encoding TERT to human fibroblasts and myoblasts increases telomerase activity transiently (24–48 h) and rapidly extends telomeres"),
 ("25614443","web_PMC4415018.html.txt","Introduction","avoids immortalization, yet transiently increases telomerase activity, rapidly extends telomeres, delays expression of senescence markers, and increases proliferative capacity"),
]
src_cache = {}
out = []
for pmid, f, sec, q in Q:
    if pmid not in src_cache:
        src_cache[pmid] = re.sub(r"\s+", " ", open(T+pmid+".txt", encoding="utf-8").read())
    ok = q in src_cache[pmid]
    out.append((pmid, f, sec, q, "PASS" if ok else "FAIL"))
for r in out: print(r[4], r[0], r[1], "|", r[3][:90])
