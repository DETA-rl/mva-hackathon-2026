"""C1 recheck: names that returned 404 on openfda.generic_name are re-queried on
substance_name and brand_name before any class verdict, so a search-syntax miss cannot
produce a false removal. Drug names only."""
import json, time, urllib.parse, urllib.request
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
NAMES = ["fasudil","fenretinide","heather","hesperidin","ifenprodil","infigratinib",
         "lenvatinib","maprotiline","niclosamide","nikita","osimertinib",
         "truseltiq","lenvima","tagrisso","ludiomil","niclocide","eril"]
def get(u):
    try:
        with urllib.request.urlopen(u, timeout=45) as r: return json.load(r)
    except Exception as e: return {"__err__": str(e)}
out = []
for n in NAMES:
    q = urllib.parse.quote(n)
    row = {"name": n}
    for field in ("openfda.substance_name", "openfda.brand_name"):
        d = get("https://api.fda.gov/drug/drugsfda.json?search=%s:%%22%s%%22&limit=3" % (field, q))
        if "__err__" in d:
            row[field] = d["__err__"]
        else:
            tot = d.get("meta", {}).get("results", {}).get("total", 0)
            apps = [(r.get("application_number",""), r.get("openfda",{}).get("brand_name",[None])[0] if r.get("openfda") else None,
                     sorted({p.get("marketing_status","") for p in r.get("products",[])})) for r in d.get("results",[])]
            row[field] = {"total": tot, "apps": apps}
        time.sleep(0.3)
    out.append(row); print(json.dumps(row))
with open(OUT + "c1_recheck.json","w") as f: json.dump(out, f, indent=1)
