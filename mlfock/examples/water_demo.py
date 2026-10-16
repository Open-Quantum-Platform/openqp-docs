"""End-to-end demonstration on real OpenQP data (ROKS-triplet BHHLYP/6-31G* water).

1. sample displaced water geometries, run the ROKS reference for each
2. train the ΔFock model on N_train geometries (target F_eff, F_alpha, F_beta; base Hcore)
3. on held-out geometries compare ML orbitals with the converged reference:
   orbital-energy RMSE, closed/SOMO/virtual subspace fidelities, Fock errors,
   and the same numbers for the Hcore-only guess as a baseline
4. write an MRSF-TDDFTB reference file (OPENQP_DFTB_SIMPLE_MRSF_REF format) for one geometry

    python examples/water_demo.py [n_train=40] [n_test=10] [epochs=200]
"""

import sys
import time
import numpy as np
import scipy.linalg
import torch

from mlfock.oqp_bridge import OpenQPOracle, rohf_config
from mlfock.data import FockDataset
from mlfock.model import DeltaFockModel
from mlfock.train import train
from mlfock.predict import FockPredictor, subspace_fidelities

torch.set_default_dtype(torch.float64)
HA = 27.211386
ANG = 1.0 / 0.52917721067
WATER = np.array([[0.0, 0.0, 0.1173], [0.0, 0.7572, -0.4692], [0.0, -0.7572, -0.4692]]) * ANG
Z = np.array([8, 1, 1])


def sample(rng, n, amp=0.12):
    out = []
    for _ in range(n):
        pos = WATER + rng.normal(0, amp * ANG, WATER.shape)
        q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        out.append(pos @ q.T)                     # random orientation too
    return out


def main(n_train=40, n_test=10, epochs=200):
    rng = np.random.RandomState(0)
    oracle = OpenQPOracle(rohf_config("bhhlyp", "6-31g*"), workdir="/tmp")
    t0 = time.time()
    recs = [oracle(Z, p, tag=f"w{k}") for k, p in enumerate(sample(rng, n_train + n_test))]
    print(f"reference ROKS for {len(recs)} geometries: {time.time()-t0:.1f} s")
    layout = recs[0].layout()
    nmax = layout.max_nao()
    ds, val = FockDataset(recs[:n_train], 10.0, nmax), FockDataset(recs[n_train:], 10.0, nmax)
    model = DeltaFockModel(shells=recs[0].shells, n_channels=3, max_z=10, hidden=128)
    t0 = time.time()
    train(model, ds, val, epochs=epochs, lr=2e-3, log_every=50)
    print(f"training: {time.time()-t0:.1f} s")

    pred = FockPredictor([model])
    rows = []
    for rec in recs[n_train:]:
        orb = pred.predict(Z, rec.coords_bohr, rec.S, rec.F_base, rec.n_occ_alpha, rec.n_occ_beta)
        eps_ref, C_ref = scipy.linalg.eigh(rec.F_ref[0], rec.S)
        nshow = rec.n_occ_alpha + 4
        eps_h, C_h = scipy.linalg.eigh(rec.F_base, rec.S)
        rows.append({
            "ml_eps_rmse_eV": np.sqrt(np.mean((orb.eps[:nshow] - eps_ref[:nshow]) ** 2)) * HA,
            "hcore_eps_rmse_eV": np.sqrt(np.mean((eps_h[:nshow] - eps_ref[:nshow]) ** 2)) * HA,
            "ml_fid": subspace_fidelities(orb.C, C_ref, rec.S, rec.n_occ_alpha, rec.n_occ_beta),
            "hcore_fid": subspace_fidelities(C_h, C_ref, rec.S, rec.n_occ_alpha, rec.n_occ_beta),
            "ml_Fa_maxerr_eV": np.abs(orb.F_alpha - rec.F_ref[1]).max() * HA,
            "ml_Fb_maxerr_eV": np.abs(orb.F_beta - rec.F_ref[2]).max() * HA,
        })
    mean = lambda k: np.mean([r[k] for r in rows])
    fid = lambda k, s: np.mean([r[k][s] for r in rows])
    print("\nheld-out geometries:", len(rows))
    print(f"{'':28s}{'ML ΔFock':>12s}{'Hcore guess':>14s}")
    print(f"{'orbital-energy RMSE (eV)':28s}{mean('ml_eps_rmse_eV'):12.3f}{mean('hcore_eps_rmse_eV'):14.3f}")
    for s in ("closed", "somo", "virtual"):
        print(f"{s+' space fidelity':28s}{fid('ml_fid', s):12.4f}{fid('hcore_fid', s):14.4f}")
    print(f"{'F_alpha max error (eV)':28s}{mean('ml_Fa_maxerr_eV'):12.3f}")
    print(f"{'F_beta  max error (eV)':28s}{mean('ml_Fb_maxerr_eV'):12.3f}")
    rec = recs[-1]
    orb = pred.predict(Z, rec.coords_bohr, rec.S, rec.F_base, rec.n_occ_alpha, rec.n_occ_beta)
    orb.write_reference("/tmp/water_ml_ref.bin", layout, rec.n_occ_alpha, rec.n_occ_beta)
    model.save("/tmp/water_mlfock.pt")
    print("\nwrote /tmp/water_ml_ref.bin (OPENQP_DFTB_SIMPLE_MRSF_REF format) and /tmp/water_mlfock.pt")


if __name__ == "__main__":
    main(*[int(a) for a in sys.argv[1:]])
