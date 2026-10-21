#!/usr/bin/env python3
"""Arm B of PRE-REG-NONCHOICES (sha256 ed19c936...): PubMed literature screen.
Four fixed queries, retmax 200. Drug-name extraction against the Drugs@FDA lexicon."""
import json, time, re, urllib.request, urllib.parse, collections

OUT = "/[redacted]/scratchpad/agent_out/nonchoices"
EUT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CALLS = {"n": 0}

QUERIES = {
 "L1": "(BUB1B[tiab] OR BubR1[tiab]) AND (drug[tiab] OR treatment[tiab] OR inhibitor[tiab] OR activator[tiab])",
 "L2": '"mosaic variegated aneuploidy"[tiab] AND (treatment[tiab] OR therapy[tiab])',
 "L3": 'aneuploidy[tiab] AND "drug repurposing"[tiab]',
 "L4": "(BUB1B[tiab] OR BubR1[tiab]) AND (stabilization[tiab] OR stabilisation[tiab] OR \"protein level\"[tiab] OR degradation[tiab])",
}


def fetch(url, raw=False):
    CALLS["n"] += 1
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                b = r.read().decode("utf-8", "replace")
            return b if raw else json.loads(b)
        except Exception as e:
            if attempt == 2:
                print(f"  FAIL: {e}")
                return None
            time.sleep(4)


# fixed lexicon from the public Drugs@FDA bulk Products.txt already on the box
lex = set()
for line in open(f"{OUT}/Products.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) > 5:
        for name in re.split(r"[;,]", f[5]):          # ActiveIngredient column
            n = name.strip().lower()
            n = re.sub(r"\s+(hydrochloride|sodium|maleate|sulfate|acetate|citrate|mesylate|"
                       r"tartrate|phosphate|succinate|fumarate|besylate|chloride|potassium|"
                       r"calcium|dihydrate|monohydrate)$", "", n).strip()
            if len(n) >= 6 and re.fullmatch(r"[a-z][a-z0-9 \-]+", n):
                lex.add(n)
print(f"lexicon: {len(lex)} distinct active-ingredient names")

hits = collections.defaultdict(lambda: collections.defaultdict(set))
counts = {}
for qid, q in QUERIES.items():
    d = fetch(f"{EUT}/esearch.fcgi?db=pubmed&retmode=json&retmax=200&term={urllib.parse.quote(q)}")
    ids = d["esearchresult"]["idlist"]
    counts[qid] = {"total": int(d["esearchresult"]["count"]), "retrieved": len(ids)}
    print(f"{qid}: total {counts[qid]['total']}, retrieved {len(ids)}"
          f"{'  TRUNCATED' if counts[qid]['total'] > 200 else ''}")
    time.sleep(1)
    for i in range(0, len(ids), 100):
        xml = fetch(f"{EUT}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids[i:i+100])}", raw=True)
        time.sleep(1)
        if not xml:
            continue
        for art in xml.split("<PubmedArticle>")[1:]:
            pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
            if not pm:
                continue
            txt = re.sub(r"<[^>]+>", " ", art)
            low = " " + re.sub(r"\s+", " ", txt).lower() + " "
            for name in lex:
                if f" {name} " in low or f" {name}, " in low or f" {name}. " in low:
                    hits[name][qid].add(pm.group(1))

rows = []
for name, per_q in sorted(hits.items()):
    pmids = sorted({p for s in per_q.values() for p in s})
    rows.append({"drug": name, "queries": sorted(per_q), "n_pmids": len(pmids), "pmids": pmids[:8]})
rows.sort(key=lambda r: -r["n_pmids"])
print(f"\nArm B: {len(rows)} distinct lexicon names in titles/abstracts, calls={CALLS['n']}")
for r in rows[:50]:
    print(f"  {r['drug']:<32} {r['n_pmids']:>3}  {','.join(r['queries'])}  {r['pmids'][:3]}")

json.dump({"counts": counts, "rows": rows, "calls": CALLS["n"]},
          open(f"{OUT}/armB_raw.json", "w"), indent=1)
