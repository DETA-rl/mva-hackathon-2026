# Blind pass over child exonic calls after gnomAD matching. Summarises rarity classes per gene. No gene prior is used to select.
import glob, collections, sys
D = __import__("os").environ["REPL_OUT"] + "/"
RARE = 0.001
rows = []
for f in sorted(glob.glob(D + "child_exonic_gnomad_exomes.part*.tsv")):
    for i, line in enumerate(open(f)):
        if i == 0 or not line.strip():
            continue
        rows.append(line.rstrip("\n").split("\t"))
print("rows", len(rows))
status = collections.Counter(r[7] for r in rows)
print("gnomAD status:", dict(status))
def af(r):
    try:
        return float(r[8])
    except ValueError:
        return None
rare = []
for r in rows:
    a = af(r)
    if r[7] in ("absent_site", "site_present_alt_absent", "not_in_exome_release"):
        cls = "absent_in_gnomad_exomes"
    elif r[7] == "found" and (a is None or a == 0.0):
        # allele present in the record but zero count after QC (AC0) or no AF: treat as unobserved
        cls = "absent_in_gnomad_exomes"
    elif a is None:
        cls = "unknown_af"
    elif a < RARE:
        cls = "rare"
    else:
        cls = "common_or_low"
    r.append(cls)
    if cls in ("rare", "absent_in_gnomad_exomes"):
        rare.append(r)
print("classes:", dict(collections.Counter(r[-1] for r in rows)))
# Per gene: rare hets, rare homs, and genes with >=2 rare calls (possible compound-het pair; phase unknown)
per = collections.defaultdict(list)
for r in rare:
    per[r[6]].append(r)
pairs = {g: v for g, v in per.items() if len(v) >= 2}
print("genes with >=2 rare exonic calls:", len(pairs))
for g in sorted(pairs, key=lambda g: -len(pairs[g]))[:60]:
    v = pairs[g]
    desc = "; ".join(f"{r[0]}:{r[1]} {r[2]}>{r[3]} {r[4]} AF={r[8]} {r[-1]}" for r in v[:4])
    print(f"{g} n={len(v)} :: {desc}")
homs = [r for r in rare if r[4] in ("1/1", "1|1")]
print("rare homozygous exonic calls:", len(homs))
for r in homs[:40]:
    print("  HOM", r[6], r[0]+":"+r[1], r[2]+">"+r[3], r[7], r[8], r[-1])
