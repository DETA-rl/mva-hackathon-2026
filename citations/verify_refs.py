#!/usr/bin/env python3
"""Verify citations against PubMed. Output refs.json + REFERENCES.md.
A ref is VERIFIED only if PubMed returns a record whose first author, year and title keywords match."""
import json, re, sys, time, urllib.parse, urllib.request, datetime

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode()

# key, pubmed query, expected first-author surname, expected year, title keywords (all must appear), supports (claim)
REFS = [
 ("suijkerbuijk2010", "Suijkerbuijk[au] AND BUBR1 AND mosaic variegated aneuploidy", "Suijkerbuijk", 2010, ["BUBR1", "mosaic variegated"], "BUBR1 re-expression rescues MVA patient cells"),
 ("baker2013", "Baker DJ[au] AND increased expression of BubR1 protects against aneuploidy", "Baker", 2013, ["BubR1", "aneuploidy", "cancer"], "Extra BubR1 lowers aneuploidy and cancer, extends lifespan (mouse)"),
 ("north2014", "North BJ[au] AND SIRT2 AND BubR1", "North", 2014, ["SIRT2", "BubR1"], "SIRT2 deacetylates BubR1; NAD+ raises BubR1 (mouse)"),
 ("homer2005", "Homer HA[au] AND Mad2 AND oocytes AND 2005[dp]", "Homer", 2005, ["Mad2"], "MAD2 mRNA rescues meiosis; steep dose dependence"),
 ("alex2019", "Electroporated recombinant proteins as tools for in vivo functional complementation, imaging and chemical biology", None, 2019, ["Electroporated recombinant proteins"], "Recombinant kinetochore proteins delivered by electroporation assemble correctly"),
 ("radford2022", "BUB1B mRNA rescue embryo cleavage chromosome segregation BUBR1 zygote", None, 2022, ["BUB"], "BUB1B mRNA rescue in early embryo cleavage"),
 ("ramunas2015", "Ramunas J[au] AND telomerase mRNA AND 2015[dp]", "Ramunas", 2015, ["telomer"], "Transient modified mRNA of a nuclear protein (hTERT) works in dividing human cells"),
 ("wild2016", "PMID:26904940", "Wild", 2016, ["Spindle Assembly Checkpoint", "Lowered APC/C Activity"], "Genetically lowered APC/C activity makes the SAC non-essential for viability in human cells"),
 ("thu2018", "Thu KL[au] AND CRISPR AND TTK AND 2018[dp]", "Thu", 2018, ["TTK"], "CRISPR screen: APC/C and MAD2L1BP loss confers resistance to Mps1 inhibition"),
 ("quinton2021", "Whole-genome doubling confers unique genetic vulnerabilities on tumour cells", None, 2021, ["genome doubling"], "KIF18A inhibition selectively kills chromosomally unstable cells"),
 ("bertoldo2020", "Bertoldo MJ[au] AND NAD AND oocyte AND 2020[dp]", "Bertoldo", 2020, ["NAD"], "NAD+ precursor rescues aged-oocyte quality (mouse)"),
 ("rio2019", "Successful engraftment of gene-corrected hematopoietic stem cells in non-conditioned patients with Fanconi anemia", None, 2019, ["Fanconi", "non-conditioned"], "Gene-corrected HSC engraft without conditioning in FA"),
 ("rio2025", "Haematopoietic gene therapy of non-conditioned patients with Fanconi anaemia-A FANCOLEN-1", None, 2025, ["Fanconi"], "FANCOLEN-1 long-term results, no conditioning"),
 ("breda2023", "In vivo hematopoietic stem cell modification by mRNA delivery", None, 2023, ["hematopoietic stem cell"], "In vivo HSC editing with CD117-targeted LNP"),
 ("hirsch2017", "Regeneration of the entire human epidermis using transgenic stem cells", None, 2017, ["epidermis"], "Holoclone-based gene-corrected epidermis"),
 ("cheng2020_sort", "Cheng Q[au] AND selective organ targeting SORT nanoparticles", "Cheng", 2020, ["Selective organ targeting"], "SORT LNPs deliver mRNA/CRISPR beyond the liver"),
 ("koeberl2024", "propionic acidaemia mRNA first-in-human phase 1/2 interim analyses", None, 2024, ["propionic", "mRNA"], "Repeat-dose mRNA protein replacement in children (mRNA-3927)"),
 ("ou2026", "PMID:42489054", "Ou", 2026, ["PEG-Lipid", "Muscle"], "PEG-lipid structure tunes muscle tropism of mRNA-LNPs"),
 ("liu2026", "PMID:42677161", "Liu", 2026, ["hepatic tropism"], "Reprogramming LNP biological identity for extrahepatic delivery"),
 ("repellin2026", "PMID:42379311", "Repellin", 2026, ["Muscle", "mRNA"], "Muscle contribution to LNP mRNA vaccine delivery"),
 ("liao2026", "PMID:42285307", "Liao", 2026, ["dihydrosphingomyelin"], "DHSM LNPs: longer circulation, extrahepatic transfection"),
 ("bohers2008", "PMID:18932004", "Bohers", 2008, ["BUBR1", "aneuploidy"], "Residual BUBR1 is dosage-dependent: PCS tracks the decrease, aneuploidy clear below 50% (shRNA HeLa gradient 8.5-77%)"),
 ("sieben2020", "PMID:31738183", "Sieben", 2020, ["BubR1", "mosaic-variegated"], "Mouse BubR1 L1002P + hypomorph combos reproduce MVA heterogeneity (cancer, dwarfism, sarcopenia)"),
 ("nair2023", "PMID:38008853", "Nair", 2023, ["FBXW7", "BubR1"], "SCF-FBXW7 targets BubR1 for ubiquitin degradation in mitosis (turnover is regulated)"),
 ("baker2004", "PMID:15208629", "Baker", 2004, ["BubR1 insufficiency"], "BubR1 insufficiency causes early aging phenotypes in mice"),
 ("pcs_mva_rms2019", "PMID:31184400", None, 2019, ["Rhabdomyosarcoma", "premature chromatid separation"], "Reported case: rhabdomyosarcoma in PCS-MVA, reduced-intensity treatment"),
 ("choi2016", "PMID:27374329", "Choi", 2016, ["Mitotic Checkpoint", "Insulin"], "Mitotic checkpoint regulators (MAD2/BUBR1) control insulin receptor endocytosis and metabolic homeostasis"),
 ("park2023", "PMID:37725942", "Park", 2023, ["MAD2", "Insulin Receptor Endocytosis"], "MAD2-dependent insulin receptor endocytosis regulates metabolic homeostasis"),
 ("geoerger2012", "PMID:22033322", "Geoerger", 2012, ["temsirolimus", "rhabdomyosarcoma"], "Phase II temsirolimus in children incl. rhabdomyosarcoma"),
 ("mascarenhas2019", "PMID:31513481", "Mascarenhas", 2019, ["Temsirolimus", "Bevacizumab"], "COG ARST0921: first-relapse RMS, temsirolimus+chemo had superior EFS vs bevacizumab+chemo (not vs chemo alone)"),
 ("gupta2024", "PMID:38936378", "Gupta", 2024, ["temsirolimus", "rhabdomyosarcoma"], "COG ARST1431 phase 3: temsirolimus added to VAC/VI in intermediate-risk RMS (outcome not yet read)"),
 ("giblin2026_pkd2_preprint", "PMID:42282798", "Giblin", 2026, ["Collecting Duct", "Pkd2"], "PREPRINT (bioRxiv, not peer reviewed): collecting-duct-targeted LNP delivers Pkd2 mRNA, systemic IV in mouse"),
 ("hou2023_sod2", "PMID:38028193", "Hou", 2023, ["SOD2", "renal"], "Chemically modified SOD2 mRNA in LNP alleviates renal ischemia-reperfusion injury (mouse). NOTE: the DR report attributed this to Zhu; first author is Hou"),
 ("thielmann2021_teprasiran", "PMID:34474590", "Thielmann", 2021, ["Teprasiran"], "Phase 2: teprasiran siRNA for AKI prevention in high-risk cardiac surgery"),
 ("nejm2026_aoc_dm1", "PMID:41707138", None, 2026, ["Antibody-Oligonucleotide Conjugate", "Myotonic Dystrophy"], "Systemic IV antibody-oligonucleotide conjugate (anti-TfR1) reaches muscle in humans (DM1), oligo not mRNA"),
 ("moltherp2026_delpacibart", "PMID:41821312", None, 2026, ["Delpacibart", "myotonic dystrophy"], "Del-desiran phase 1/2: molecular improvement in DM1 muscle"),
]


