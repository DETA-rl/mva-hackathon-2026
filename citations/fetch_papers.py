#!/usr/bin/env python3
"""For each VERIFIED ref in refs.json: save metadata + PubMed abstract, and the full-text PDF only if open access.
Output: papers/<key>/{meta.json, abstract.txt, fulltext.pdf?} and PAPERS_INDEX.md"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "mva-hackathon-ref-archiver/1.0 (research; contact via repo)"}

def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        d = r.read()
    return d if binary else d.decode("utf-8", "replace")

refs = [r for r in json.load(open("refs.json")) if r["status"] == "VERIFIED"]
os.makedirs("papers", exist_ok=True)
rows = []
for r in refs:
    pmid, key = r["pmid"], r["key"]
    d = f"papers/{key}"; os.makedirs(d, exist_ok=True)
    # abstract
    ab = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text")
    open(f"{d}/abstract.txt", "w").write(ab.strip() + "\n"); time.sleep(0.35)
    # Europe PMC core record
    q = urllib.parse.quote(f"EXT_ID:{pmid} AND SRC:MED")
    core = json.loads(get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json"))
    res = (core.get("resultList", {}).get("result") or [{}])[0]
    pmcid = res.get("pmcid", ""); is_oa = res.get("isOpenAccess") == "Y"; lic = res.get("license", "")
    pdf = "none (not open access)"
    if pmcid and is_oa:
        try:
            b = get(f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf", binary=True)
            if b[:4] == b"%PDF":
                open(f"{d}/fulltext.pdf", "wb").write(b); pdf = f"fulltext.pdf ({len(b)//1024} KB)"
            else:
                pdf = "OA flagged but PDF not retrievable"
        except Exception as e:
            pdf = f"OA flagged, download error: {e}"
    meta = {**r, "pmcid": pmcid, "open_access": is_oa, "license": lic,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "doi_url": f"https://doi.org/{r['doi']}" if r.get("doi") else "",
            "preprint": "bioRxiv" in r.get("journal", "")}
    json.dump(meta, open(f"{d}/meta.json", "w"), indent=1, ensure_ascii=False)
    rows.append((key, meta, pdf))
    print(f"{key:28} OA={str(is_oa):5} {pdf}")
    time.sleep(0.35)

with open("PAPERS_INDEX.md", "w") as f:
    f.write("# Reference papers archive\n\nEvery entry was matched against its PubMed record (first author, year, title). "
            "Full text is included only when the paper is open access; otherwise the PubMed abstract is archived and the DOI link points to the publisher.\n\n")
    f.write("| Key | Citation | PMID | Access | Local copy |\n|---|---|---|---|---|\n")
    for key, m, pdf in rows:
        acc = "preprint (not peer reviewed)" if m["preprint"] else ("open access" if m["open_access"] else "paywalled")
        f.write(f'| {key} | {m["first_author"]} et al. {m["title"][:80]}... *{m["journal"]}* {m["pubdate"][:4]} | [{m["pmid"]}]({m["pubmed_url"]}) | {acc} | {pdf} |\n')
print(len(rows), "papers archived;", sum(1 for _, m, _ in rows if m["open_access"]), "open access")
