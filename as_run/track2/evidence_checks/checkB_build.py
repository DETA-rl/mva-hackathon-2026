import re, csv, io, sys, xml.etree.ElementTree as ET
BASE = "/private/tmp/[redacted]/scratchpad/t2/evidence"
RAW = BASE + "/checkB_raw/"

def norm(s):
    return " ".join(s.split())

def abstract_corpus(path):
    root = ET.parse(path).getroot()
    parts = []
    for art in root.iter('PubmedArticle'):
        t = art.find('.//ArticleTitle')
        if t is not None:
            parts.append(("Title", ''.join(t.itertext())))
        for ab in art.iter('AbstractText'):
            parts.append(("Abstract", ''.join(ab.itertext())))
    return parts

def pmc_corpus(path):
    # paragraphs written by pmc_text.py as "[section] text"
    parts = []
    for line in open(path).read().split('\n'):
        m = re.match(r'\[(.*?)\] (.*)', line)
        if m:
            parts.append(('Abstract (PMC copy)' if m.group(1) == 'article' else m.group(1), m.group(2)))
    return parts

CORPORA = {
    "26748241_abs": abstract_corpus(RAW + "pubmed_26748241.xml"),
    "31513481_abs": abstract_corpus(RAW + "pubmed_31513481.xml"),
    "31738183_abs": abstract_corpus(RAW + "pubmed_31738183.xml"),
    "32251383_pmc": pmc_corpus(RAW + "PMC7735425.txt"),
    "33505027_pmc": pmc_corpus(RAW + "PMC7889737.txt"),
    "35141499_pmc": pmc_corpus(RAW + "PMC8814761.txt"),
    "27374329_pmc": pmc_corpus(RAW + "PMC5560052.txt"),
    "29067790_abs": abstract_corpus(RAW + "pubmed_29067790.xml"),
    "31501599_abs": abstract_corpus(RAW + "pubmed_31501599.xml"),
    "32251383_abs": abstract_corpus(RAW + "pubmed_32251383.xml"),
    "33505027_abs": abstract_corpus(RAW + "pubmed_33505027.xml"),
    "35141499_abs": abstract_corpus(RAW + "pubmed_35141499.xml"),
    "27374329_abs": abstract_corpus(RAW + "pubmed_27374329.xml"),
    "31184400_title": abstract_corpus(RAW + "pubmed_31184400.xml"),
}

