#!/usr/bin/env python3
"""Abstracts for the records that could decide a direction in Batch 4 part A, plus a fixed
search for the Aurora B class source. PMIDs and mechanism terms only."""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4a/"
EF = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ES = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

PMIDS = ["39845481", "32573315", "19397590", "18668508", "19713760", "18723675",
         "16227576", "42757823", "37443114", "33542435", "38048028"]

# the Aurora B class source, searched not assumed
SEARCHES = [
    'Hesperadin[tiab] AND Aurora[tiab]',
    '("Aurora B"[tiab] OR AURKB[tiab]) AND ("spindle checkpoint"[tiab] OR "spindle assembly checkpoint"[tiab]) AND (inhibitor[tiab] OR inhibition[tiab]) AND BubR1[tiab]',
]
for q in SEARCHES:
    url = ES + "?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": q, "retmax": "8", "retmode": "json", "sort": "relevance"})
    with urllib.request.urlopen(url, timeout=40) as r:
        j = json.load(r)
    print("SEARCH:", q, "->", j["esearchresult"]["count"], j["esearchresult"].get("idlist"))
    PMIDS += [p for p in j["esearchresult"].get("idlist", [])[:4] if p not in PMIDS]
    time.sleep(0.4)

url = EF + "?" + urllib.parse.urlencode(
    {"db": "pubmed", "id": ",".join(PMIDS), "retmode": "xml"})
with urllib.request.urlopen(url, timeout=90) as r:
    xml = r.read()
open(OUT + "b4a_abstracts.xml", "wb").write(xml)

root = ET.fromstring(xml)
out = []
for art in root.iter("PubmedArticle"):
    pmid = art.findtext(".//PMID")
    ti = art.findtext(".//ArticleTitle") or ""
    jr = art.findtext(".//Journal/ISOAbbreviation") or ""
    yr = art.findtext(".//PubDate/Year") or art.findtext(".//PubDate/MedlineDate") or ""
    ab = " ".join("".join(e.itertext()) for e in art.iter("AbstractText"))
    out.append("PMID %s | %s %s\n%s\nABSTRACT: %s\n" % (pmid, jr, yr, ti, ab[:1800]))
open(OUT + "b4a_abstracts.txt", "w").write("\n".join(out))
print("\n\n".join(out))
