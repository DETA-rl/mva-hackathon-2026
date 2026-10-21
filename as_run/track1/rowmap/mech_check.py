# POST HOC diagnostic (not pre-registered): causal-row exactness by causal and decoy consequence classes, PRIM trials.
import collections, os
SP = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/spikein/")
def first_cls(path):
    out = {}
    for l in open(path):
        f = l.rstrip("\n").split("\t")
        if f[0] == "chrom": continue
        out.setdefault(":".join(f[:4]), f[12])
    return out
cv = first_cls(SP + "spike_cons_visible.tsv"); dv = first_cls("decoy_cons.tsv")
TR = {"nonsense": "T", "frameshift": "T", "missense": "M", "splice_region": "S", "inframe_indel": "I", "stop_lost": "L"}
alle = {}
for l in open(SP + "trials.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] in ("A", "E") and f[2] == "v4": alle[f[1]] = f[5].split(";")
dec = {}
for l in open("decoy_draws.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] != "stratum": dec[f[1]] = f[3].split(";")
tab = collections.defaultdict(lambda: collections.Counter())
for l in open("trials_rowmap.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] not in ("A-CH-dec", "E-CH-dec") or f[11] != "C1": continue
    base, d = f[1].rsplit("-d", 1)
    c = "+".join(sorted(TR.get(cv.get(k, "NA"), "x") for k in alle[base]))
    dd = "+".join(sorted(TR.get(dv.get(k, "NA"), "x") for k in dec[base][:int(d)]))
    g = (c, dd)
    tab[g]["n_" + f[10]] += 1; tab[g]["ok_" + f[10]] += f[17] == "True"
print("causal\tdecoys\tN\t" + "\t".join(r for r in ("R0", "P1", "P2", "P3", "P4", "P5")))
for g, c in sorted(tab.items(), key=lambda x: -x[1]["n_R0"]):
    if c["n_R0"] < 8: continue
    print(g[0], g[1], c["n_R0"], *[round(c["ok_" + r] / c["n_" + r], 2) for r in ("R0", "P1", "P2", "P3", "P4", "P5")], sep="\t")
