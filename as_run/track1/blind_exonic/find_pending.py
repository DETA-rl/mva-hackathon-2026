import collections
D="/home/[redacted]/Documents/HACKATON/_private/blind_gnomad/"
calls=[]
for line in open(D+"child_exonic_calls.tsv"):
    if line.startswith("chrom"): continue
    c,p,r,a,gt,flt,genes=line.rstrip("\n").split("\t"); calls.append((c,int(p),r,a))
calls.sort(key=lambda x:(x[0],x[1]))
regions=[]
for c,p,r,a in calls:
    if regions and regions[-1][0]==c and p-regions[-1][2]<200000:
        regions[-1][2]=p; regions[-1][3].append((c,p,r,a))
    else:
        regions.append([c,p,p,[(c,p,r,a)]])
done=set()
for line in open(D+"child_exonic_gnomad_exomes.part3.tsv"):
    f=line.rstrip("\n").split("\t")
    if len(f)>=8 and f[0]!="chrom": done.add((f[0],f[1],f[2],f[3]))
pending=[]
for i,(c,s,e,items) in enumerate(regions):
    if i%4!=3: continue
    todo=[it for it in items if (it[0],str(it[1]),it[2],it[3]) not in done]
    if todo: pending.append((i,c,s,e,len(items),len(todo)))
print("first pending w3 regions:", pending[:3])
