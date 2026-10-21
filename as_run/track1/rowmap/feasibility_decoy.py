# Pre-freeze feasibility, PUBLIC ClinVar only (no child data, no ranking, no consequence step):
# per-gene counts of non-P/LP records that look like rare coding decoys by ClinVar MC and AF fields.
import collections, gzip, json, os, re
D = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/")
SET18 = ["RNU4ATAC","RNU6ATAC","ZRSR2","SNRNP48","ESCO2","PCNT","CENPF","BUB1B","TRIP13","CEP57","SMC5","MAD1L1","CEP192","TRIM37","CDC20","MAD2L1BP","CENATAC","SLF2"]
NONPLP = {"Uncertain_significance","Likely_benign","Benign","Benign/Likely_benign","Conflicting_classifications_of_pathogenicity","Conflicting_interpretations_of_pathogenicity"}
CODING = re.compile(r"missense_variant|nonsense|frameshift_variant|splice_donor|splice_acceptor|inframe_|stop_lost")
AUTO = {str(i) for i in range(1, 23)}
last = {}; rec = {}
for l in gzip.open(D + "clinvar.vcf.gz", "rt"):
    if l[0] == "#": continue
    c = l.rstrip("\n").split("\t")
    ch = c[0].replace("chr", ""); alts = c[4].split(",")
    sig = c[7].split("CLNSIG=")[1].split(";")[0] if "CLNSIG=" in c[7] else "NA"
    for a in alts: last[(ch, c[1], c[3], a)] = sig
    if len(alts) != 1 or ch not in AUTO: continue
    if not re.fullmatch("[ACGT]{1,50}", c[3]) or not re.fullmatch("[ACGT]{1,50}", alts[0]): continue
    info = dict(kv.split("=", 1) for kv in c[7].split(";") if "=" in kv)
    if not info.get("GENEINFO"): continue
    rec[(ch, c[1], c[3], alts[0])] = info
cnt = collections.Counter()
for k, info in rec.items():
    if last[k] not in NONPLP: continue
    if not CODING.search(info.get("MC", "")): continue
    af = info.get("AF_EXAC") or info.get("AF_ESP") or info.get("AF_TGP")
    if af is not None and float(af) >= 0.001: continue
    for g in [x.split(":")[0] for x in info["GENEINFO"].split("|")]: cnt[g] += 1
out = {"set18_autosomal_decoy_like_counts": {g: cnt.get(g, 0) for g in SET18}, "genes_with_ge2": sum(1 for v in cnt.values() if v >= 2)}
json.dump(out, open("feasibility_decoy.json", "w"), indent=1); print(json.dumps(out))
