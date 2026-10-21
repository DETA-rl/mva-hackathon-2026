"""PRE-REG-R2A: per-residue RSA (Shrake-Rupley, probe 1.40 A, 100 points; Tien 2013 theoretical max ASA).

Usage: python -I rsa.py <pdb> <out_csv>
"""
import csv
import sys

from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import three_to_index, index_to_one
from Bio.PDB.SASA import ShrakeRupley

# Tien et al. 2013 PLoS One, theoretical maximum ASA (A^2)
MAX_ASA = {"A": 129.0, "R": 274.0, "N": 195.0, "D": 193.0, "C": 167.0, "Q": 225.0, "E": 223.0,
           "G": 104.0, "H": 224.0, "I": 197.0, "L": 201.0, "K": 236.0, "M": 224.0, "F": 240.0,
           "P": 159.0, "S": 155.0, "T": 172.0, "W": 285.0, "Y": 263.0, "V": 174.0}

st = PDBParser(QUIET=True).get_structure("x", sys.argv[1])
ShrakeRupley(probe_radius=1.40, n_points=100).compute(st[0], level="R")
with open(sys.argv[2], "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["resnum", "aa", "sasa", "rsa"])
    for r in st[0]["A"]:
        aa = index_to_one(three_to_index(r.get_resname()))
        w.writerow([r.id[1], aa, f"{r.sasa:.2f}", f"{r.sasa / MAX_ASA[aa]:.4f}"])
