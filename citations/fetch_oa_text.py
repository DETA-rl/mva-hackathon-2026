import json,os,re,time,urllib.request,glob
UA={"User-Agent":"Mozilla/5.0"}
rows=[]
for mp in sorted(glob.glob("papers/*/meta.json")):
    m=json.load(open(mp)); d=os.path.dirname(mp)
    if not (m.get("open_access") and m.get("pmcid")): continue
    try:
        x=urllib.request.urlopen(urllib.request.Request(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{m['pmcid']}/fullTextXML",headers=UA),timeout=60).read().decode("utf-8","replace")
    except Exception as e:
        m["fulltext"]="not redistributable via Europe PMC (author manuscript / no CC license): read at "+m["pubmed_url"]; json.dump(m,open(mp,"w"),indent=1,ensure_ascii=False); print("NO ",m["key"]); continue
    lic=re.search(r'<license[^>]*xlink:href="([^"]+)"',x); lic=lic.group(1) if lic else ""
    open(f"{d}/fulltext.xml","w").write(x)
    body=re.sub(r"<(/p|/title|/sec)>","\n",x); body=re.sub(r"<[^>]+>","",body); body=re.sub(r"\n\s*\n+","\n\n",body)
    open(f"{d}/fulltext.txt","w").write(body.strip()+"\n")
    m["fulltext"]="fulltext.xml + fulltext.txt"; m["license_url"]=lic
    json.dump(m,open(mp,"w"),indent=1,ensure_ascii=False); print("YES",m["key"],lic); time.sleep(0.4)
