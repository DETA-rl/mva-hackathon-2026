"""C3 direction evidence, one primary source per mechanism class present in Batch 4 items
50-98. Prints only sentences that carry both a class term and a chromosome or checkpoint
endpoint, to keep the record compact. Drug names, gene symbols and PMIDs only."""
import json
import re
import time
import urllib.parse
import urllib.request

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
QUERIES = {
    "griseofulvin_spindle": "griseofulvin[tiab] AND (aneugen*[tiab] OR spindle[tiab] OR tubulin[tiab] OR micronucle*[tiab])",
    "topo2_etoposide": "(etoposide[tiab]) AND (chromosome missegregation[tiab] OR aneuploid*[tiab] OR micronucle*[tiab]) AND human[tiab]",
    "anthracycline_bub1b": "(doxorubicin[tiab] OR anthracycline[tiab] OR idarubicin[tiab] OR mitoxantrone[tiab]) AND (BUB1B[tiab] OR BubR1[tiab])",
    "alkylator_clastogen": "(melphalan[tiab] OR ifosfamide[tiab] OR cyclophosphamide[tiab]) AND (micronucle*[tiab] OR chromosomal aberration*[tiab])",
    "antimetabolite_clastogen": "(methotrexate[tiab] OR gemcitabine[tiab]) AND (micronucle*[tiab] OR chromosomal aberration*[tiab] OR aneuploid*[tiab])",
    "topo1_irinotecan": "(irinotecan[tiab] OR topotecan[tiab] OR camptothecin[tiab]) AND (micronucle*[tiab] OR chromosomal aberration*[tiab])",
    "mitomycin_clastogen": "mitomycin C[tiab] AND (positive control[tiab] OR clastogen*[tiab]) AND micronucle*[tiab]",
    "bubr1_resistance_direction": "(BUB1B[tiab] OR BubR1[tiab]) AND (resistance[tiab]) AND (DNA-damaging[tiab] OR chemotherapy[tiab] OR cisplatin[tiab])",
}
KEEP = re.compile(r"(aneuploid|missegregat|micronucle|chromosom|spindle|checkpoint|BubR1|BUB1B|clastogen|aneugen)", re.I)


def esearch(q, n=4):
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json"
         "&retmax=%d&sort=relevance&term=%s" % (n, urllib.parse.quote(q)))
    with urllib.request.urlopen(u, timeout=60) as r:
        d = json.load(r)
    return d["esearchresult"]["count"], d["esearchresult"]["idlist"]


def efetch(ids):
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
         + ",".join(ids))
    with urllib.request.urlopen(u, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


store = {}
for k, q in QUERIES.items():
    cnt, ids = esearch(q)
    print("\n===== %s | count=%s" % (k, cnt))
    store[k] = {"query": q, "count": cnt, "records": {}}
    if not ids:
        continue
    xml = efetch(ids)
    for art in xml.split("<PubmedArticle>")[1:]:
        pid = re.search(r"<PMID[^>]*>(\d+)</PMID>", art).group(1)
        ti = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S)
        ti = re.sub(r"<[^>]+>", "", ti.group(1)) if ti else ""
        ab = re.sub(r"<[^>]+>", "", " ".join(
            re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S)))
        yr = re.search(r"<Year>(\d{4})</Year>", art)
        store[k]["records"][pid] = {"year": yr.group(1) if yr else "", "title": ti, "abstract": ab}
        print("-- %s (%s) %s" % (pid, yr.group(1) if yr else "", ti[:120]))
        for s in re.split(r"(?<=\.)\s+", ab):
            if KEEP.search(s) and len(s) < 320:
                print("   *", s.strip())
    time.sleep(0.5)
with open(OUT + "lit_class.json", "w") as f:
    json.dump(store, f, indent=1)
