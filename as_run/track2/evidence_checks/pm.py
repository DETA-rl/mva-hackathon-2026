import json, sys, urllib.parse, urllib.request, time
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
def get(url):
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e; time.sleep(1.5)
    raise err
def search(q, n=6):
    u = B + "esearch.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "term": q, "retmax": n, "retmode": "json"})
    ids = get(u)["esearchresult"]["idlist"]
    time.sleep(0.4)
    if not ids: return []
    u = B + "esummary.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    res = get(u)["result"]
    time.sleep(0.4)
    out = []
    for i in ids:
        r = res[i]
        doi = next((a["value"] for a in r.get("articleids", []) if a["idtype"] == "doi"), "")
        au = r.get("authors", [])
        first = au[0]["name"] if au else "?"
        out.append(f'{i} | {first} | {r.get("pubdate","")[:4]} | {r.get("source","")} | {r.get("title","")[:150]} | {doi}')
    return out
if __name__ == "__main__":
    for q in sys.argv[1:]:
        print("## " + q)
        for line in search(q): print(line)
        print()
