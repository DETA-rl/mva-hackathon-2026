#!/usr/bin/env python3
"""Union of arm A and arm B under PRE-REG-NONCHOICES (sha256 ed19c936...), Section 4."""
import json, re, collections

OUT = "/[redacted]/scratchpad/agent_out/nonchoices"
A = json.load(open(f"{OUT}/armA_raw.json"))
B = json.load(open(f"{OUT}/armB_raw.json"))

SALT = (r"\s+(hydrochloride|hcl|sodium|maleate|sulfate|sulphate|acetate|citrate|mesylate|"
        r"tartrate|phosphate|succinate|fumarate|besylate|chloride|potassium|calcium|nitrate|"
        r"dihydrate|monohydrate|anhydrous|d-mannitol|acid)$")


def norm(n):
    n = n.strip().lower()
    for _ in range(3):
        n = re.sub(SALT, "", n).strip()
    return {"nicotinic acid": "niacin", "niacinamide": "nicotinamide",
            "abraxane": "paclitaxel", "ibandronate": "ibandronic acid",
            "risedronic": "risedronic acid", "zoledronic": "zoledronic acid",
            "bortezomib": "bortezomib"}.get(n, n)


# mechanism block per gene, fixed from the pre-reg gene table
BLOCK = {}
for g in "BUB1B BUB3 MAD2L1 CDC20 TTK BUB1 KIF18A PLK4 AURKB MTOR".split():
    BLOCK[g] = "mitotic-checkpoint-and-aneuploidy-tolerance"
for g in "NAMPT NAPRT NMNAT1 NMNAT2 NMNAT3 NMRK1 NMRK2 SIRT1 SIRT2".split():
    BLOCK[g] = "NAD-and-sirtuin"
for g in "CREBBP EP300 KAT2B".split():
    BLOCK[g] = "acetyltransferase"
for g in "HSF1 HSPA1A HSP90AA1 HSP90AB1".split():
    BLOCK[g] = "proteostasis"
for g in ("ANAPC1 ANAPC2 ANAPC4 ANAPC5 ANAPC11 CDC16 CDC23 CDC27 UBE2C UBE2S "
          "PSMB1 PSMB2 PSMB5 FBXW7").split():
    BLOCK[g] = "ubiquitin-proteasome-and-APCC"
for g in "PPP2CA PPP2R1A PPP2R5A PPP2R5B PPP2R5C PPP2R5D PPP2R5E".split():
    BLOCK[g] = "PP2A"

uni = collections.defaultdict(lambda: {"genes": set(), "blocks": set(), "arms": set(),
                                       "src": set(), "moa": set(), "pmids": set()})
for r in A["dgidb"]:
    u = uni[norm(r["drug"])]
    u["genes"].add(r["gene"]); u["blocks"].add(BLOCK.get(r["gene"], "other"))
    u["arms"].add("A1-DGIdb"); u["src"].add(r["concept_id"])
    if r["itype"]:
        u["moa"].add(f"{r['gene']} {r['itype'].lower()}")
for r in A["chembl"]:
    u = uni[norm(r["name"])]
    u["genes"].add(r["gene"]); u["blocks"].add(BLOCK.get(r["gene"], "other"))
    u["arms"].add("A2-ChEMBL"); u["src"].add(r["mol"]); u["moa"].add(r["moa"] or "")
for r in B["rows"]:
    u = uni[norm(r["drug"])]
    u["arms"].add("B-PubMed"); u["pmids"].update(r["pmids"][:4])

# Section 4: already evaluated, with the deciding test
EVAL = {}
for d in ["niacin", "arimoclomol", "fingolimod", "nmn", "nr", "sodium phenylbutyrate",
          "phenylbutyrate"]:
    EVAL[d] = "carried candidate (TRACK2_REPORT_v2 Section 5)"
EVAL["nicotinamide"] = "T2-CLASS-01 (C1 and C4): dropped"
for d in ["everolimus", "sirolimus", "temsirolimus"]:
    EVAL[d] = "T2-P4: MTOR flagged 0.986"
for d in ["vorinostat", "romidepsin", "belinostat", "panobinostat", "givinostat",
          "valproate", "valproic"]:
    EVAL[d] = "RESULT-R2C-HDAC: class excluded on direction"
EVAL["fingolimod"] = "RESULT-R2B-EXPOSURE: removed on direction and exposure"

rows = []
for name, u in uni.items():
    if len(name) < 4 or name in {"oxygen", "sodium", "calcium", "potassium", "amino acids",
                                 "nitric oxide", "cysteine", "adenosine", "water"}:
        kind = "EXCLUDED-nonspecific"
    else:
        kind = "already-evaluated" if name in EVAL else "new"
    blocks = u["blocks"] or {"unassigned-literature-cooccurrence"}
    rows.append({"drug": name, "status": kind, "deciding_test": EVAL.get(name, ""),
                 "arms": sorted(u["arms"]), "genes": sorted(u["genes"]),
                 "blocks": sorted(blocks), "moa": sorted(x for x in u["moa"] if x)[:3],
                 "src": sorted(u["src"])[:3], "pmids": sorted(u["pmids"])[:4]})
rows.sort(key=lambda r: (r["status"], r["drug"]))

c = collections.Counter(r["status"] for r in rows)
print("UNIVERSE", dict(c), "total", len(rows))
both = [r for r in rows if len(r["arms"]) > 1 and not r["arms"] == ["B-PubMed"]]
print("reached by both arms:", len([r for r in rows if any(a.startswith('A') for a in r['arms'])
                                    and 'B-PubMed' in r['arms']]))
print("arm A only:", len([r for r in rows if 'B-PubMed' not in r['arms']]),
      " arm B only:", len([r for r in rows if r['arms'] == ['B-PubMed']]))
bb = collections.Counter(b for r in rows if r["status"] == "new" for b in r["blocks"])
print("new drugs per mechanism block:", dict(bb))
print("\nalready-evaluated reached by the screen:",
      sorted(r["drug"] for r in rows if r["status"] == "already-evaluated"))
json.dump(rows, open(f"{OUT}/universe.json", "w"), indent=1)
