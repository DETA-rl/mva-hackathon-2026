"""PRE-REG-R2A: ThermoMPNN site-saturation ddG on one PDB chain (local weights, no network).

Loads the published Lightning checkpoint into TransferModel directly (no pytorch_lightning
or wandb needed). Output CSV: resnum, wildtype, mutation, ddG (positive = destabilising).
Usage: CUDA_VISIBLE_DEVICES=1 PYTHONPATH=<pylib> python thermo_ssm.py <thermompnn_dir> <pdb> <out_csv> [start end]
"""
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch

TM = Path(sys.argv[1])
PDB = sys.argv[2]
OUT = sys.argv[3]
RANGE = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else None
sys.path.insert(0, str(TM))

from omegaconf import OmegaConf  # noqa: E402
from protein_mpnn_utils import alt_parse_PDB  # noqa: E402
from transfer_model import TransferModel  # noqa: E402

ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"


@dataclass
class Mutation:
    position: int
    wildtype: str
    mutation: str
    ddG: Optional[float] = None
    pdb: Optional[str] = ""


# same model config as analysis/custom_inference.py
cfg = OmegaConf.create({
    "platform": {"thermompnn_dir": str(TM), "accel": "gpu"},
    "training": {"num_workers": 8, "learn_rate": 0.001, "epochs": 100, "lr_schedule": True},
    "model": {"hidden_dims": [64, 32], "subtract_mut": True, "num_final_layers": 2,
              "freeze_weights": True, "load_pretrained": True, "lightattn": True, "lr_schedule": True},
})
model = TransferModel(cfg)
ck = torch.load(TM / "models" / "thermoMPNN_default.pt", map_location="cpu", weights_only=True)
sd = {k[len("model."):]: v for k, v in ck["state_dict"].items() if k.startswith("model.")}
model.load_state_dict(sd, strict=True)
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.eval().to(dev)

first = min(int(l[22:26]) for l in open(PDB) if l.startswith("ATOM") and l[21] == "A")
pdb = alt_parse_PDB(PDB, "A")
seq = pdb[0]["seq"]
muts = []
for idx, wt in enumerate(seq):
    resnum = first + idx
    if wt == "-" or (RANGE and not RANGE[0] <= resnum <= RANGE[1]):
        continue
    for mt in ALPHABET[:-1]:
        muts.append((resnum, Mutation(position=idx, wildtype=wt, mutation=mt, pdb=pdb[0]["name"])))

with torch.no_grad():
    pred, _ = model(pdb, [m for _, m in muts])

with open(OUT, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["resnum", "wildtype", "mutation", "ddG"])
    for (resnum, m), p in zip(muts, pred):
        w.writerow([resnum, m.wildtype, m.mutation, f"{p['ddG'].cpu().item():.6f}"])
print(PDB, "device", dev, "residues", len({r for r, _ in muts}), "rows", len(muts), "->", OUT)
