import sys, xml.etree.ElementTree as ET, re
src, dst = sys.argv[1], sys.argv[2]
root = ET.parse(src).getroot()
out = []
def txt(el):
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
if root.tag.endswith('PubmedArticleSet'):
    for art in root.iter('PubmedArticle'):
        for ab in art.iter('AbstractText'):
            lab = ab.get('Label')
            out.append(('[ABSTRACT' + (f' {lab}' if lab else '') + '] ') + txt(ab))
else:
    for art in root.iter('article'):
        for ab in art.iter('abstract'):
            for p in ab.iter('p'):
                out.append('[ABSTRACT] ' + txt(p))
        body = art.find('body')
        if body is not None:
            def walk(el, depth, title):
                for ch in el:
                    tag = ch.tag
                    if tag == 'sec':
                        t = ch.find('title')
                        tt = txt(t) if t is not None else ''
                        out.append(f'[SECTION] {tt}')
                        walk(ch, depth+1, tt)
                    elif tag == 'p':
                        out.append(f'[{title}] ' + txt(ch))
                    elif tag in ('list','boxed-text','disp-quote'):
                        for p in ch.iter('p'):
                            out.append(f'[{title}] ' + txt(p))
            walk(body, 0, 'BODY')
open(dst,'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(dst, len(out), 'lines')
