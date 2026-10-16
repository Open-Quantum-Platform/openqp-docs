"""End-to-end driver on real OpenQP data (needs pyoqp + openqp-dftb).

Usage:
    python examples/generate_and_train.py geoms.xyz records/ --train

* geoms.xyz : multi-frame XYZ (Angstrom), e.g. frames from an MRSF trajectory.
* For each frame: run DFTB (base) and ROKS-DFT (reference) in OpenQP,
  project the DFT Fock matrix to the DFTB basis with S_cross, store a record.
* S_cross (Gaussian AO x DFTB AO overlap) must be supplied by a function
  you provide; see `cross_overlap` below and README section "Projection".
"""

import sys
import numpy as np
from pathlib import Path

from mlfock.extract import FockRecord, project_record
from mlfock.oqp_bridge import OpenQPOracle, DFTBBase, dump_records

ANG2BOHR = 1.0 / 0.52917721067

DFT_CONFIG = {
    "input": {"system": "", "charge": 0, "method": "hf", "basis": "6-31gs",
              "functional": "bhhlyp", "runtype": "energy"},
    "scf": {"type": "rohf", "multiplicity": 3, "maxit": 100},
    "guess": {"type": "huckel"},
}
DFTB_CONFIG = {
    "input": {"system": "", "charge": 0, "method": "dftb", "runtype": "energy"},
    "dftb": {"type": "mrsf", "reference": "roks", "reference_multiplicity": 3},
    "tdhf": {"nstate": 3},
}


def read_xyz_frames(path):
    lines = Path(path).read_text().splitlines()
    k = 0
    while k < len(lines):
        n = int(lines[k]); k += 2
        Z, pos = [], []
        for line in lines[k:k + n]:
            sym, x, y, z = line.split()[:4]
            Z.append({"H": 1, "C": 6, "N": 7, "O": 8, "F": 9}[sym])
            pos.append([float(x), float(y), float(z)])
        k += n
        yield np.array(Z), np.array(pos) * ANG2BOHR


def cross_overlap(mol_dft, Z, pos):
    """<Gaussian AO | DFTB AO>.  Placeholder: implement with your SK-orbital
    Gaussian fits and OpenQP's one-electron integral driver."""
    raise NotImplementedError("provide S_cross for the projection step")


def main(xyz, out_dir, do_train=False):
    system_text = ""
    oracle = DFTBBase(DFTB_CONFIG)
    dft = OpenQPOracle(DFT_CONFIG)
    records = []
    for k, (Z, pos) in enumerate(read_xyz_frames(xyz)):
        H_tb, S_tb = oracle(Z, pos)
        rec_big = dft(Z, pos)
        S_cross = cross_overlap(dft.mol, Z, pos)
        rec = project_record(rec_big, S_cross, F_base=H_tb, S_base=S_tb)
        rec.tag = f"frame{k}"
        records.append(rec)
    dump_records(records, out_dir)
    if do_train:
        from mlfock.train import main as train_main
        train_main(["--data", out_dir, "--out", "mlfock_model.pt", "--epochs", "300"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--train" in sys.argv)
