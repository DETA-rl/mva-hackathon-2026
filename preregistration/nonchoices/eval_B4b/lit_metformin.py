"""Metformin direction check: the two records the frozen-style query returned, plus the human
lymphocyte cytogenetics record. PMIDs only."""
import json
import re
import urllib.request

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
IDS = ["33161761", "35568294", "27957796"]
u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
     + ",".join(IDS))
with urllib.request.urlopen(u, timeout=90) as r:
    xml = r.read().decode("utf-8", "replace")
out = {}
for art in xml.split("<PubmedArticle>")[1:]:
    pid = re.search(r"<PMID[^>]*>(\d+)</PMID>", art).group(1)
    ti = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S)
    ti = re.sub(r"<[^>]+>", "", ti.group(1)) if ti else ""
    ab = re.sub(r"<[^>]+>", "", " ".join(
        re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S)))
    out[pid] = {"title": ti, "abstract": ab}
    print("\n== %s %s\n%s" % (pid, ti, ab[:1700]))
with open(OUT + "lit_metformin.json", "w") as f:
    json.dump(out, f, indent=1)
