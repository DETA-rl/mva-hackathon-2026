"""Fetch titles for the PMIDs that BATCHES.md lists as the source for the literature
co-occurrence rows in Batch 4 items 50-98. PMIDs only leave this machine."""
import json, urllib.request
OUT="/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
PMIDS="33186389,34304612,36245843,36389792,40273626,40595080,39949372,41053901,33708237,34147108,38410481,38987356,41579174,42330849,41381790,34035233,37808164,20442314,36567949,40565600,41169944,33244299,33922244,39911278,31942195,42168250,42483440,40209578,41516135,42146413,40068082,39045407,40750410,31987036,32121037,32850387,31853539,34919076,32154490,34545188,31877723,41184881"
u="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="+PMIDS
with urllib.request.urlopen(u, timeout=60) as r: d=json.load(r)
res=d["result"]
out={}
for pid in res.get("uids",[]):
    rec=res[pid]
    out[pid]={"title":rec.get("title",""),"journal":rec.get("source",""),"year":rec.get("pubdate","")[:4]}
    print(pid,"|",rec.get("pubdate","")[:4],"|",rec.get("title","")[:160])
with open(OUT+"lit_titles.json","w") as f: json.dump(out,f,indent=1)
