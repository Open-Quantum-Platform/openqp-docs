"""Build training records from an XYZ trajectory and train (needs pyoqp).

    python examples/generate_and_train.py traj.xyz records/ --train [--basis 6-31g*] [--functional bhhlyp]

Each frame is run as a ROKS-triplet reference in OpenQP; records hold
F_eff / F_alpha / F_beta (targets), Hcore (base) and S in OpenQP's AO basis.
"""

import argparse
from pathlib import Path
import numpy as np

from mlfock.oqp_bridge import OpenQPOracle, rohf_config, dump_records

ANG2BOHR = 1.0 / 0.52917721067
SYMBOLS = {"H": 1, "He": 2, "Li": 3, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Si": 14, "P": 15,
           "S": 16, "Cl": 17}


def read_xyz_frames(path):
    lines = Path(path).read_text().splitlines()
    k = 0
    while k < len(lines):
        n = int(lines[k]); k += 2
        Z, pos = [], []
        for line in lines[k:k + n]:
            sym, x, y, z = line.split()[:4]
            Z.append(SYMBOLS[sym]); pos.append([float(x), float(y), float(z)])
        k += n
        yield np.array(Z), np.array(pos) * ANG2BOHR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xyz"); ap.add_argument("out_dir")
    ap.add_argument("--basis", default="6-31g*"); ap.add_argument("--functional", default="bhhlyp")
    ap.add_argument("--charge", type=int, default=0); ap.add_argument("--mult", type=int, default=3)
    ap.add_argument("--train", action="store_true"); ap.add_argument("--epochs", type=int, default=300)
    a = ap.parse_args()
    oracle = OpenQPOracle(rohf_config(a.functional, a.basis, a.charge, a.mult))
    recs = [oracle(Z, pos, tag=f"frame{k}") for k, (Z, pos) in enumerate(read_xyz_frames(a.xyz))]
    dump_records(recs, a.out_dir)
    print(f"wrote {len(recs)} records to {a.out_dir}")
    if a.train:
        from mlfock.train import main as train_main
        train_main(["--data", a.out_dir, "--out", "mlfock_model.pt", "--epochs", str(a.epochs)])


if __name__ == "__main__":
    main()
