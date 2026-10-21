"""Build the protein-model control input from the rule-compliant pool (controls_rule.tsv).

Missense controls only (protein LMs score amino-acid substitutions; nonsense controls are not scorable this way).
For each control: canonical GENCODE v44 protein-coding transcript of its gene, CDS from the reference FASTA,
amino-acid position and ref/alt residues from the genomic change. Rows are kept only if the genomic ref base
matches the reference and the residue at that position matches the translated protein.
Writes a protein/controls/ folder in the layout score.py expects (controls.tsv plus one <GENE>.fasta per gene).
Usage: build_protein_rule.py <controls_rule.tsv> <out_controls_dir>
"""
import collections
import gzip
import os
import sys

import pysam

GTF = os.environ["REPL_GTF"]
FA = os.environ[
    "REPL_FASTA"]
CTRL_TSV, OUT = sys.argv[1], sys.argv[2]

bases = "TCAG"
aas = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODON, i = {}, 0
for a in bases:
    for b in bases:
        for c in bases:
            CODON[a + b + c] = aas[i]
            i += 1
COMP = {"A": "T", "C": "G", "G": "C", "T": "A", "N": "N"}

genes_needed = set()
ctrl = []
with open(CTRL_TSV) as fh:
    head = fh.readline().rstrip("\n").split("\t")
    for line in fh:
        r = dict(zip(head, line.rstrip("\n").split("\t")))
        if r["csq"] != "missense":
            continue
        r["gene"] = r["id"].rsplit("_", 1)[0]
        ctrl.append(r)
        genes_needed.add(r["gene"])
genes_needed.add("BUB1B")  # child call needs the BUB1B protein sequence

tx = {}
with gzip.open(GTF, "rt") as f:
    for line in f:
        if line[0] == "#":
            continue
        c = line.rstrip("\n").split("\t", 8)
        if c[2] not in ("exon", "CDS"):
            continue
        at = c[8]
        if 'transcript_type "protein_coding"' not in at or 'tag "Ensembl_canonical"' not in at:
            continue
        gname = at.split('gene_name "')[1].split('"')[0]
        if gname not in genes_needed:
            continue
        tid = at.split('transcript_id "')[1].split('"')[0]
        t = tx.setdefault(tid, {"gene": gname, "chrom": c[0].replace("chr", ""), "strand": c[6],
                                "exons": [], "cds": []})
        (t["exons"] if c[2] == "exon" else t["cds"]).append((int(c[3]), int(c[4])))
gene_tx = {}
for tid, t in tx.items():
    gene_tx.setdefault(t["gene"], tid)
missing = genes_needed - set(gene_tx)
print("canonical transcripts found:", len(gene_tx), "missing:", sorted(missing))

fa = pysam.FastaFile(FA)
chr_prefix = "chr" if any(x.startswith("chr") for x in fa.references) else ""


def cds_info(tid):
    t = tx[tid]
    segs = sorted(t["cds"])  # ascending; a minus-strand block must not be reversed before the whole-string reverse complement
    seq, cum = "", []
    for s, e in segs:
        cum.append((s, e, len(seq)))
        seq += fa.fetch(chr_prefix + t["chrom"], s - 1, e).upper()
    if t["strand"] == "-":
        seq = "".join(COMP.get(b, "N") for b in reversed(seq))
        L = len(seq)
        cum = [(s, e, L - off - (e - s + 1)) for s, e, off in cum]
    return seq, cum


def translate(seq):
    out = []
    for k in range(0, len(seq) - 2, 3):
        aa = CODON.get(seq[k:k + 3], "X")
        if aa == "*":
            break
        out.append(aa)
    return "".join(out)


proteins, info = {}, {}
for g, tid in gene_tx.items():
    seq, cum = cds_info(tid)
    proteins[g] = translate(seq)
    info[g] = (tid, seq, cum)

out_rows = []
dropped = collections.Counter()
for r in ctrl:
    g = r["gene"]
    if g not in info:
        dropped["no_transcript"] += 1
        continue
    tid, seq, cum = info[g]
    t = tx[tid]
    pos = int(r["pos"])
    off = None
    for s, e, o in cum:
        if s <= pos <= e:
            off = o + (pos - s) if t["strand"] == "+" else o + (e - pos)
            break
    if off is None:
        dropped["outside_cds"] += 1
        continue
    genome_ref = fa.fetch(chr_prefix + r["chrom"].replace("chr", ""), pos - 1, pos).upper()
    if genome_ref != r["ref"]:
        dropped["genome_ref_mismatch"] += 1
        continue
    codon0 = (off // 3) * 3
    k = off - codon0
    cod = seq[codon0:codon0 + 3]
    alt_base = r["alt"] if t["strand"] == "+" else COMP.get(r["alt"], "N")
    alt_cod = cod[:k] + alt_base + cod[k + 1:]
    ref_aa, alt_aa = CODON.get(cod, "X"), CODON.get(alt_cod, "X")
    aa_pos = codon0 // 3 + 1
    if proteins[g][aa_pos - 1:aa_pos] != ref_aa:
        dropped["protein_residue_mismatch"] += 1
        continue
    if alt_aa in ("X", "*") or alt_aa == ref_aa:
        dropped["not_missense_after_translation"] += 1
        continue
    out_rows.append({"gene": g, "pos": aa_pos, "ref": ref_aa, "alt": alt_aa, "label": r["label"],
                     "chrom": r["chrom"], "vcf_pos": r["pos"], "vcf_ref": r["ref"], "vcf_alt": r["alt"],
                     "review": "clinvar_rule_pool_missense"})

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "controls.tsv"), "w") as fh:
    cols = ["gene", "pos", "ref", "alt", "label", "chrom", "vcf_pos", "vcf_ref", "vcf_alt", "review"]
    fh.write("\t".join(cols) + "\n")
    for r in out_rows:
        fh.write("\t".join(str(r[c]) for c in cols) + "\n")
for g, seq in proteins.items():
    with open(os.path.join(OUT, f"{g}.fasta"), "w") as fh:
        fh.write(f">{g}\n")
        for k in range(0, len(seq), 60):
            fh.write(seq[k:k + 60] + "\n")
_cand = __import__("json").loads(__import__("os").environ.get("REPL_CANDIDATE_RESIDUE", "null")); child_ok = (proteins.get(_cand[0], "")[_cand[1] - 1:_cand[1]] == _cand[2]) if _cand else None
print("kept:", len(out_rows), "P:", sum(1 for r in out_rows if r["label"] == "1"),
      "B:", sum(1 for r in out_rows if r["label"] == "0"), "dropped:", dict(dropped))
print(f"{_cand[0]} residue {_cand[1]} is {_cand[2]} (child check):" if _cand else "candidate residue not checked (no candidate in this run) (child check):", child_ok)
