"""Provenance of the DGIdb target claims carried in BATCHES.md for Batch 4 items 50-98.
The claim is the database's, not ours; this records which source DB asserts it and with what
interaction type. Drug and gene names only leave this machine."""
import json
import urllib.request

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
DRUGS = ["LOPERAMIDE", "LEVOCETIRIZINE", "ISOPROTERENOL", "NICARDIPINE", "HESPERIDIN",
         "FASUDIL", "METFORMIN", "NICLOSAMIDE", "MAPROTILINE", "GLASDEGIB", "LAPATINIB",
         "IDARUBICIN", "HALOPERIDOL", "IFENPRODIL", "FENRETINIDE", "INFIGRATINIB"]
GENES = ("MTOR", "AURKB", "PLK4", "KIF18A", "BUB1B")

query = ("{drugs(names:" + json.dumps(DRUGS) + "){nodes{name interactions{gene{name} "
         "interactionTypes{type directionality} interactionScore sources{sourceDbName}}}}}")
req = urllib.request.Request("https://dgidb.org/api/graphql",
                             data=json.dumps({"query": query}).encode(),
                             headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=90) as r:
    d = json.load(r)
with open(OUT + "claim_provenance.json", "w") as f:
    json.dump(d, f, indent=1)

nodes = d.get("data", {}).get("drugs", {}).get("nodes", [])
print("drugs returned: %d" % len(nodes))
for n in nodes:
    keep = [i for i in n["interactions"] if i["gene"]["name"] in GENES]
    if not keep:
        print("%s -> no interaction with %s returned" % (n["name"], "/".join(GENES)))
        continue
    for i in keep:
        types = [(t["type"], t["directionality"]) for t in i["interactionTypes"]]
        srcs = sorted({s["sourceDbName"] for s in i["sources"]})
        print("%s -> %s | types=%s | score=%s | sources=%s"
              % (n["name"], i["gene"]["name"], types, i["interactionScore"], srcs))
