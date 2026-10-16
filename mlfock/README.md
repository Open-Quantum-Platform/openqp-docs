# mlfock — learned Fock matrices for MRSF-TDDFT(B) orbitals

Goal: give MRSF-TDDFTB orbitals of real ROKS-DFT quality at DFTB cost.
The model never outputs orbitals directly (they are not unique and jump at
near-degeneracies).  It outputs the **Fock matrix**, which is smooth in
geometry and built from atom-pair blocks; one generalized diagonalization
then yields orthonormal MOs and orbital energies.

The recommended target is the **delta over DFTB** in the DFTB minimal basis:

    F_model = H_DFTB + ΔF_ML,    ΔF_ML ≈ F_ROKS(projected) − H_DFTB

Everything downstream (MRSF-TDDFTB response, gradients) keeps working on
the same basis and the same code path.

## Layout

| file | what |
|---|---|
| `mlfock/basis.py`    | minimal s/p AO layout, block slicing, AO rotation matrices (`p_order="yzx"` = openqp-dftb convention) |
| `mlfock/extract.py`  | Fock from converged MOs (`F = S C ε Cᵀ S`), OpenQP / openqp-dftb readers, big→small basis projection, `FockRecord` I/O |
| `mlfock/features.py` | pair local frames + rotation-invariant environment features (torch) |
| `mlfock/model.py`    | `DeltaFockModel`: predicts each pair block in its local frame, rotates back, symmetrizes over both pair orientations |
| `mlfock/data.py`, `mlfock/train.py` | dataset and trainer (`python -m mlfock.train --data records/`) |
| `mlfock/predict.py`  | assemble F, `eigh(F, S)`, ensemble uncertainty, optional true SCF residual |
| `mlfock/onthefly.py` | residual-gated active learning with background refits and a replay buffer |
| `mlfock/oqp_bridge.py` | OpenQP oracle (ROKS SCF), DFTB base Hamiltonian, orbital injection into OpenQP |
| `tests/`             | equivariance, permutation, round-trip, learning and on-the-fly tests (no OpenQP needed) |

## Quick start (synthetic check)

    pip install -e .[test]
    pytest tests -q

## Real data

1. Generate records: for each geometry run the DFTB reference (base) and the
   ROKS-DFT reference (target) in OpenQP; see `examples/generate_and_train.py`.
2. Train: `python -m mlfock.train --data records/ --val val/ --out model.pt`.
3. Predict:

```python
from mlfock import DeltaFockModel, FockPredictor
pred = FockPredictor([DeltaFockModel.load("model_seed0.pt"),
                      DeltaFockModel.load("model_seed1.pt")])
orb = pred.predict(Z, pos_bohr, S_tb, F_base=H_tb, n_occ_alpha=na, n_occ_beta=nb)
orb.C, orb.eps, orb.uncertainty
```

4. On the fly, inside an MD loop:

```python
from mlfock import OnTheFlyLearner
from mlfock.oqp_bridge import OpenQPOracle
learner = OnTheFlyLearner(models, OpenQPOracle(DFT_CONFIG), tol_uncertainty=2e-3)
orb, used_oracle = learner.step(Z, pos, S_tb, H_tb, na, nb)
```

## Two things that still need you

**Projection (S_cross).**  Moving the DFT Fock matrix into the DFTB basis
needs the overlap between the Gaussian AOs and the Slater-Koster orbitals.
Fit each SK valence orbital to a few Gaussians once per element, evaluate the
Gaussian-Gaussian overlap in OpenQP, and pass it as `S_cross` to
`project_record`.  Until then you can skip projection and train in the
Gaussian basis (`record_from_openqp`, `p_order="xyz"`, `F_base=None`); the
`run_mrsf_with_orbitals` bridge then feeds the ML orbitals to OpenQP's own
MRSF-TDDFT response, which is a complete path today.

**Native orbital injection.**  The openqp-dftb C ABI only takes a warm-start
MO file as an SCC *guess* and re-converges.  To run the MRSF-TDDFTB response
on fixed ML orbitals a small "use these reference orbitals, skip SCC" entry
point is needed on the native side.  `write_dftb_orbitals` writes them in a
plain binary layout (`int64 nbf, noca, nocb; float64 eps[nbf]; float64
C[nbf*nbf] column-major`) for that entry.

## Uncertainty, honestly

Diagonalizing the predicted F gives orbitals that are trivially
self-consistent with F itself, so the commutator residual is not free: it
needs one real Fock build from the ML density (one DFT SCF iteration).
`FockPredictor(fock_builder=...)` does that when asked.  The cheap default is
ensemble disagreement (train 2–4 seeds).  The on-the-fly learner gates on
either, plus a periodic forced oracle call.

## Model notes

* Equivariance by local frames: z along r_ij, x from a cutoff-weighted sum of
  neighbour directions; AO blocks rotate with `D = blockdiag(1, P R Pᵀ)`.
* Each off-diagonal pair is evaluated in both orientations and averaged
  transposed, which makes the result exactly permutation invariant.
* s and p shells only (H, C, N, O, F minimal basis).  d shells raise.
* Upgrade path: swap `DeltaFockModel` for an e3nn/QHNet-style tensor-product
  model; `assemble`, `extract_blocks`, the data format and everything
  downstream stay the same.
