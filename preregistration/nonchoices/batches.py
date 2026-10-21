#!/usr/bin/env python3
"""Group the new drugs into the four mechanism batches of PRE-REG-NONCHOICES Section 6."""
import json, collections

OUT = "/[redacted]/scratchpad/agent_out/nonchoices"
rows = json.load(open(f"{OUT}/universe.json"))

ALSO = ["acetylcysteine", "ambroxol", "ataluren", "azithromycin", "digoxin", "escin", "fisetin",
        "hydroxychloroquine", "idebenone", "irinotecan", "isotretinoin", "l-glutamine",
        "levetiracetam", "mesalamine", "potassium citrate", "pralsetinib", "propranolol",
        "rilmenidine", "ruxolitinib", "somatropin", "spermidine", "tauroursodeoxycholic acid",
        "teprenone", "tocilizumab", "trametinib", "trehalose"]
ALSO_BLOCK = {"ambroxol": 1, "teprenone": 1, "tauroursodeoxycholic acid": 1, "trehalose": 1,
              "escin": 1, "l-glutamine": 1, "acetylcysteine": 1,
              "idebenone": 2, "spermidine": 2, "fisetin": 2, "isotretinoin": 2,
              "ataluren": 3, "azithromycin": 3,
              "irinotecan": 4, "trametinib": 4, "pralsetinib": 4, "ruxolitinib": 4,
              "tocilizumab": 4, "propranolol": 4, "levetiracetam": 4, "digoxin": 4,
              "hydroxychloroquine": 4, "mesalamine": 4, "potassium citrate": 4,
              "rilmenidine": 4, "somatropin": 4}
BATCH = {"proteostasis": 1, "NAD-and-sirtuin": 2, "acetyltransferase": 2,
         "ubiquitin-proteasome-and-APCC": 3, "PP2A": 3,
         "mitotic-checkpoint-and-aneuploidy-tolerance": 4,
         "unassigned-literature-cooccurrence": 4}
TITLE = {1: "Proteostasis, chaperone and heat-shock route",
         2: "NAD+, sirtuin and acetyltransferase route",
         3: "Ubiquitin-proteasome, APC/C and PP2A route",
         4: "Mitotic-checkpoint, aneuploidy-tolerance and unassigned literature co-occurrence"}

b = collections.defaultdict(list)
for r in rows:
    if r["status"] != "new":
        continue
    nb = min(BATCH.get(x, 4) for x in r["blocks"])
    mech = "; ".join(r["moa"]) or (("targets " + ", ".join(r["genes"])) if r["genes"] else
                                   "not assigned by the screen (literature co-occurrence only)")
    src = ", ".join(r["src"]) if r["src"] else ("PMID " + ", ".join(r["pmids"]))
    b[nb].append((r["drug"], mech, src, "+".join(a.split("-")[0] for a in r["arms"])))
for d in ALSO:
    b[ALSO_BLOCK[d]].append((d, "not assigned by the screen", "also considered", "-"))

lines = []
for nb in (1, 2, 3, 4):
    items = sorted(b[nb])
    lines.append(f"\n### Batch {nb}. {TITLE[nb]} ({len(items)} drugs)\n")
    lines.append("| Drug (INN or common name) | Claimed target or mechanism | Source record | Arm |")
    lines.append("|---|---|---|---|")
    for d, m, s, a in items:
        lines.append(f"| {d} | {m[:110]} | {s[:70]} | {a} |")
    print(f"Batch {nb}: {len(items)}")
open(f"{OUT}/_batch_tables.md", "w").write("\n".join(lines))
print("total new:", sum(len(v) for v in b.values()))
