#!/usr/bin/env python3
"""C1 for eval_B4a: regulatory class from the public Drugs@FDA bulk files already on the box.

Reading fixed by PRE-REG-NONCHOICES Section 5.1 (identical to C1 of PRE-REG-T2-CLASS-01):
"Rx" if every authorised oral or systemic single-agent product is prescription; "OTC" if an
authorised non-prescription drug product exists; "no authorised drug product" if none exists.
This script reports the raw marketing-status and form evidence per name; the reading is applied
in the RESULT file. No patient data. Local public file only, no API call.
"""
import csv
import json
import sys
from collections import defaultdict

DL = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/dl_fda/"
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4a/"

NAMES = [
    "afatinib", "alpelisib", "amikacin", "amiodarone", "amsacrine", "arsenic trioxide",
    "ascorbic", "aspirin", "atorvastatin", "axitinib", "azathioprine", "baricitinib",
    "belumosudil", "bendamustine", "beta-hydroxyisovaleric", "bleomycin", "cabozantinib",
    "calcitriol", "canagliflozin", "capecitabine", "capivasertib", "carbon dioxide",
    "carboplatin", "chloroquine", "chlorpromazine", "cisplatin", "cladribine", "copanlisib",
    "cyclosporine", "cytarabine", "dapagliflozin", "dasatinib", "decitabine", "dequalinium",
    "dexamethasone", "dexrazoxane", "digoxin", "donepezil", "doxazosin", "doxycycline",
    "ebastine", "eltrombopag", "entrectinib", "enzalutamide", "epinephrine", "erlotinib",
    "estradiol", "estradiol and progesterone", "etomidate",
]
# extra synonyms searched for the same row, recorded explicitly
SYN = {
    "ascorbic": ["ascorbic acid", "sodium ascorbate"],
    "beta-hydroxyisovaleric": ["beta-hydroxy-beta-methylbutyrate", "calcium hmb"],
    "aspirin": ["aspirin", "acetylsalicylic acid"],
    "cyclosporine": ["cyclosporine", "cyclosporin"],
    "estradiol and progesterone": ["estradiol", "progesterone"],
    "chloroquine": ["chloroquine phosphate", "chloroquine"],
    "epinephrine": ["epinephrine", "epinephrine bitartrate"],
    "amiodarone": ["amiodarone hydrochloride", "amiodarone"],
}

status_name = {}
with open(DL + "MarketingStatus_Lookup.txt") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        status_name[r["MarketingStatusID"]] = r["MarketingStatusDescription"]

status = defaultdict(set)   # (ApplNo, ProductNo) -> {status ids}
with open(DL + "MarketingStatus.txt") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        status[(r["ApplNo"], r["ProductNo"])].add(r["MarketingStatusID"])

SYSTEMIC = ("ORAL", "INTRAVENOUS", "INJECTION", "INTRAMUSCULAR", "SUBCUTANEOUS",
            "TRANSDERMAL", "SUBLINGUAL", "RECTAL", "INTRAVESICAL", "INTRATHECAL",
            "INTRA-ARTERIAL", "INHALATION", "BUCCAL", "INTRAPERITONEAL", "INTRAVENOUS;")

rows = []
with open(DL + "Products.txt", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        rows.append(r)

res = {}
for name in NAMES:
    keys = [k.lower() for k in SYN.get(name, [name])]
    hits = []
    for r in rows:
        ing = (r.get("ActiveIngredient") or "").lower()
        parts = [p.strip() for p in ing.split(";")]
        dn = (r.get("DrugName") or "").lower()
        # a part matches if it is the parent name or the parent name followed by a salt or
        # ester word ("amikacin sulfate" matches "amikacin"). Recorded so the rule is auditable.
        exact = any(p == k or p.startswith(k + " ") for k in keys for p in parts)
        in_combo = exact and len(parts) > 1
        single = exact and len(parts) == 1
        if not exact and not any(k == dn for k in keys):
            continue
        form = (r.get("Form") or "").upper()
        sysmic = any(t in form for t in SYSTEMIC)
        sts = sorted(status.get((r["ApplNo"], r["ProductNo"]), set()))
        hits.append({
            "appl": r["ApplNo"], "prod": r["ProductNo"], "form": r.get("Form", ""),
            "ingredient": r.get("ActiveIngredient", ""), "single": single,
            "combo": in_combo, "systemic": sysmic,
            "status": [status_name.get(s, s) for s in sts],
        })
    # summarise
    sing_sys = [h for h in hits if h["single"] and h["systemic"]]
    summary = {
        "n_products": len(hits),
        "n_single_systemic": len(sing_sys),
        "statuses_single_systemic": sorted({s for h in sing_sys for s in h["status"]}),
        "statuses_any": sorted({s for h in hits for s in h["status"]}),
        "forms_single_systemic": sorted({h["form"] for h in sing_sys})[:6],
        "example_appl": sorted({h["appl"] for h in sing_sys})[:3] or sorted({h["appl"] for h in hits})[:3],
        "keys_searched": keys,
    }
    res[name] = summary
    print("%-28s n=%-4d single_sys=%-4d status_single_sys=%s status_any=%s" % (
        name, len(hits), len(sing_sys),
        ",".join(summary["statuses_single_systemic"]) or "-",
        ",".join(summary["statuses_any"]) or "-"))

with open(OUT + "c1_drugsatfda_salts.json", "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
print("\nwrote", OUT + "c1_drugsatfda_salts.json")
