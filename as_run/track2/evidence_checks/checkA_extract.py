import sys, re, html, os
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
RAW = "/private/tmp/[redacted]/scratchpad/t2/evidence/checkA_raw/"
OUT = "/private/tmp/[redacted]/scratchpad/t2/evidence/checkA_txt/"

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def from_pmc_xml(path):
    tree = ET.parse(path)
    lines = []
    for el in tree.iter():
        tag = el.tag.split('}')[-1]
        if tag in ("article-title", "abstract", "p", "title", "sec"):
            if tag in ("p",):
                t = norm("".join(el.itertext()))
                if t: lines.append(("[%s] " % tag) + t)
            elif tag in ("article-title", "title"):
                t = norm("".join(el.itertext()))
                if t: lines.append("## " + t)
    return lines

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.out=[]; self.buf=None; self.skip=0; self.tag=None
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style","nav","header","footer","noscript"): self.skip+=1
        if tag in ("p","h1","h2","h3","h4","li","figcaption","blockquote"):
            self.buf=[]; self.tag=tag
    def handle_endtag(self, tag):
        if tag in ("script","style","nav","header","footer","noscript") and self.skip: self.skip-=1
        if tag == self.tag and self.buf is not None:
            t = norm("".join(self.buf))
            if t: self.out.append(("## " if tag.startswith("h") else "[%s] " % tag) + t)
            self.buf=None; self.tag=None
    def handle_data(self, d):
        if self.buf is not None and not self.skip: self.buf.append(d)

def from_html(path):
    p = P(); p.feed(open(path, encoding="utf-8", errors="ignore").read())
    return p.out

def run(pmid, kind, src):
    if kind == "xml": lines = from_pmc_xml(RAW+src)
    elif kind == "html": lines = from_html(RAW+src)
    else: lines = [norm(open(RAW+src).read())]
    seen=set(); res=[]
    for l in lines:
        if l not in seen: seen.add(l); res.append(l)
    open(OUT+"%s.txt" % pmid, "w").write("\n".join(res)+"\n")
    print(pmid, kind, len(res), "lines", sum(len(x) for x in res), "chars")

jobs = [
 ("15655110","html","web_PMC545877.html"),
 ("20516114","xml","PMC2887387.xml"),
 ("23242215","xml","PMC3707109.xml"),
 ("23789096","xml","PMC3654266.xml"),
 ("24344301","html","web_PMC3910577.html"),
 ("24825348","html","web_PMC4194088.html"),
 ("25614443","html","web_PMC4415018.html"),
 ("15475955","txt","abs_15475955.txt"),
 ("18932004","txt","abs_18932004.txt"),
 ("25285631","txt","abs_25285631.txt"),
]
for j in jobs: run(*j)
