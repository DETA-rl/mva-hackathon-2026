import json, sys, urllib.request, urllib.parse
for doi in sys.argv[1:]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mva-research-audit/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            m = json.load(r)["message"]
            title = (m.get("title") or ["?"])[0][:110]
            year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
            print(f"OK   {doi} | {year} | {title}")
    except Exception as e:
        print(f"FAIL {doi} | {type(e).__name__} {getattr(e,'code','')}")
