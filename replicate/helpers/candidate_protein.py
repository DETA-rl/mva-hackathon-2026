"""Harness helper, not an analysis script: protein notation for the candidate's calls.

Uses the corrected consequence code itself (replicate/analysis/track1/blind_exonic/consequence_fixed.py, the
version validated in C-FIX-02): its tables and functions are loaded the same way validate_consequence.py loads
them (text before the per-call loop). Input: REPL_CANDIDATE_CALLS (JSON list of calls with transcript).
Output: the same list with aa_pos, ref_aa, alt_aa and protein (for example X123Y or X123*), printed as JSON.
"""
import json
import os

src = os.environ["REPL_CONSEQUENCE_SCRIPT"]
text = open(src).read().split("\nrows = []")[0]
ns = {"__name__": "consequence_fixed"}
exec(compile(text, src, "exec"), ns)

out = []
for c in json.loads(os.environ["REPL_CANDIDATE_CALLS"]):
    tid = c["transcript"]
    t = ns["tx"][tid]
    c["strand"] = t["strand"]
    if len(c["ref"]) == 1 and len(c["alt"]) == 1:
        off = ns["cds_offset"](tid, int(c["pos"]))
        seq, _ = ns["cds_seq"](tid)
        codon0 = (off // 3) * 3
        k = off - codon0
        cod = seq[codon0:codon0 + 3]
        alt = c["alt"].upper() if t["strand"] == "+" else ns["COMP"].get(c["alt"].upper(), "N")
        mut = cod[:k] + alt + cod[k + 1:]
        ref_aa, alt_aa = ns["CODON"].get(cod, "X"), ns["CODON"].get(mut, "X")
        c.update(aa_pos=codon0 // 3 + 1, ref_aa=ref_aa, alt_aa=alt_aa, protein=f"{ref_aa}{codon0 // 3 + 1}{alt_aa}")
    else:
        c.update(aa_pos=None, ref_aa=None, alt_aa=None, protein=None)
    out.append(c)
print(json.dumps(out))
