"""C1 for eval_B4b: regulatory class by drug name only, via openFDA drugsfda and label endpoints.
Reading per PRE-REG-T2-CLASS-01 C1 as reused by PRE-REG-NONCHOICES 5.1. Drug names only leave
this machine. No patient data. Output: one row per name.
"""
import json, time, urllib.parse, urllib.request
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
NAMES = ["etoposide","fasudil","fenretinide","fentanyl","ferric","ferrous","fluvastatin",
"gemcitabine","gentamicin","glasdegib","glucagon","griseofulvin","haloperidol","heather",
"trastuzumab","hesperidin","hydroxychloroquine","idarubicin","ifenprodil","ifosfamide",
"imatinib","infigratinib","irinotecan","isoniazid","isoproterenol","lapatinib","lenvatinib",
"letrozole","levetiracetam","levocetirizine","levonorgestrel","norepinephrine","loperamide",
"lovastatin","maprotiline","melphalan","mesalamine","metformin","methotrexate","mifepristone",
"minocycline","mitomycin","mitoxantrone","nicardipine","niclosamide","nicotine","nikita",
"olaparib","osimertinib"]

def get(url):
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.load(r)
    except Exception as e:
        return {"__err__": str(e)}

rows = []
for n in NAMES:
    q = urllib.parse.quote(n)
    u1 = "https://api.fda.gov/drug/drugsfda.json?search=openfda.generic_name:%22" + q + "%22&limit=5"
    d1 = get(u1)
    nres = d1.get("meta", {}).get("results", {}).get("total", 0) if "__err__" not in d1 else "err"
    apps, mktg, routes = [], set(), set()
    if isinstance(nres, int) and nres:
        for res in d1.get("results", []):
            apps.append(res.get("application_number", ""))
            for p in res.get("products", []):
                mktg.add(p.get("marketing_status", ""))
                routes.add(p.get("route", ""))
    # OTC / prescription marketing categories from the label endpoint
    u2 = "https://api.fda.gov/drug/label.json?search=openfda.generic_name:%22" + q + "%22&count=openfda.product_type.exact"
    d2 = get(u2)
    ptypes = {}
    if "results" in d2:
        ptypes = {r["term"]: r["count"] for r in d2["results"]}
    rows.append({"name": n, "drugsfda_total": nres, "apps": apps[:3],
                 "marketing_status": sorted(mktg), "routes": sorted(routes),
                 "label_product_types": ptypes,
                 "err": d1.get("__err__", "") or d2.get("__err__", "")})
    print(json.dumps(rows[-1]))
    time.sleep(0.4)
with open(OUT + "c1_openfda.json", "w") as f:
    json.dump(rows, f, indent=1)
