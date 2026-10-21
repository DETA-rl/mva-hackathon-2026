"""Scan a tree before publication: file contents, file names and (for a git repository) the whole history with
its commit metadata.

Usage:
  python tools/leak_scan.py DIR [--patterns FILE] [--allow-email ADDRESS] [--quiet]

Two kinds of finding.

FAIL (exit code 1): anything that identifies our machines or accounts, or the child's data files. Built-in:
folders of a real local user (/home/<name>, /Users/<name>, /media/<name>, /private/tmp/<name>, -Users-<name>),
private and VPN IPv4 addresses, e-mail addresses, UUIDs, secret-like tokens, and files that are sequencing data
(VCF, BAM, CRAM, FASTQ or their indexes, by name or by content). --patterns FILE adds private regexes, one per line
(local user names, machine names, addresses, session names); 'i:' at the start of a line makes it case-insensitive,
'#' starts a comment. Keep that file outside the repository.

WARN (reported with every location, never a failure): the candidate's variant coordinates, protein change,
residue number and the proband label. These are our Track 1 answer and may be published; the scan lists where they
occur so a reader of the output knows. Built-in: sample-identifier patterns outside the organisers' documented file
names, and 8-9 digit numbers inside the candidate neighbourhoods (except the public positions listed below);
private patterns prefixed 'c:' are reported the same way.
"""
import argparse
import os
import re
import subprocess
import sys

ORGANISER_FILE = re.compile(r"WGS_EX\d{6,8}_[A-Z0-9]{5}DSX\d(?:\.vcf\.gz(?:\.tbi)?|_S\d+_L00[1-4]_R[12]_001\.fastq\.gz)")
GENERIC = {
    "local user folder": re.compile(r"/(?:home|Users|media)/(?!\[redacted\]|<|\()[^/\s'\"`]+|/private/tmp/(?!\[redacted\]|<|\()[^/\s'\"`]+"
                                    r"|-Users-[A-Za-z]|[A-Z]:\\Users\\"),
    "private or VPN IPv4": re.compile(r"(?<![\w.=/-])(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7]))"
                                      r"\.\d{1,3}\.\d{1,3}(?![\d.])"),
    "e-mail address": re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    "UUID": re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
    "secret-like token": re.compile(r"hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
                                    r"|-----BEGIN [A-Z ]*PRIVATE KEY"),
    "sample-identifier pattern": re.compile(r"\bEX\d{6,8}\b|\b[A-Z0-9]{5}DSX\d\b|PROBAND\d+"),
}
NEIGHBOURHOOD = "number inside a candidate neighbourhood"
WARN = {"sample-identifier pattern", NEIGHBOURHOOD}       # plus every 'c:' private pattern
DATA_FILE = re.compile(r"\.(?:vcf|vcf\.gz|vcf\.bgz|bcf|bam|bai|cram|crai|fastq|fq|fastq\.gz|fq\.gz|tbi|csi)$", re.I)
ALLOWED = {"e-mail address": {"noreply@anthropic.com"}}
# candidate neighbourhoods (GRCh38) and the public positions inside them (BUB1B gene span used by H03, dbSNP
# rs576524605 tested by H02); the same rule as tests/test_harness.py
WINDOWS = [(40_100_000, 40_300_000), (118_950_000, 119_080_000)]
PUBLIC_OK = {40_160_984, 40_221_137, 40_117_087, 40_117_088}
NUMBER = re.compile(r"(?<![\d.])\d{1,3}(?:,\d{3}){2,}(?![\d])|(?<![\d.])\d{8,9}(?![\d])")


def load_private(path):
    pats = []
    for line in open(path):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        flags, child = 0, False
        while line[:2] in ("i:", "c:"):
            if line[:2] == "i:":
                flags = re.I
            else:
                child = True
            line = line[2:]
        name = f"{'answer' if child else 'private'} pattern {len(pats) + 1}"
        if child:
            WARN.add(name)
        pats.append((name, re.compile(line, flags)))
    return pats


