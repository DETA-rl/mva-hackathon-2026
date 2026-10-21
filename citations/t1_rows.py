# Rows for LIT_CHECK.tsv. Each quote is checked by normalised substring match against the stored source text.
import json, re, xml.etree.ElementTree as ET
BASE = "/private/tmp/[redacted]/scratchpad/t1/citations/"
A = json.load(open(BASE + "abstracts.json"))
pmc = re.sub(r"\s+", " ", " ".join(" ".join(x.itertext()) for x in ET.parse(BASE + "pmc_toledano.xml").getroot().iter() if x.tag in ("p", "title", "abstract")))
A["PMC11387191"] = pmc
for pid,f in [("39174735","39174735.xml")]:
    for a in ET.parse(BASE+f).getroot().findall("PubmedArticle"):
        art=a.find("MedlineCitation/Article")
        A[pid]=" ".join("".join(x.itertext()) for x in art.findall("Abstract/AbstractText"))
def norm(s): return re.sub(r"\s+", " ", s).strip()
def check(pid, quote):
    if not quote: return "NA"
    return "PASS" if norm(quote) in norm(A[pid]) else "FAIL"

ROWS = [
 dict(line="92", claim="Hanks 2004: truncating and missense BUB1B mutations in MVA families, two with embryonal RMS",
      pmid="15475955", pm="yes", src="15475955",
      quote="In five families with mosaic variegated aneuploidy, including two with embryonal rhabdomyosarcoma, we identified truncating and missense mutations of BUB1B",
      verdict="SUPPORTED", action="None. Hanks S, 2004, Nat Genet, title matches."),
 dict(line="92", claim="Ochiai 2014: second-allele upstream variant (rs576524605, chr15:40117088, ref at 45 reads) absent in child",
      pmid="24344301", pm="yes", src="24344301",
      quote="A unique single nucleotide substitution, G > A at ss802470619, was identified in an intergenic region 44 kb upstream of a BUB1B transcription start site",
      verdict="PARTLY", action="Paper names ss802470619, not rs576524605. Identity is inferred by position: dbSNP rs576524605 is G>A at GRCh38 chr15:40117088 (GRCh37 40409289), 43.9 kb upstream of the BUB1B TSS of ENST00000287598 (GRCh37 40453227). Say so in the text, or resolve ss802470619 in dbSNP and cite it. Absence at this site is a read-level fact and stands."),
 dict(line="92", claim="...so the second allele must be coding",
      pmid="24344301", pm="yes", src="24344301",
      quote="No second mutation was found in the opposite allele of any of the families studied",
      verdict="NOT SUPPORTED", action="Delete 'must be coding'. Excluding one upstream variant does not establish a coding second allele; noncoding, structural or other second alleles remain open. Also the paper calls its variant 'suggested ... causal', so write 'reported as causal' rather than 'the causal variant'."),
 dict(line="62", claim="Readthrough of a TGA stop is drug- and context-dependent",
      pmid="39174735", pm="yes", src="39174735",
      quote="We find that different drugs promote the readthrough of complementary subsets of PTCs defined by local sequence context.",
      quote2=("PMC11387191","most drugs increasing the readthrough of UGA more effectively than UAG and UAA PTCs"),
      verdict="SUPPORTED", action="None required. Optional: add the full-text TGA sentence from PMC11387191: 'most drugs increasing the readthrough of UGA more effectively than UAG and UAA PTCs'. The study is reporter assays in HEK293T cells, not the child; keep the claim at that level."),
 dict(line="62", claim="Under the standard rule, a premature stop more than ~50 nt upstream of the last exon-exon junction triggers NMD",
      pmid="none (candidate 9644970: Nagy E 1998, Trends Biochem Sci, 'A rule for termination-codon position within intron-containing genes')", pm="title only", src=None,
      quote="", verdict="NOT CHECKABLE", action="PubMed record for 9644970 has no abstract, so the 50-nt threshold cannot be quoted. Get the full text, check the threshold, and cite 9644970 with the number as stated there. If the full text is unavailable, cite the rule without the number."),
 dict(line="66", claim="'The field converged on BUB1B'",
      pmid="none", pm="no", src="32861809",
      quote="Three genes, BUB1B, CEP57 and TRIP13, are involved in this syndrome.",
      verdict="UNSOURCED", action="No source for 'converged'. The literature names three genes (32861809; also 31738183: 'biallelic BUBR1, CEP57, or TRIP13 aberrations'), and some MVA is 'of unknown cause' (28553959). Replace with a cited statement or delete."),
 dict(line="9", claim="'The disease name and the literature point to the MVA gene set'",
      pmid="none -> proposed 24259107, 31738183", pm="yes", src="24259107",
      quote="Mutations in BUB1B and CEP57 genes, which are involved in mitotic spindle and microtubule stabilization, respectively, are responsible for a subset of patients with MVA.",
      verdict="PROPOSED (supported)", action="Add [24259107] and [31738183] (quote in 31738183: 'characterized by biallelic BUBR1, CEP57, or TRIP13 aberrations'). Use the same three-gene core in the text."),
 dict(line="24", claim="CEP57 c.915_925dup11 is a reported MVA allele (table row; draft gives no source)",
      pmid="none -> proposed 24259107", pm="yes", src="24259107",
      quote="We report on a girl with this disorder due to c.915-925dup11 mutation in CEP57",
      verdict="PROPOSED (supported)", action="If the row presents this as a known MVA allele, cite 24259107. Paper writes c.915-925dup11 (hyphen); keep one notation and note the match was by allele definition."),
 dict(line="32", claim="Second-tier MVA genes: SMC5, SLF2, MAD1L1, CENATAC, TRIM37, MAD2L1BP, CEP192, CDC20",
      pmid="none -> per-gene: SMC5 41374403; CEP192 37981762; MAD1L1 36322655; MAD2L1BP 37796616; TRIM37 41702694; CDC20 33094908 (aneuploidy only)", pm="yes (6 of 8)", src="36322655",
      quote="These data point to MAD1L1 mutations as the cause of a new variant of mosaic variegated aneuploidy with systemic inflammation and unprecedented tumor susceptibility.",
      verdict="PARTLY", action="Cite per gene only where the abstract supports the MVA link: SMC5 (41374403, 'confirming its association with MVA/near-tetraploidy'), CEP192 (37981762), MAD1L1 (36322655). TRIM37 (41702694): 'we observed mosaic variegated aneuploidies' in Mulibrey nanism siblings, so cite for the phenotype overlap, not as an MVA gene. MAD2L1BP (37796616): abstract links it to 'aneuploidy and tumor predisposition' with no MVA label, so PARTLY. CDC20 (33094908) reports random aneuploidy in a premature-aging case, not MVA. No paper found linking SLF2 or CENATAC to MVA: label them as database candidates or remove."),
 dict(line="none (not in draft)", claim="radford2022: BUB1B mRNA rescue in early embryo cleavage (ledger entry only)",
      pmid="none", pm="no", src=None, quote="", verdict="NOT FOUND",
      action="PubMed: radford[au] AND BUB1B = 0 hits; BUB1B AND mRNA AND embryo AND cleavage AND 2022 = 0 hits. Crossref query (author Radford, BUB1B embryo, 2021-2023) returned no items. Remove radford2022 from refs/refs.json and refs/REFERENCES.md (and drop from the public copy per t2/audit/AUDIT.md). Do not cite."),
 dict(line="none", claim="Alu / mobile-element precedent", pmid="none", pm="NA", src=None, quote="",
      verdict="NA", action="No such sentence in the draft. Nothing to check. If one is added, it needs a source."),
 # [redacted]: lines that cite the authors' internal research notes are not reproduced
 # [redacted]
]