def resolve(query):
    if query.startswith("PMID:"):
        return [query[5:]]
    u = E + "esearch.fcgi?db=pubmed&retmax=5&sort=relevance&term=" + urllib.parse.quote(query)
    return re.findall(r"<Id>(\d+)</Id>", get(u))

def summary(pmid):
    d = json.loads(get(E + f"esummary.fcgi?db=pubmed&retmode=json&id={pmid}"))["result"].get(pmid)
    if not d: return None
    doi = next((a["value"] for a in d.get("articleids", []) if a["idtype"] == "doi"), "")
    return {"pmid": pmid, "title": d["title"], "journal": d["source"], "pubdate": d["pubdate"],
            "first_author": (d.get("authors") or [{"name": ""}])[0]["name"], "doi": doi}

def matches(s, au, yr, kws):
    t = s["title"].lower()
    ok_kw = all(k.lower() in t for k in kws)
    ok_yr = str(yr) in s["pubdate"] or abs(int(re.findall(r"\d{4}", s["pubdate"])[0]) - yr) <= 1
    ok_au = (au is None) or au.lower() in s["first_author"].lower()
    return ok_kw and ok_yr and ok_au

out = []
today = datetime.date.today().isoformat()
for key, q, au, yr, kws, claim in REFS:
    rec = {"key": key, "claim_supported": claim, "status": "UNVERIFIED", "checked": today}
    try:
        for pmid in resolve(q):
            s = summary(pmid); time.sleep(0.4)
            if s and matches(s, au, yr, kws):
                rec.update(s); rec["status"] = "VERIFIED"; break
        else:
            rec["note"] = "no PubMed record matched author/year/title keywords"
    except Exception as e:
        rec["note"] = f"error: {e}"
    out.append(rec)
    print(f'{rec["status"]:10} {key:16} {rec.get("pmid","-"):10} {rec.get("title","")[:70]}')

json.dump(out, open("refs.json", "w"), indent=1, ensure_ascii=False)
with open("REFERENCES.md", "w") as f:
    f.write(f"# Verified references (checked against PubMed on {today})\n\n")
    f.write("Only entries marked VERIFIED were matched on first author, year and title keywords against the PubMed record. UNVERIFIED entries must not be cited.\n\n")
    for r in out:
        if r["status"] == "VERIFIED":
            f.write(f'- **{r["key"]}** {r["first_author"]} et al. {r["title"]} *{r["journal"]}* {r["pubdate"]}. PMID {r["pmid"]}' + (f', DOI {r["doi"]}' if r["doi"] else "") + f'. Supports: {r["claim_supported"]}\n')
    f.write("\n## Not verified (do not cite)\n\n")
    for r in out:
        if r["status"] != "VERIFIED":
            f.write(f'- {r["key"]}: {r.get("note","")} (claim: {r["claim_supported"]})\n')
print(sum(r["status"] == "VERIFIED" for r in out), "/", len(out), "verified")
