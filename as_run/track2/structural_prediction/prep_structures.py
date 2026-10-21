"""PRE-REG-R2A: build primary / S1 / S2 structures from AlphaFold models and record pLDDT.

primary = full-length AF model minus residues with CA pLDDT < 50
S1      = unmodified full-length AF model
S2      = BUBR1 only, unmodified model cropped to [kinase start - 25, 1050]
Usage: python -I prep_structures.py <work_dir> <bubr1_kinase_start>
"""
import json
import sys
from pathlib import Path

from Bio.PDB import PDBIO, PDBParser, Select

W = Path(sys.argv[1])
KSTART = int(sys.argv[2])
D = W / "data"
O = W / "structures"
O.mkdir(exist_ok=True)


class Keep(Select):
    def __init__(self, keep):
        self.keep = keep

    def accept_residue(self, res):
        return res.id[1] in self.keep


plddt_all = {}
for acc in ["O60566", "P60484", "P51580"]:
    st = PDBParser(QUIET=True).get_structure(acc, D / f"AF_{acc}.pdb")
    chain = st[0]["A"]
    pl = {r.id[1]: r["CA"].get_bfactor() for r in chain}
    plddt_all[acc] = pl
    io = PDBIO()
    io.set_structure(st)
    io.save(str(O / f"{acc}_S1.pdb"), Keep(set(pl)))
    io.save(str(O / f"{acc}_primary.pdb"), Keep({k for k, v in pl.items() if v >= 50}))
    if acc == "O60566":
        io.save(str(O / f"{acc}_S2.pdb"), Keep({k for k in pl if KSTART - 25 <= k <= 1050}))
    n_low = sum(v < 50 for v in pl.values())
    print(acc, "residues", len(pl), "removed_pLDDT<50", n_low)

json.dump(plddt_all, open(O / "plddt.json", "w"))
