"""C1 recheck 2: drugsfda products.brand_name and the label endpoint, with positive controls
(lenvima, tagrisso) to prove the query syntax before any class verdict is recorded."""
import json, time, urllib.parse, urllib.request
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
PAIRS = [("lenvatinib","LENVIMA"),("osimertinib","TAGRISSO"),("infigratinib","TRUSELTIQ"),
         ("maprotiline","MAPROTILINE HYDROCHLORIDE"),("niclosamide","NICLOCIDE"),
         ("fasudil","FASUDIL"),("fenretinide","FENRETINIDE"),("ifenprodil","IFENPRODIL"),
         ("hesperidin","HESPERIDIN"),("nikita","NIKITA")]
def get(u):
    try:
        with urllib.request.urlopen(u, timeout=45) as r: return json.load(r)
    except Exception as e: return {"__err__": str(e)}
out=[]
for generic, brand in PAIRS:
    row={"generic":generic,"brand":brand}
    d = get("https://api.fda.gov/drug/drugsfda.json?search=products.brand_name:%%22%s%%22&limit=3" % urllib.parse.quote(brand))
    row["drugsfda_products_brand"] = d.get("__err__") or [(r.get("application_number"), r.get("sponsor_name"), sorted({p.get("marketing_status","") for p in r.get("products",[])})) for r in d.get("results",[])]
    time.sleep(0.3)
    d2 = get("https://api.fda.gov/drug/label.json?search=openfda.substance_name:%%22%s%%22&limit=1" % urllib.parse.quote(generic))
    if "__err__" in d2: row["label_substance"]=d2["__err__"]
    else:
        r0=d2["results"][0]
        row["label_substance"]={"total":d2["meta"]["results"]["total"],"brand":r0.get("openfda",{}).get("brand_name"),"type":r0.get("openfda",{}).get("product_type"),"app":r0.get("openfda",{}).get("application_number")}
    time.sleep(0.3)
    out.append(row); print(json.dumps(row))
with open(OUT+"c1_recheck2.json","w") as f: json.dump(out,f,indent=1)
