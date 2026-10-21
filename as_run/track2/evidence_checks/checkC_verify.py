import re, csv, sys, xml.etree.ElementTree as ET
D = '/private/tmp/[redacted]/scratchpad/t2/evidence/checkC_src/'
OUT = '/private/tmp/[redacted]/scratchpad/t2/evidence/checkC.tsv'

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

def fulltext(fname):
    # Tags stripped two ways: inline-faithful (no space) and block-faithful (space).
    # A quote counts as found if it occurs in either variant.
    raw = open(D + fname, encoding='utf-8').read()
    body = re.sub(r'<!DOCTYPE[^>]*>', ' ', raw)
    import html
    a = norm(html.unescape(re.sub(r'<[^>]+>', '', body)))
    b = norm(html.unescape(re.sub(r'<[^>]+>', ' ', body)))
    return (a, b)

def found(q, texts):
    return any(norm(q) in t for t in texts)

# (pmid, draft_line, source_file, source_label, section, quote, verdict, note)
# A row may carry several quotes: list of (file, section, quote).
ROWS = [
 dict(pmid='37725942', line='92', src='PMC10658066.xml', source='abstract (PMC XML has abstract only, no body)',
  quotes=[('Abstract', 'Cell division regulators MAD2, BUBR1, and p31comet promote IR endocytosis on insulin stimulation.'),
          ('Abstract', 'Here, we show that genetic ablation of the IR-MAD2 interaction in mice delays IR endocytosis, increases IR levels, and prolongs insulin action at the cell surface.')],
  verdict='SUPPORTED',
  note='Mouse data. The second sentence of L92 (BUBR1 and clathrin endocytosis, BUBR1 deficiency and insulin sensitivity, PMID 27374329) is not in this list and was not checked.'),

 dict(pmid='38008853', line='40', src='PMC11072012.xml', source='abstract (PMC XML has abstract only, no body)',
  quotes=[('Abstract', 'Here, we show that E3 ubiquitin ligase, SCF-FBXW7 targets BubR1 for ubiquitin-mediated degradation and thereby controls SAC in human cells.')],
  verdict='SUPPORTED',
  note='Human cells, per abstract. The first sentence of L40 ("BUBR1 is actively regulated in mitosis") is uncited. The abstract supports it only loosely (Cdk1 phosphorylation signals the ligase). The lever sentence is marked hypothesis by the draft, so it is not a paper claim.'),

 dict(pmid='38570682', line='86', src='PMC11156579.xml', source='fulltext PMC (PMC11156579)',
  quotes=[('Abstract', 'Here we report interim analyses of a first-in-human, phase 1/2, open-label, dose-optimization study and an extension study evaluating the safety and efficacy of mRNA-3927, a dual mRNA therapy encoding PCCA and PCCB.'),
          ('Results', 'Across both studies, a total of 346 IV doses of mRNA-3927 were administered'),
          ('Participants', 'The median (range) age for all cohorts was 8.5 (1.3–26.8) years')],
  verdict='SUPPORTED',
  note='Repeat dosing (346 IV doses) and first-in-human are verbatim. "Children" is an approximation: participants were aged 1 year or older, with median 8.5 years and range 1.3 to 26.8. Propionic acidaemia is a different disease, as the draft says.'),

 dict(pmid='38570682', line='180', src='PMC11156579.xml', source='fulltext PMC (PMC11156579)',
  quotes=[('Discussion', 'So far, mRNA-3927 has been well tolerated in participants with PA at the doses administered, with no DLTs observed'),
          ('Results', 'Across both studies, a total of 346 IV doses of mRNA-3927 were administered')],
  verdict='SUPPORTED',
  note='The safety-precedent wording is supported. The same paper reports drug-related SAEs (including one grade 3 pancreatitis, judged related to PA) and infusion-related reactions, so "safety precedent" should not be read as a clean safety result. The "do not establish safety for BUBR1" conclusion is the draft\'s own inference.'),

 dict(pmid='37899683', line='182', src='pubmed_37899683.xml', source='abstract (no PMCID; PubMed abstract)',
  quotes=[('Methods', 'A single-arm, open-label clinical trial was performed in individuals with A-T, receiving NR over a period of 2 years.'),
          ('Methods', 'Using generalized mixed models, test results were compared to expected disease progression based on historical data.'),
          ('Results', 'NAD+ concentrations increased rapidly in peripheral blood and stabilized at a higher level than baseline.'),
          ('Results', 'The total scores in the neuromotor test panels, as evaluated at the 18-month time point, improved for all but one participant, primarily driven by improvements in coordination subscores and eye movements.'),
          ('Conclusions', 'Long-term use of NR appears to be safe and well tolerated, and it improves motor coordination and eye movements in patients with A-T of all ages.')],
  verdict='SUPPORTED',
  note='Single arm, 2 years, historical comparison, all ages, NAD+ up, 18-month neuromotor scores improved (all but one participant). The "all ages" wording comes from the conclusions. The draft\'s "not a checkpoint or aneuploidy endpoint" is a fair reading: the paper measures neuromotor scores and NAD+ only.'),

 dict(pmid='39387327', line='182', src='pubmed_39387327.xml', source='abstract (no PMCID; PubMed abstract)',
  quotes=[('Methods', 'This 6-week pilot feasibility 1:1 randomized controlled trial enrolled 20 CCS on a structured telehealth exercise program ± nicotinamide riboside (NR)'),
          ('Results', 'Median age (years) at cancer diagnosis was 16.5 (range, 1.5-21.5) and 35.5 (range, 18.0-67.0) at study enrollment.'),
          ('Results', 'There were no severe adverse events attributable to study interventions.')],
  verdict='SUPPORTED',
  note='Randomised pilot, n=20, median age 35.5 at enrollment (range 18 to 67), so all adults. The abstract reports feasibility and "no severe adverse events" (the draft says adverse events, which is accurate). The population is prediabetic childhood-cancer survivors, which fits "at risk for diabetes". The exercise plus or minus NR design is in Methods.'),

 dict(pmid='38936378', line='137', src='PMC11550893.xml', source='fulltext PMC (PMC11550893); title quote from PubMed record because the PMC XML title has no space after "children,"',
  quotes=[('Title', 'Addition of temsirolimus to chemotherapy in children, adolescents, and young adults with intermediate-risk rhabdomyosarcoma', 'pubmed_38936378.xml'),
          ('Results', 'The hazard ratio of Arm B vs Arm A is 0.86 (95% CI: (0.58, 1.26)).'),
          ('Results', 'At a median follow-up of 3.57 years (IQR 2.80 to 4.51 years), there was no statistically significant difference in EFS between Arm A and Arm B (3-year EFS was 64.8% (95% CI: (55.5%, 74.1%)) vs. 66.8% (95% CI: (57.5%, 76.2%)), log-rank p=0.44).')],
  verdict='SUPPORTED',
  note='HR 0.86, 95% CI 0.58 to 1.26 and log-rank p=0.44 all match the Results. Title wording covers children, adolescents and young adults (eligibility was up to age 40). The Results say no statistically significant difference, which is what "did not improve" means here. Not checked: whether a Lancet interpretation sentence was cited; it is not in this row.'),

 dict(pmid='39642902', line='180', src='pubmed_39642902.xml', source='abstract (no PMCID; PubMed abstract)',
  quotes=[('Methods', 'were transduced with a therapeutic FANCA-encoding lentiviral vector and re-infused without any cytotoxic conditioning treatment.'),
          ('Interpretation', 'These results show for the first time that haematopoietic gene therapy without genotoxic conditioning enables sustained engraftment and reversal of BMF progression in patients with Fanconi anaemia.')],
  verdict='SUPPORTED',
  note='Conditioning-free gene therapy in Fanconi anaemia-A, 9 treated and 8 evaluable. The primary endpoint was met in 5 of 8. Calling this "conditioning-free HSC work" is accurate.'),

 dict(pmid='40437086', line='180', src='PMC12286858.xml', source='fulltext PMC (PMC12286858)',
  quotes=[('Abstract', 'Here we demonstrate that in vivo gene delivery to HSPCs after systemic LV administration is enabled by the substantial trafficking of these cells from the liver to the bone marrow in newborn mice.'),
          ('Discussion', 'Here we show that the early postnatal period provides a unique opportunity to access HSCs in vivo for LV gene transfer in mice, bypassing the hurdles associated with ex vivo engineering.')],
  verdict='PARTLY',
  note='Trafficking is supported, but the work is mouse-only (newborn mice; ADA-SCID, Fanconi and other mouse models). "Corrected HSC trafficking" is a loose label: the paper is about in vivo gene transfer enabled by HSPC trafficking, not about correction as the object of study. Use as context is consistent with the draft.'),

 dict(pmid='42489054', line='85', src='PMC13580304.xml', source='abstract (PMC XML has abstract only, no body)',
  quotes=[('Abstract', 'By tuning PEG‐lipid tails and linkers, it achieves precise muscle targeting with 16.2‐fold enhanced expression in Ai9 mice')],
  verdict='PARTLY',
  note='The paper shows that tuning tail and linker together gives muscle targeting. It does not isolate a tail-only change, so "changing the PEG-lipid tail alters muscle tropism" overstates it. Mouse data (Ai9, RSV vaccine). Suggested fix: "tuning the PEG-lipid tail and linker alters muscle tropism".'),

 dict(pmid='42489054', line='179', src='PMC13580304.xml', source='abstract (PMC XML has abstract only, no body)',
  quotes=[('Abstract', 'By tuning PEG‐lipid tails and linkers, it achieves precise muscle targeting with 16.2‐fold enhanced expression in Ai9 mice')],
  verdict='SUPPORTED',
  note='General claim that tropism depends on PEG-lipid chemistry is supported. Tail and linker were varied together, which is why L85 is only partly supported.'),

 dict(pmid='42677161', line='85', src='PMC13528380.xml', source='fulltext PMC (PMC13528380, review)',
  quotes=[('Abstract', 'This review summarizes recent advances in delivery to the lungs, spleen, brain, heart, kidney, bone, and pancreas,')],
  verdict='SUPPORTED',
  note='This is a review. "Active area" is a paraphrase of "recent advances". The abstract also says extrahepatic targeting is a design problem with translational bottlenecks, which fits the draft. The quote is from the review\'s abstract.'),

 dict(pmid='42677161', line='179', src='PMC13528380.xml', source='fulltext PMC (PMC13528380, review)',
  quotes=[('Abstract', 'of LNPs must be reprogrammed by modifying the three interconnected factors of lipid composition, physicochemical properties and protein corona modulation.')],
  verdict='PARTLY',
  note='The review says targeting depends on lipid composition, physicochemical properties and protein corona. It does not say "chemistry" in the abstract, so "depends on its chemistry" is a close paraphrase, not verbatim. The "any in vivo work must start from a delivery test" conclusion is the draft\'s own recommendation and no cited paper states it.'),
]