# (corpus, quote)
Q = {
 "26748241_title": ("26748241_abs", "mTOR inhibitor temsirolimus and MEK1/2 inhibitor U0126 promote chromosomal instability and cell type-dependent phenotype changes of glioblastoma cells."),
 "26748241_abs1": ("26748241_abs", "TEM significantly increased clonal and non-clonal chromosome aberrations."),
 "27374329_a": ("27374329_pmc", "MAD2 directly binds to IR and facilitates BUBR1-dependent recruitment of the clathrin adaptor AP2 to IR."),
 "27374329_b": ("27374329_pmc", "p31comet blocks the MAD2–BUBR1 interaction and prevents spontaneous clathrin-mediated IR endocytosis."),
 "27374329_c": ("27374329_pmc", "BUBR1 deficiency enhances insulin sensitivity in mice."),
 "27374329_d": ("27374329_pmc", "Liver-specific ablation of p31comet causes insulin resistance, hyperinsulinemia, glucose intolerance, and hyperglycemia, and diminishes the plasma membrane localization of insulin receptor (IR) in hepatocytes."),
 "29067790_a": ("29067790_abs", "Sirt2-dependent BubR1 deacetylation involves in the regulation of meiotic apparatus in normal oocytes and mediates the effects of advanced maternal age on oocyte quality."),
 "29067790_b": ("29067790_abs", "Importantly, BubR1-K243R overexpression in oocytes derived from aged mice markedly suppresses spindle/chromosome anomalies and thereupon lowers the incidence of aneuploid eggs."),
 "31184400_title": ("31184400_title", "Rhabdomyosarcoma with premature chromatid separation-mosaic variegated aneuploidy syndrome: Reduced-intensity chemotherapy."),
 "31501599_a": ("31501599_abs", "lentiviral-mediated hematopoietic gene therapy reproducibly confers engraftment and proliferation advantages of gene-corrected hematopoietic stem cells (HSCs) in non-conditioned patients with FA subtype A."),
 "31501599_b": ("31501599_abs", "The progressive engraftment of corrected HSCs in non-conditioned patients with FA supports that gene therapy should constitute an innovative low-toxicity therapeutic option for this life-threatening disorder."),
 "31513481_a": ("31513481_abs", "Eighty-seven of 100 planned patients were enrolled"),
 "31513481_b": ("31513481_abs", "The 6-month EFS for the bevacizumab arm was 54.6% (95% CI, 39.8% to 69.3%) and 69.1% (95% CI, 55.1% to 83%) for the temsirolimus arm."),
 "31513481_c": ("31513481_abs", "Patients who received temsirolimus had a superior EFS compared with bevacizumab."),
 "31513481_d": ("31513481_abs", "with an observed two-sided P value of .003 favoring temsirolimus"),
 "31738183_title": ("31738183_abs", "BubR1 allelic effects drive phenotypic heterogeneity in mosaic-variegated aneuploidy progeria syndrome."),
 "31738183_b": ("31738183_abs", "we mimicked the BUBR1L1012P mutation in mice (BubR1L1002P) and combined it with 2 other MVA variants, BUBR1X753 and BUBR1H, generating a truncated protein and low amounts of wild-type protein, respectively."),
 "31738183_c": ("31738183_abs", "Together, these data demonstrate that BUBR1 allelic effects beyond protein level and aneuploidy contribute to disease heterogeneity"),
 "32251383_a": ("32251383_abs", "multiple classes of lipid nanoparticles are systematically engineered to exclusively edit extrahepatic tissues via addition of a supplemental SORT molecule."),
 "32251383_b": ("32251383_abs", "Lung-, spleen- and liver-targeted SORT lipid nanoparticles were designed to selectively edit therapeutically relevant cell types"),
 "33505027_a": ("33505027_abs", "We also identify KIF18A, which encodes a mitotic kinesin protein, as being specifically required for the viability of WGD+ cells."),
 "33505027_b": ("33505027_pmc", "inhibition of the SAC using the small molecule inhibitor AZ3146"),
 "35141499_a": ("35141499_abs", "This mitotic slippage caused chromosome instability."),
 "35141499_b": ("35141499_pmc", "We found that mTORC1 inhibition also elicits mitotic slippage in human cells."),
 "35141499_c": ("35141499_pmc", "Rapamycin treatment promotes chromosome instability in yeast and mammalian cells"),
}

