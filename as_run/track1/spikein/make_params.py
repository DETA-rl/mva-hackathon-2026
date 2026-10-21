# Builds parametrized copies of two frozen pipeline scripts by exact text replacement (input/output paths only).
# Each replacement must match exactly once; the unified diff is written next to the copy. Originals are only read.
import difflib, os, sys
D = os.path.expanduser("~/Documents/HACKATON/_private/blind_gnomad/")
W = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/spikein/")
JOBS = [
    ("consequence_fixed.py", "consequence_param.py", [
        ('sorted(__import__("glob").glob(HERE + "child_exonic_gnomad_exomes.part*.tsv"))',
         'sorted(__import__("glob").glob(__import__("sys").argv[1]))'),
        ('open(HERE + "child_exonic_consequence_fixed.tsv", "w")',
         'open(__import__("sys").argv[2], "w")'),
    ]),
    # The blind_gnomad copy of child_exonic_calls.py does not parse under Python 3.13 and writes header "gene";
    # the table on disk has header "genes", which matches this copy (sha256 fdeacbcb...).
    ("../analysis_scripts/child_exonic_calls.py", "calls_param.py", [
        ('VCF = "/home/[redacted]/Documents/HACKATON/data/WGS_EX2312012_HGWCNDSX7.vcf.gz"',
         'VCF = __import__("sys").argv[1]'),
        ('out = open(D + "child_exonic_calls.tsv", "w")',
         'out = open(__import__("sys").argv[2], "w")'),
    ]),
]
for src, dst, reps in JOBS:
    text = open(D + src).read()
    new = text
    for a, b in reps:
        n = new.count(a)
        if n != 1:
            sys.exit(f"{src}: pattern found {n} times, expected 1: {a}")
        new = new.replace(a, b)
    open(W + dst, "w").write(new)
    diff = "".join(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "blind_gnomad/" + src, dst))
    open(W + dst + ".diff", "w").write(diff)
    print(dst, "written;", sum(1 for l in diff.splitlines() if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))), "changed lines")
