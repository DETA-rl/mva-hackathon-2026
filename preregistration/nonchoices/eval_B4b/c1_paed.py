"""C1 paediatric limb for the only row in items 50-98 that could plausibly pass (gentamicin).
Reported, never exclusionary, per PRE-REG-NONCHOICES 5.1. Drug name only."""
import json
import re
import urllib.request

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
u = ("https://api.fda.gov/drug/label.json?search=openfda.generic_name:%22gentamicin%22"
     "+AND+openfda.route:%22INTRAVENOUS%22&limit=2")
with urllib.request.urlopen(u, timeout=60) as r:
    j = json.load(r)
out = []
for res in j.get("results", []):
    for f in ("pediatric_use", "use_in_specific_populations", "indications_and_usage"):
        for t in res.get(f, []):
            txt = re.sub(r"\s+", " ", t).strip()
            if f == "indications_and_usage":
                txt = txt[:400]
            out.append(f + ": " + txt[:900])
out = list(dict.fromkeys(out))
for s in out:
    print("-", s, "\n")
with open(OUT + "c1_paed_gentamicin.json", "w") as f:
    json.dump(out, f, indent=1)
