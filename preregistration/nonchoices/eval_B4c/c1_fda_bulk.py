# C1 regulatory class from the public Drugs@FDA bulk files already on this box.
# Public data only. Drug names only. No patient data. Reads, never writes outside this dir.
import csv, sys, collections
D="/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/dl_fda/"
names=[n.strip() for n in open(sys.argv[1]) if n.strip()]
look={}
for r in csv.DictReader(open(D+"MarketingStatus_Lookup.txt"),delimiter="\t"):
    look[r["MarketingStatusID"].strip()]=r["MarketingStatusDescription"].strip()
ms=collections.defaultdict(set)
for r in csv.DictReader(open(D+"MarketingStatus.txt"),delimiter="\t"):
    ms[(r["ApplNo"].strip(),r["ProductNo"].strip())].add(look.get(r["MarketingStatusID"].strip(),"?"))
prods=list(csv.DictReader(open(D+"Products.txt"),delimiter="\t"))
out=[]
for n in names:
    key=n.lower()
    hits=[]
    for p in prods:
        ing=(p.get("ActiveIngredient") or "").lower(); dn=(p.get("DrugName") or "").lower()
        if key in ing or key in dn:
            hits.append((p["ApplNo"].strip(),p["ProductNo"].strip(),p.get("Form",""),p.get("DrugName","")))
    st=collections.Counter()
    forms=collections.Counter()
    appls=set()
    for a,pn,form,dn in hits:
        appls.add(a)
        for s in ms.get((a,pn),{"not in MarketingStatus.txt"}): st[s]+=1
        forms[form.split(";")[0].strip()]+=1
    out.append((n,len(hits),len(appls),dict(st),[f for f,_ in forms.most_common(4)]))
w=csv.writer(sys.stdout,delimiter="\t")
w.writerow(["drug","product_rows","applications","marketing_status_counts","top_forms"])
for r in out: w.writerow(r)
