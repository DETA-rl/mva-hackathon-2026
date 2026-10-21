import sys, re, html
import xml.etree.ElementTree as ET
for f in sys.argv[1:]:
    root = ET.parse(f).getroot()
    print("=====", f)
    for art in root.iter('PubmedArticle'):
        t = art.find('.//ArticleTitle')
        print("TITLE:", ''.join(t.itertext()) if t is not None else None)
        for ab in art.iter('AbstractText'):
            label = ab.get('Label')
            txt = ''.join(ab.itertext())
            print(f"[{label or ''}] {txt}")
