import re, glob, os, collections
base = "/private/tmp/[redacted]/scratchpad/hackaton_private/NLP/research/"
files = sorted(f for f in glob.glob(base + "*.md") if re.match(r"(\d\d)-", os.path.basename(f)) and int(os.path.basename(f)[:2]) <= 30)
cnt = collections.Counter(); titles = {}; srcs = collections.defaultdict(set)
for f in files:
    tag = os.path.basename(f)[:2]
    for line in open(f, encoding="utf-8", errors="replace"):
        m = re.match(r"^\[\d+\]:\s+(\S+)\s*(.*)$", line)
        if not m: continue
        url = re.sub(r"\?utm_source=chatgpt\.com", "", m.group(1))
        t = m.group(2).strip()
        cnt[url] += 1; srcs[url].add(tag)
        if t and url not in titles: titles[url] = t[:120]
print("total unique refs", len(cnt))
for url, n in cnt.most_common(90):
    print(n, sorted(srcs[url])[:6], url[:70], "|", titles.get(url, "")[:110])
