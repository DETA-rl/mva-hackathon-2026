import json, urllib.request, sys

B = "https://gtexportal.org/api/v2"


def get(p):
    with urllib.request.urlopen(B + p, timeout=90) as r:
        return json.load(r)


GENES = ["IREB2", "CHD2", "SPRED1", "FBN1", "IDH2", "MFGE8", "ALDH1A2", "RORA", "CSK", "IGF1R",
         "NUSAP1", "TP53BP1", "PML", "CYP1A1", "HERC2", "OCA2", "FES", "MAP2K1", "SEMA6D", "AP4E1"]
TISSUE = sys.argv[1] if len(sys.argv) > 1 else "Whole_Blood"
for sym in GENES:
    try:
        g = get(f"/reference/gene?geneId={sym}&gencodeVersion=v26&genomeBuild=GRCh38%2Fhg38")["data"][0]["gencodeId"]
        r = get(f"/association/singleTissueEqtl?gencodeId={g}&tissueSiteDetailId={TISSUE}&datasetId=gtex_v8")
        d = r.get("data", [])
        print(sym, g, "n=", len(d), "keys=", list(d[0].keys())[:12] if d else "")
        if d:
            print("  example:", {k: d[0][k] for k in d[0] if k in ("variantId", "nes", "pValue", "snpId", "pos", "chromosome")})
    except Exception as e:
        print(sym, "ERR", repr(e)[:200])
