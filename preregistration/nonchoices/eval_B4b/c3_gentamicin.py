"""C3 for the one mechanistically on-point arm in items 50-98: aminoglycoside readthrough of a
premature termination codon. Label pharmacokinetics by drug name from openFDA; readthrough
concentrations from the primary records. Drug names and PMIDs only."""
import json, re, urllib.parse, urllib.request
OUT="/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
def get(u):
    try:
        with urllib.request.urlopen(u,timeout=60) as r: return r.read().decode("utf-8","replace")
    except Exception as e: return "__ERR__"+str(e)
# 1. label PK text for gentamicin injection
d=get("https://api.fda.gov/drug/label.json?search=openfda.generic_name:%22gentamicin%22+AND+openfda.route:%22INTRAVENOUS%22&limit=3")
pk=[]
if not d.startswith("__ERR__"):
    j=json.loads(d)
    for r in j.get("results",[]):
        for f in ("clinical_pharmacology","pharmacokinetics","description","dosage_and_administration"):
            for t in r.get(f,[]):
                for m in re.finditer(r"[^.]*(peak|protein bind|serum concentration|mcg/mL|microgram)[^.]*\.", t, re.I):
                    s=m.group(0).strip()
                    if len(s)<400: pk.append(f+": "+s)
pk=list(dict.fromkeys(pk))[:14]
print("=== gentamicin label PK sentences (openFDA label, IV route) ===")
for s in pk: print("-",s)
# 2. readthrough concentration numbers from primary records
ids=["40342992","41210582","42504002"]
xml=get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="+",".join(ids))
print("\n=== readthrough records, sentences carrying a concentration or dose ===")
recs={}
for art in xml.split("<PubmedArticle>")[1:]:
    pid=re.search(r"<PMID[^>]*>(\d+)</PMID>",art).group(1)
    ti=re.sub(r"<[^>]+>","",re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>",art,re.S).group(1))
    ab=re.sub(r"<[^>]+>","", " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>",art,re.S)))
    recs[pid]={"title":ti,"abstract":ab}
    print("\n--",pid,ti[:130])
    for m in re.finditer(r"[^.]*(mg/mL|ug/mL|mcg/mL|uM|microM|mM|mg/kg|concentration)[^.]*\.", ab, re.I):
        print("   *",m.group(0).strip()[:300])
json.dump({"label_pk":pk,"records":recs},open(OUT+"c3_gentamicin.json","w"),indent=1)
