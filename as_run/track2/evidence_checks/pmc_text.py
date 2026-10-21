import sys, re, html
import xml.etree.ElementTree as ET
# usage: pmc_text.py file.xml out.txt  -> one paragraph per line, prefixed with section title
root = ET.parse(sys.argv[1]).getroot()
out = []
def walk(el, sec):
    for ch in el:
        tag = ch.tag.split('}')[-1]
        if tag == 'sec':
            t = ch.find('title')
            s = ''.join(t.itertext()).strip() if t is not None else sec
            walk(ch, s)
        elif tag == 'p':
            txt = ' '.join(''.join(ch.itertext()).split())
            out.append(f"[{sec}] {txt}")
        elif tag in ('abstract','body','front','back','article','sub-article'):
            walk(ch, sec or tag)
        elif tag in ('title','label','fig','table-wrap','ref-list'):
            continue
        else:
            walk(ch, sec)
for body in root.iter():
    pass
walk(root, '')
open(sys.argv[2], 'w').write('\n'.join(out))
print(len(out), 'paragraphs')