def main():
    cache = {}
    results = []
    fails = 0
    for r in ROWS:
        if r['src'] not in cache:
            cache[r['src']] = fulltext(r['src'])
        text = cache[r['src']]
        checks = []
        for item in r['quotes']:
            sec, q = item[0], item[1]
            qtext = cache[item[2]] if len(item) > 2 and item[2] not in (None,) and item[2] != r['src'] and item[2] in cache else (
                fulltext(item[2]) if len(item) > 2 else text)
            if len(item) > 2:
                cache.setdefault(item[2], qtext)
            ok = found(q, qtext)
            checks.append(ok)
            if not ok:
                fails += 1
        verbatim = 'PASS' if all(checks) else 'FAIL'
        results.append(dict(
            pmid=r['pmid'], draft_line=r['line'], source_used=r['source'],
            section=' | '.join(item[0] for item in r['quotes']),
            verbatim_quote=' || '.join(item[1] for item in r['quotes']),
            verbatim_check=verbatim, verdict=r['verdict'], note=r['note'],
            _per=checks))
    cols = ['pmid', 'draft_line', 'source_used', 'section', 'verbatim_quote', 'verbatim_check', 'verdict', 'note']
    def clean(s):
        return s.replace('\t', ' ').replace('\n', ' ')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\t'.join(cols) + '\n')
        for row in results:
            f.write('\t'.join(clean(str(row[c])) for c in cols) + '\n')
    from collections import Counter
    print('rows', len(results))
    print('verdicts', Counter(r['verdict'] for r in results))
    print('verbatim', Counter(r['verbatim_check'] for r in results))
    for row in results:
        if row['verbatim_check'] == 'FAIL':
            print('FAIL', row['pmid'], row['draft_line'], row['_per'])
    print('per-quote results:')
    for row in results:
        print(row['pmid'], row['draft_line'], row['_per'])

main()
