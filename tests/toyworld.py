"""A synthetic genome, annotation and data set for the tests. No real data of any person is used.

Two coding transcripts on chr1 (one per strand), each with two coding exons and short UTRs, embedded in random
sequence with a fixed seed. Everything the ported scripts read is generated here: FASTA (+ .fai), GENCODE-style
GTF, VCF (+ .tbi), exon BED, gnomAD-style frequency parts, ClinVar-style VCF, HPO files and DepMap-style tables.
"""
from __future__ import annotations

import gzip
import os
import random

import pysam

CODON = {}
_b = "TCAG"
_aa = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
_i = 0
for x in _b:
    for y in _b:
        for z in _b:
            CODON[x + y + z] = _aa[_i]
            _i += 1
COMP = {"A": "T", "C": "G", "G": "C", "T": "A", "N": "N"}


def rc(s):
    return "".join(COMP[b] for b in reversed(s))


# coding sequence in transcript orientation: M A W K P G F S L Q Y *
CDS = "ATGGCTTGGAAACCCGGGTTTTCCTTACAATACTAA"
UTR5, UTR3 = "GGCAC", "TTGCA"
SPLIT = 13                      # first coding exon = CDS[:13], second = CDS[13:]


class Tx:
    """Positions (1-based, genome) of one toy transcript."""

    def __init__(self, tid, gene, strand, exons, cds):
        self.tid, self.gene, self.strand, self.exons, self.cds = tid, gene, strand, exons, cds

    def cds_positions(self):
        """Genome position of every CDS base, in transcript order."""
        pos = []
        for s, e in sorted(self.cds):
            pos.extend(range(s, e + 1))
        return pos if self.strand == "+" else pos[::-1]


def build_genome(seed=7):
    rng = random.Random(seed)
    rnd = lambda n: "".join(rng.choice("ACGT") for _ in range(n))
    ex1 = UTR5 + CDS[:SPLIT]
    ex2 = CDS[SPLIT:] + UTR3
    intron = "GT" + rnd(36) + "AG"
    seq = rnd(100)
    # plus-strand transcript GENEP
    p_e1s = len(seq) + 1
    seq += ex1
    p_e1e = len(seq)
    seq += intron
    p_e2s = len(seq) + 1
    seq += ex2
    p_e2e = len(seq)
    seq += rnd(200)
    # minus-strand transcript GENEM: genome carries revcomp(ex2) first, then revcomp(intron), then revcomp(ex1)
    m_e2s = len(seq) + 1
    seq += rc(ex2)
    m_e2e = len(seq)
    seq += rc(intron)
    m_e1s = len(seq) + 1
    seq += rc(ex1)
    m_e1e = len(seq)
    seq += rnd(300)
    txp = Tx("ENSTTOYP.1", "GENEP", "+", [(p_e1s, p_e1e), (p_e2s, p_e2e)],
             [(p_e1s + len(UTR5), p_e1e), (p_e2s, p_e2e - len(UTR3))])
    txm = Tx("ENSTTOYM.1", "GENEM", "-", [(m_e2s, m_e2e), (m_e1s, m_e1e)],
             [(m_e2s + len(UTR3), m_e2e), (m_e1s, m_e1e - len(UTR5))])
    return seq, [txp, txm]


def write_fasta(path, seq, name="chr1"):
    with open(path, "w") as fh:
        fh.write(f">{name}\n")
        for k in range(0, len(seq), 60):
            fh.write(seq[k:k + 60] + "\n")
    pysam.faidx(path)


def write_gtf(path, txs):
    lines = []
    for t in txs:
        attr = (f'gene_id "{t.gene}_ID"; transcript_id "{t.tid}"; gene_type "protein_coding"; gene_name "{t.gene}"; '
                f'transcript_type "protein_coding"; tag "basic"; tag "Ensembl_canonical";')
        s0 = min(s for s, _ in t.exons)
        e0 = max(e for _, e in t.exons)
        lines.append(f"chr1\ttoy\tgene\t{s0}\t{e0}\t.\t{t.strand}\t.\tgene_id \"{t.gene}_ID\"; gene_type \"protein_coding\"; gene_name \"{t.gene}\";")
        for s, e in t.exons:
            lines.append(f"chr1\ttoy\texon\t{s}\t{e}\t.\t{t.strand}\t.\t{attr}")
        for s, e in t.cds:
            lines.append(f"chr1\ttoy\tCDS\t{s}\t{e}\t.\t{t.strand}\t0\t{attr}")
    with gzip.open(path, "wt") as fh:
        fh.write("##description: toy annotation for tests\n" + "\n".join(lines) + "\n")


def truth_class(t: Tx, i, alt_tx):
    """Consequence of changing CDS base i (transcript orientation) to alt_tx, from the CDS string itself."""
    codon0 = (i // 3) * 3
    cod = CDS[codon0:codon0 + 3]
    mut = cod[:i - codon0] + alt_tx + cod[i - codon0 + 1:]
    a0, a1 = CODON[cod], CODON[mut]
    if a0 == "*" and a1 != "*":
        return "stop_lost"
    if a1 == "*" and a0 != "*":
        return "nonsense"
    return "synonymous" if a0 == a1 else "missense"


def snv_at(t: Tx, seq, i, alt_tx):
    """Genome-strand (pos, ref, alt) for a change of CDS base i to alt_tx."""
    g = t.cds_positions()[i]
    ref = seq[g - 1]
    alt = alt_tx if t.strand == "+" else COMP[alt_tx]
    return g, ref, alt
