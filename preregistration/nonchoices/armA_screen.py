#!/usr/bin/env python3
"""Arm A of PRE-REG-NONCHOICES (sha256 ed19c936...): gene-to-drug database screen.
DGIdb GraphQL + ChEMBL via UniProt. Gene symbols only leave this machine."""
import json, time, urllib.request, urllib.parse, collections, sys

OUT = "/[redacted]/scratchpad/agent_out/nonchoices"
CALLS = {"n": 0}

GENES = ["BUB1B","BUB3","MAD2L1","CDC20","TTK","BUB1",
         "NAMPT","NAPRT","NMNAT1","NMNAT2","NMNAT3","NMRK1","NMRK2",
         "SIRT1","SIRT2",
         "CREBBP","EP300","KAT2B",
         "HSF1","HSPA1A","HSP90AA1","HSP90AB1",
         "ANAPC1","ANAPC2","ANAPC4","ANAPC5","ANAPC11","CDC16","CDC23","CDC27",
         "UBE2C","UBE2S","PSMB1","PSMB2","PSMB5",
         "PPP2CA","PPP2R1A","PPP2R5A","PPP2R5B","PPP2R5C","PPP2R5D","PPP2R5E",
         "KIF18A","PLK4","AURKB","MTOR","FBXW7"]


def get(url, data=None, hdrs=None):
    CALLS["n"] += 1
    if CALLS["n"] > 100:
        raise SystemExit("CALL BOUND 100 REACHED")
    req = urllib.request.Request(url, data=data, headers=hdrs or {"Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if attempt == 2:
                print(f"  FAIL {url[:80]}: {e}", file=sys.stderr)
                return None
            time.sleep(4)


# ---------- A1: DGIdb ----------
dgidb = []
for i in range(0, len(GENES), 10):
    batch = GENES[i:i + 10]
    q = ('{genes(names:%s){nodes{name interactions{drug{name conceptId approved} '
         'interactionTypes{type}}}}}' % json.dumps(batch))
    d = get("https://dgidb.org/api/graphql", json.dumps({"query": q}).encode(),
            {"Content-Type": "application/json", "Accept": "application/json"})
    if not d or not d.get("data"):
        continue
    for node in d["data"]["genes"]["nodes"]:
        for it in node["interactions"]:
            if it["drug"].get("approved"):
                dgidb.append({"gene": node["name"], "drug": it["drug"]["name"],
                              "concept_id": it["drug"]["conceptId"],
                              "itype": ",".join(t["type"] for t in it["interactionTypes"])})
    time.sleep(1)
print(f"A1 DGIdb: {len(dgidb)} approved interactions, "
      f"{len({r['drug'] for r in dgidb})} distinct drugs, calls={CALLS['n']}")

# ---------- A2: ChEMBL ----------
acc2sym = {}
for i in range(0, len(GENES), 24):
    batch = GENES[i:i + 24]
    q = "(" + " OR ".join(f"gene_exact:{g}" for g in batch) + ") AND organism_id:9606 AND reviewed:true"
    url = ("https://rest.uniprot.org/uniprotkb/search?" +
           urllib.parse.urlencode({"query": q, "fields": "accession,gene_primary", "size": 500, "format": "json"}))
    d = get(url)
    for e in (d or {}).get("results", []):
        sym = (e.get("genes") or [{}])[0].get("geneName", {}).get("value")
        if sym in GENES:
            acc2sym[e["primaryAccession"]] = sym
print(f"A2 UniProt: {len(acc2sym)} accessions for {len(set(acc2sym.values()))}/{len(GENES)} genes")
missing = sorted(set(GENES) - set(acc2sym.values()))
if missing:
    print(f"   no reviewed accession: {missing}")

accs = sorted(acc2sym)
tgt2sym = {}
for i in range(0, len(accs), 15):
    b = accs[i:i + 15]
    d = get("https://www.ebi.ac.uk/chembl/api/data/target.json?limit=1000"
            f"&target_components__accession__in={','.join(b)}")
    for t in (d or {}).get("targets", []):
        if t.get("organism") == "Homo sapiens" and t.get("target_type") == "SINGLE PROTEIN":
            syms = {acc2sym[c["accession"]] for c in t.get("target_components", [])
                    if c.get("accession") in acc2sym}
            if syms:
                tgt2sym[t["target_chembl_id"]] = sorted(syms)[0]
print(f"A2 ChEMBL targets: {len(tgt2sym)} single-protein human targets")

mechs = []
tids = sorted(tgt2sym)
for i in range(0, len(tids), 15):
    b = tids[i:i + 15]
    off = 0
    while True:
        d = get("https://www.ebi.ac.uk/chembl/api/data/mechanism.json?limit=1000"
                f"&offset={off}&target_chembl_id__in={','.join(b)}")
        if not d:
            break
        mechs += [{"mol": m["molecule_chembl_id"], "gene": tgt2sym.get(m.get("target_chembl_id"), "?"),
                   "moa": m.get("mechanism_of_action"), "action": m.get("action_type")}
                  for m in d.get("mechanisms", [])]
        if not d["page_meta"].get("next"):
            break
        off += 1000
print(f"A2 mechanisms: {len(mechs)} records, {len({m['mol'] for m in mechs})} distinct molecules")

mols = sorted({m["mol"] for m in mechs})
info = {}
for i in range(0, len(mols), 50):
    b = mols[i:i + 50]
    d = get("https://www.ebi.ac.uk/chembl/api/data/molecule.json?limit=1000"
            f"&molecule_chembl_id__in={','.join(b)}")
    for m in (d or {}).get("molecules", []):
        info[m["molecule_chembl_id"]] = {"name": m.get("pref_name"), "max_phase": m.get("max_phase")}

chembl = []
for m in mechs:
    meta = info.get(m["mol"], {})
    try:
        phase = float(meta.get("max_phase") or 0)
    except (TypeError, ValueError):
        phase = 0
    if phase == 4.0:
        chembl.append({**m, "name": meta.get("name") or m["mol"]})
print(f"A2 ChEMBL approved (max_phase 4): {len(chembl)} records, "
      f"{len({r['name'] for r in chembl})} distinct drugs, calls={CALLS['n']}")

per_gene = collections.Counter()
for r in dgidb:
    per_gene[r["gene"]] += 1
for r in chembl:
    per_gene[r["gene"]] += 1
over = {g: c for g, c in per_gene.items() if c > 50}
print(f"genes over the 50-drug class bound: {over if over else 'none'}")

json.dump({"dgidb": dgidb, "chembl": chembl, "per_gene": dict(per_gene),
           "over_bound": over, "genes_no_accession": missing, "calls": CALLS["n"]},
          open(f"{OUT}/armA_raw.json", "w"), indent=1)
print(f"TOTAL CALLS ARM A: {CALLS['n']}")
