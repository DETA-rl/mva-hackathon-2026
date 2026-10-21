import urllib.request, json, time
ids = ["11447274", "15592459", "19726757", "15475955"]
for i in ids:
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={i}"
    try:
        raw = urllib.request.urlopen(url, timeout=60).read().decode()
        r = json.loads(raw)["result"].get(i, {})
        au = (r.get("authors") or [{}])[0].get("name", "")
        print(i, r.get("pubdate", "")[:4], au, "|", r.get("fulljournalname", "")[:30], "|", r.get("title", "")[:110])
    except Exception as e:
        print(i, "ERROR", str(e)[:120])
    time.sleep(3)