# draft rows: (pmid, line, source_used, quote keys, verdict, note)
ROWS = [
 ("26748241", "137", "abstract (PMID 26748241 has no PMCID; title and abstract checked)", ["26748241_title","26748241_abs1"], "NOT SUPPORTED",
  "Single-agent CIN is supported: TEM alone and U0126 alone promoted chromosome aberrations in U251/T98G glioblastoma cells. The paper tests the drugs in separate arms and reports no combination arm (no 'combin' in record), so the draft's claim of a combination effect is not supported as written. The draft's rejection argument leans on this sentence, so it needs rewording."),
 ("27374329", "92", "fulltext PMC (PMC5560052); quotes sit in its abstract", ["27374329_a","27374329_d","27374329_c"], "SUPPORTED",
  "Paper: MAD2 binds IR and facilitates BUBR1-dependent AP2 recruitment; p31comet prevents clathrin-mediated IR endocytosis; liver/hepatocyte data; BUBR1 deficiency enhances insulin sensitivity in mice. Draft's 'may' hedging is appropriate. Cited sentence's first PMID (37725942) is not in my scope."),
 ("29067790", "42", "abstract (PMC full text fetched; quotes taken from abstract)", ["29067790_a","29067790_b"], "SUPPORTED",
  "Paper's own wording is 'mediates the effects of advanced maternal age on oocyte quality'; the aneuploidy link rests on K243R overexpression lowering aneuploid-egg incidence in aged oocytes. Draft's 'mouse oocyte evidence only' is consistent with the paper. Note paper's site is BubR1 K243 (not K250)."),
 ("29067790", "72", "abstract (PMC full text fetched; quotes taken from abstract)", ["29067790_a","29067790_b"], "SUPPORTED",
  "Same paper as line 42. Only the 29067790 part of the Basis sentence is checked here; the NMN and threshold parts belong to 24825348 and 18932004."),
 ("31184400", "33", "title only (no abstract in PubMed record; no PMCID)", ["31184400_title"], "PARTLY",
  "Title supports an RMS case series/report in PCS-MVA treated with reduced-intensity chemotherapy. The word 'case' (number of patients) and treatment details cannot be checked from the title alone."),
 ("31501599", "181", "abstract (no PMCID)", ["31501599_a","31501599_b"], "SUPPORTED",
  "Qualitative engraftment claim supported. Population is FA subtype A patients, not MVA; the draft says it is cited only for the qualitative finding, which matches."),
 ("31513481", "137", "abstract (PMC record has abstract only, no body)", ["31513481_a","31513481_b","31513481_c","31513481_d"], "PARTLY",
  "87 patients (Eighty-seven of 100 planned) and EFS 69.1% vs 54.6% are correct, but the comparator is the bevacizumab + chemo arm, not chemo alone; the draft omits this. 'A small signal' understates the paper, which reports P=.003 favoring temsirolimus and calls temsirolimus 'superior'."),
 ("31738183", "31", "abstract (PMC record has abstract only, no body)", ["31738183_title","31738183_b"], "PARTLY",
  "'Allelic effects drive phenotypic heterogeneity' matches the title. 'Reproduces the MVA genotype' overstates it: the mice carry a mimic of one MVA variant combined with two other MVA variants. The abstract says allelic effects 'contribute to' heterogeneity; the title says 'drive'."),
 ("32251383", "85", "fulltext PMC (PMC7735425); quotes from abstract", ["32251383_a"], "SUPPORTED",
  "Paper engineers SORT LNPs for organ-selective (lung, spleen, liver) editing. Supports 'can be tuned to target particular organs'."),
 ("32251383", "179", "fulltext PMC (PMC7735425); quotes from abstract", ["32251383_a","32251383_b"], "SUPPORTED",
  "Supports that targeting depends on particle design. The mechanism in this paper is an added SORT molecule, not PEG-lipid tail chemistry (that claim is from PMID 42489054, not mine)."),
 ("33505027", "43", "fulltext PMC (PMC7889737)", ["33505027_a","33505027_b"], "PARTLY",
  "KIF18A claim supported by abstract. The second sentence is inaccurate as written: the source does name inhibitors (AZ3146 Mps1 inhibitor, MG132 proteasome inhibitor, RRM1 inhibitors), but none for KIF18A. Reword to 'no KIF18A inhibitor is named'."),
 ("35141499", "137", "fulltext PMC (PMC8814761)", ["35141499_a","35141499_b","35141499_c"], "PARTLY",
  "Mitotic slippage in yeast and human cells is supported. CIN is shown only in yeast (SUP11 mini-chromosome assay); human cells show mitotic slippage, not CIN. The paper's CIN statement for mammalian cells cites prior work (Bonatti 1998; Choi 2000), not its own data."),
]

def run():
    rows = []
    for pmid, line, src, keys, verdict, note in ROWS:
        quotes, sections, checks = [], [], []
        for k in keys:
            corp_key, q = Q[k]
            corpus = CORPORA[corp_key]
            hit = None
            for sec, txt in corpus:
                if q in norm(txt):
                    hit = sec
                    break
            ok = hit is not None
            checks.append(ok)
            sections.append(hit if ok else "NOT FOUND")
            quotes.append(q)
            if not ok:
                print("FAIL", pmid, line, k, file=sys.stderr)
        vc = "PASS" if all(checks) else "FAIL"
        rows.append([pmid, line, src, " || ".join(sections), " || ".join(quotes), vc, verdict, note])
    return rows

if __name__ == "__main__":
    rows = run()
    for r in rows:
        assert all("\t" not in f for f in r)
    out = BASE + "/checkB.tsv"
    with open(out, "w") as f:
        f.write("pmid\tdraft_line\tsource_used\tsection\tverbatim_quote\tverbatim_check\tverdict\tnote\n")
        for r in rows:
            f.write("\t".join(x.replace("\n"," ") for x in r) + "\n")
    for r in rows:
        print(r[0], r[1], r[5], r[6], r[3])
