"""C3/C5 mechanism queries for eval_B4b. Gene symbols, drug names, mechanism terms and PMIDs
only. esearch then efetch of titles and abstracts; abstracts truncated on print."""
import json, re, time, urllib.parse, urllib.request
OUT="/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
Q={
"gent_readthrough":"(gentamicin[tiab]) AND (readthrough[tiab] OR read-through[tiab]) AND (nonsense[tiab] OR premature termination[tiab])",
"bub1b_readthrough":"(BUB1B[tiab] OR BubR1[tiab]) AND (readthrough[tiab] OR read-through[tiab] OR nonsense suppression[tiab])",
"metformin_bubr1":"metformin[tiab] AND (BubR1[tiab] OR BUB1B[tiab] OR spindle assembly checkpoint[tiab])",
"hesperidin_mitosis":"hesperidin[tiab] AND (aurora[tiab] OR BubR1[tiab] OR spindle[tiab] OR mitotic[tiab])",
"fasudil_aurora":"fasudil[tiab] AND (aurora[tiab] OR mitotic[tiab] OR spindle[tiab])",
"etoposide_aneu":"etoposide[tiab] AND (aneuploidy[tiab] OR micronucleus[tiab] OR chromosome missegregation[tiab])",
"mitomycin_aneu":"mitomycin[tiab] AND (aneuploidy[tiab] OR micronuclei[tiab] OR chromosome aberration[tiab])",
"griseofulvin_aneu":"griseofulvin[tiab] AND (aneuploidy[tiab] OR micronucle*[tiab] OR spindle[tiab])",
"bubr1_lowered_by_drug":"(BubR1[tiab] OR BUB1B[tiab]) AND (downregulat*[tiab] OR degradation[tiab]) AND (chemotherapy[tiab] OR cisplatin[tiab] OR etoposide[tiab] OR doxorubicin[tiab])",
}
def esearch(q,n=8):
    u="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=%d&term=%s"%(n,urllib.parse.quote(q))
    with urllib.request.urlopen(u,timeout=60) as r: d=json.load(r)
    return d["esearchresult"]["count"], d["esearchresult"]["idlist"]
def efetch(ids):
    u="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="+",".join(ids)
    with urllib.request.urlopen(u,timeout=90) as r: return r.read().decode("utf-8","replace")
store={}
for k,q in Q.items():
    cnt,ids=esearch(q)
    print("\n===== %s | count=%s | %s"%(k,cnt,",".join(ids)))
    store[k]={"query":q,"count":cnt,"ids":ids,"records":{}}
    if ids:
        xml=efetch(ids)
        for art in xml.split("<PubmedArticle>")[1:]:
            pid=re.search(r"<PMID[^>]*>(\d+)</PMID>",art)
            ti=re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>",art,re.S)
            abs_=" ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>",art,re.S))
            yr=re.search(r"<Year>(\d{4})</Year>",art)
            clean=lambda s: re.sub(r"<[^>]+>","",s).replace("\n"," ").strip() if s else ""
            pid=pid.group(1) if pid else "?"
            store[k]["records"][pid]={"year":yr.group(1) if yr else "","title":clean(ti.group(1) if ti else ""),"abstract":clean(abs_)}
            print("- %s (%s) %s"%(pid,store[k]["records"][pid]["year"],store[k]["records"][pid]["title"][:140]))
            print("   ABS: %s"%store[k]["records"][pid]["abstract"][:700])
    time.sleep(0.5)
with open(OUT+"lit_mech.json","w") as f: json.dump(store,f,indent=1)
