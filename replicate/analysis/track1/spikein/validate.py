# Gate G1: the parametrized copies and the ranking library reproduce the frozen outputs on the REAL, unspiked data.
# No spike-in is used here. Writes val_* files in the work dir only.
import csv, filecmp, gzip, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spikelib as L
D, W = L.D, L.W
PY = sys.executable
res = {}
# G1a consequence_param.py on the original part tables == child_exonic_consequence_fixed.tsv
subprocess.run([PY, W + "consequence_param.py", D + "child_exonic_gnomad_exomes.part*.tsv", W + "val_consequence_orig.tsv"], check=True)
res["G1a_consequence_identical"] = filecmp.cmp(W + "val_consequence_orig.tsv", D + "child_exonic_consequence_fixed.tsv", shallow=False)
# G1b calls_param.py: the first 3000 rows of child_exonic_calls.tsv as a VCF must come back unchanged
allrows = [l.rstrip("\n").split("\t") for l in open(D + "child_exonic_calls.tsv")]
res["G1b_header"] = allrows[0]
rows = allrows[1:3001] + allrows[-3000:]
with gzip.open(W + "val_calls_in.vcf.gz", "wt") as fh:
    fh.write("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS\n")
    for c, p, r, a, gt, flt, g in rows:
        fh.write(f"{c}\t{p}\t.\t{r}\t{a}\t.\t{flt}\t.\tGT\t{gt}\n")
subprocess.run([PY, W + "calls_param.py", W + "val_calls_in.vcf.gz", W + "val_calls_out.tsv"], check=True)
back = [l.rstrip("\n").split("\t") for l in open(W + "val_calls_out.tsv")]
res["G1b_calls_roundtrip_identical"] = back[1:] == rows and back[0] == allrows[0]
# G1c/d ranking library == frozen summaries
cons = L.read_consequence(D + "child_exonic_consequence_fixed.tsv")
seen = L.seen_from_rows(cons)
cands = L.v3_candidates(seen.values())
clin = L.clinvar_lookup({L.key(f) for f in cands})
o3, t3, g3 = L.rank_v3(cands, clin)
open(W + "val_v3_summary.tsv", "w").writelines(L.v3_summary_lines(o3, t3, g3))
res["G1c_v3_summary_identical"] = filecmp.cmp(W + "val_v3_summary.tsv", D + "ranking_v3_summary_fixed.tsv", shallow=False)
o4, tiers4, ph4 = L.rank_v4(o3, t3, g3, amendment1=False)
open(W + "val_v4_summary_noamend.tsv", "w").writelines(L.v4_summary_lines(tiers4, ph4))
res["G1d_v4_summary_identical"] = filecmp.cmp(W + "val_v4_summary_noamend.tsv", D + "ranking_v4_summary_fixed.tsv", shallow=False)
# G1e Amendment 1 top 10 and ROW-MAP rows == TRACK1 draft rows
o4a, _, _ = L.rank_v4(o3, t3, g3, amendment1=True)
draft = list(csv.DictReader(open(os.environ["REPL_DRAFT_CSV"])))
def dkeys(r):
    ks = [(r["chrom_1"].replace("chr", ""), r["pos_1"], r["ref_1"], r["alt_1"])]
    if r["chrom_2"]: ks.append((r["chrom_2"].replace("chr", ""), r["pos_2"], r["ref_2"], r["alt_2"]))
    return set(ks)
mine = [set(L.row_map(g3[g])) for g in o4a[:10]]
res["G1e_amended_top10"] = o4a[:10]
res["G1e_rows_equal_draft"] = mine == [dkeys(r) for r in draft]
res["G1e_mt_genes_in_unamended_top10"] = [g for g in o4[:10] if g.startswith("MT-")]
json.dump(res, open(W + "val_G1.json", "w"), indent=1)
print(json.dumps(res, indent=1))
