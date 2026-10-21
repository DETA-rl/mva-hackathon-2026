import collections, os
F = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/child_exonic_consequence.tsv")
rows = [l.rstrip("\n").split("\t") for l in open(F)][1:]
print("consequence rows (per transcript-call):", len(rows))
print("consequence counts:", dict(collections.Counter(r[12] for r in rows)))
PA = {"nonsense", "frameshift", "missense", "inframe_indel", "stop_lost", "splice_region"}
seen = {}
for r in rows:
    key = (r[0], r[1], r[2], r[3])
    seen.setdefault(key, r)  # first canonical transcript for each call
prot = [r for r in seen.values() if r[12] in PA and r[9] in ("rare", "unobserved")]
print("protein-altering rare or unobserved calls (first canonical transcript):", len(prot))
print("  by consequence:", dict(collections.Counter(r[12] for r in prot)))
print("  by class:", dict(collections.Counter(r[9] for r in prot)))
hom = [r for r in prot if r[4] in ("1/1", "1|1")]
print("  homozygous:", len(hom))
genes = collections.defaultdict(list)
for r in prot:
    genes[r[11]].append(r)
multi = {g: v for g, v in genes.items() if len(v) >= 2}
print("genes with >=2 protein-altering rare or unobserved calls:", len(multi))
for g in sorted(multi, key=lambda g: -len(multi[g]))[:25]:
    v = multi[g]
    print(f"{g} n={len(v)} hom={sum(1 for r in v if r[4] in ('1/1','1|1'))} :: " + "; ".join(f"{r[0]}:{r[1]} {r[12]} {r[9]} {r[4]}" for r in v[:3]))
nonsense_fs_hom = [r for r in prot if r[12] in ("nonsense", "frameshift") and r[4] in ("1/1", "1|1")]
print("homozygous nonsense or frameshift, rare or unobserved:", len(nonsense_fs_hom))
for r in nonsense_fs_hom[:30]:
    print("  ", r[11], r[0]+":"+r[1], r[2]+">"+r[3], r[12], r[9], r[4])
nonsense_fs_het = [r for r in prot if r[12] in ("nonsense", "frameshift") and r[4] in ("0/1", "0|1", "1|0")]
print("heterozygous nonsense or frameshift, rare or unobserved:", len(nonsense_fs_het))
for r in nonsense_fs_het[:40]:
    print("  ", r[11], r[0]+":"+r[1], r[2]+">"+r[3], r[12], r[9], r[4])
