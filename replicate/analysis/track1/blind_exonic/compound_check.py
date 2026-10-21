import collections, os
F = os.environ["REPL_OUT"] + "/child_exonic_consequence.tsv"
rows = [l.rstrip("\n").split("\t") for l in open(F)][1:]
seen = {}
for r in rows: seen.setdefault((r[0], r[1], r[2], r[3]), r)
PA = {"nonsense", "frameshift", "missense", "inframe_indel", "stop_lost", "splice_region"}
LOF = {"nonsense", "frameshift", "splice_region"}
prot = [r for r in seen.values() if r[12] in PA and r[9] in ("rare", "unobserved")]
print("BUB1B rows:", [(r[1], r[12], r[9], r[4]) for r in prot if r[11] == "BUB1B"])
g = collections.defaultdict(list)
for r in prot: g[r[11]].append(r)
cand = {k: v for k, v in g.items() if any(x[12] in LOF for x in v) and any(x[12] == "missense" for x in v) and sum(1 for x in v if x[4] in ("0/1","0|1","1|0")) >= 2}
print("genes with a LoF-type het and a missense het (possible compound het, phase unknown):", len(cand))
for k in sorted(cand, key=lambda k: -len(cand[k]))[:30]:
    print(k, "; ".join(f"{x[1]} {x[12]} {x[9]} {x[4]}" for x in cand[k][:4]))
print("homozygous protein-altering rare or unobserved, all:", sum(1 for r in prot if r[4] in ("1/1","1|1")))
