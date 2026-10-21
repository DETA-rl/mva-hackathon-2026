#!/usr/bin/env python3
"""Titles for every record returned by b4a_c3_search.py, so that every C3 verdict in Batch 4
part A rests on a record that was actually read rather than on an assumption about the class.
PMIDs and drug names only leave the machine."""
import json
import time
import urllib.parse
import urllib.request

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4a/"
ESUM = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

hits = json.load(open(OUT + "c3_direction_search.json"))
allp = sorted({p for v in hits.values() for p in v["pmids"] if p.isdigit()})
print("unique PMIDs:", len(allp))

titles = {}
for i in range(0, len(allp), 50):
    chunk = allp[i:i + 50]
    url = ESUM + "?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(chunk), "retmode": "json"})
    with urllib.request.urlopen(url, timeout=60) as r:
        j = json.load(r)
    for p in chunk:
        rec = j.get("result", {}).get(p, {})
        titles[p] = "%s (%s, %s)" % (rec.get("title", "?"),
                                     (rec.get("source") or "?"),
                                     (rec.get("pubdate") or "?")[:4])
    time.sleep(0.4)

with open(OUT + "c3_titles.tsv", "w") as f:
    f.write("drug\tcount\tpmid\ttitle\n")
    for d in sorted(hits):
        v = hits[d]
        if not v["pmids"]:
            f.write("%s\t%d\t-\t-\n" % (d, v["count"]))
            continue
        for p in v["pmids"]:
            f.write("%s\t%d\t%s\t%s\n" % (d, v["count"], p, titles.get(p, "?")))
json.dump(titles, open(OUT + "c3_titles.json", "w"), indent=1, sort_keys=True)
print("wrote", OUT + "c3_titles.tsv")