def pdf_text(path, raw):
    """What a PDF actually carries: its rendered text and its metadata.

    A PDF's content streams are compressed, so scanning the raw bytes matches arbitrary byte
    sequences that are not text (two byte runs in a report PDF matched the e-mail pattern), while
    inside a compressed stream would not be found in the raw bytes at all. Extracted text and the
    metadata dictionary are what a reader can see, so they are what is scanned. If neither tool is
    available the raw bytes are scanned, which is the earlier behaviour.
    """
    out = []
    for cmd in (["pdftotext", "-q", path, "-"], ["pdfinfo", path]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and r.stdout:
                out.append(r.stdout)
        except (OSError, subprocess.SubprocessError):
            pass
    return "\n".join(out) if out else raw.decode("utf-8", errors="ignore")


def scan_text(text, where, pats, hits):
    bare = ORGANISER_FILE.sub("<organiser file>", text)
    for n, line in enumerate(bare.split("\n"), 1):
        for name, rx in pats:
            for m in rx.finditer(line):
                if m.group(0) in ALLOWED.get(name, ()):
                    continue
                hits.append((where, n, name, m.group(0), name in WARN))
        for m in NUMBER.findall(line):
            v = int(m.replace(",", ""))
            if any(a <= v <= b for a, b in WINDOWS) and v not in PUBLIC_OK:
                hits.append((where, n, NEIGHBOURHOOD, m, True))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    ap.add_argument("--patterns", help="private regex file (kept outside the repository)")
    ap.add_argument("--quiet", action="store_true", help="print counts only, not the matched text")
    ap.add_argument("--allow-email", action="append", default=[], help="an e-mail address that may appear (the "
                                                                          "identity chosen for the public commit)")
    a = ap.parse_args()
    ALLOWED["e-mail address"] = ALLOWED["e-mail address"] | set(a.allow_email)
    pats = list(GENERIC.items()) + (load_private(a.patterns) if a.patterns else [])
    hits, nfiles = [], 0
    for base, dirs, files in os.walk(a.dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, a.dir)
            nfiles += 1
            scan_text(rel, f"file name {rel}", pats, hits)
            with open(p, "rb") as fh:
                raw = fh.read()
            if DATA_FILE.search(f) or raw.startswith(b"##fileformat=VCF") or raw[:4] == b"BAM\x01" or \
                    (raw[:2] == b"\x1f\x8b" and f.lower().endswith((".gz", ".bgz"))):
                hits.append((rel, 0, "sequencing data file", f, False))
            body = pdf_text(p, raw) if f.lower().endswith(".pdf") else raw.decode("utf-8", errors="ignore")
            scan_text(body, rel, pats, hits)
    ncommits = 0
    if os.path.isdir(os.path.join(a.dir, ".git")):
        g = lambda *x: subprocess.run(["git", "-C", a.dir, *x], capture_output=True, text=True, check=True).stdout  # noqa: E731
        ncommits = int(g("rev-list", "--all", "--count").strip() or 0)
        scan_text(g("log", "--all", "-p", "--format=fuller", "--no-color"), "git history", pats, hits)
        scan_text(g("for-each-ref", "--format=%(refname) %(taggername) %(taggeremail)"), "git refs", pats, hits)
    failing = [h for h in hits if not h[4]]
    warned = [h for h in hits if h[4]]
    print(f"scanned {nfiles} files" + (f" and {ncommits} commit(s) of git history" if ncommits else "") +
          f" with {len(pats)} patterns: {len(failing)} failure(s), {len(warned)} warning(s)")
    for name, rows in sorted({h[2]: [x for x in failing if x[2] == h[2]] for h in failing}.items()):
        print(f"  FAIL {name}: {len(rows)}")
        if not a.quiet:
            for where, n, _, text, _ in rows[:50]:
                print(f"    {where}:{n}: {text}")
    by_file = {}
    for where, n, name, _, _ in warned:
        by_file.setdefault(where, []).append(n)
    for where, ns in sorted(by_file.items()):
        print(f"  WARN candidate variant or proband label in {where}: {len(ns)} match(es), lines "
              f"{', '.join(str(x) for x in sorted(set(ns))[:12])}{' ...' if len(set(ns)) > 12 else ''}")
    sys.exit(1 if failing else 0)


if __name__ == "__main__":
    main()
