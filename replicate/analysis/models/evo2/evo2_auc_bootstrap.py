import csv, random
rows=list(csv.DictReader(open("evo2_rule_controls_out.tsv"),delimiter="\t"))
ctrl={r["id"]:r for r in csv.DictReader(open("controls_rule.tsv"),delimiter="\t")}
def auc(pos,neg):
    s=0.0
    for p in pos:
        for n in neg:
            s += 1.0 if p>n else (0.5 if p==n else 0.0)
    return s/(len(pos)*len(neg))
def score(sub):
    P=[-float(r["delta"]) for r in sub if ctrl[r["id"]]["label"]=="1"]
    B=[-float(r["delta"]) for r in sub if ctrl[r["id"]]["label"]=="0"]
    a=auc(P,B)
    random.seed(1); bs=[]
    for _ in range(2000):
        pp=[random.choice(P) for _ in P]; bb=[random.choice(B) for _ in B]
        bs.append(auc(pp,bb))
    bs.sort()
    return len(P),len(B),round(a,3),round(bs[49],3),round(bs[1949],3)
print("ALL      n_P, n_B, AUC, CI_low, CI_high:", score(rows))
for csq in ["missense","nonsense"]:
    sub=[r for r in rows if ctrl[r["id"]]["csq"]==csq]
    print(csq.ljust(8), score(sub))
