#!/usr/bin/env python3
"""C3 direction limb for eval_B4a: for every drug in Batch 4 part A, the search route that must
return a primary source before direction can be anything but UNKNOWN.

Query per drug, fixed for every row so no drug gets a friendlier search:
  <drug>[tiab] AND (BUB1B[tiab] OR BubR1[tiab] OR "spindle assembly checkpoint"[tiab]
                    OR "mitotic checkpoint"[tiab] OR "chromosome missegregation"[tiab])
Counts and PMIDs are recorded. A zero count is the named failed route for an UNRESOLVED row.
Only drug names and mechanism terms leave the machine. No email, no API key, no patient data.
"""
import json
import time
import urllib.parse
import urllib.request

OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4a/"
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

NAMES = [
    "afatinib", "alpelisib", "amikacin", "amiodarone", "amsacrine", "arsenic trioxide",
    "ascorbic acid", "aspirin", "atorvastatin", "axitinib", "azathioprine", "baricitinib",
    "belumosudil", "bendamustine", "beta-hydroxy-beta-methylbutyrate", "bleomycin",
    "cabozantinib", "calcitriol", "canagliflozin", "capecitabine", "capivasertib",
    "carbon dioxide", "carboplatin", "chloroquine", "chlorpromazine", "cisplatin",
    "cladribine", "copanlisib", "cyclosporine", "cytarabine", "dapagliflozin", "dasatinib",
    "decitabine", "dequalinium", "dexamethasone", "dexrazoxane", "digoxin", "donepezil",
    "doxazosin", "doxycycline", "ebastine", "eltrombopag", "entrectinib", "enzalutamide",
    "epinephrine", "erlotinib", "estradiol", "progesterone", "etomidate",
]
TERMS = ('(BUB1B[tiab] OR BubR1[tiab] OR "spindle assembly checkpoint"[tiab] '
         'OR "mitotic checkpoint"[tiab] OR "chromosome missegregation"[tiab])')

res = {}
for n in NAMES:
    q = '%s[tiab] AND %s' % (n, TERMS)
    url = ESEARCH + "?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": q, "retmax": "20", "retmode": "json"})
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            j = json.load(r)
        c = int(j["esearchresult"]["count"])
        ids = j["esearchresult"].get("idlist", [])
    except Exception as e:
        c, ids = -1, ["ERROR:%s" % e]
    res[n] = {"query": q, "count": c, "pmids": ids}
    print("%-34s %s  %s" % (n, c, ",".join(ids[:8])))
    time.sleep(0.4)

with open(OUT + "c3_direction_search.json", "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
print("wrote", OUT + "c3_direction_search.json")
