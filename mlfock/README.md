# mlfock — learned Fock matrices for MRSF-TDDFTB reference orbitals

Goal: give the MRSF-TDDFTB response reference orbitals of real ROKS-DFT
quality without running the ROKS SCF.  The model never outputs orbitals
(they are not unique and jump at near-degeneracies); it outputs **Fock
matrices**, which are smooth in geometry and built from atom-pair blocks.
One generalized diagonalization then gives orthonormal canonical orbitals.

## How it plugs into openqp-dftb (no projection needed)

openqp-dftb already has the injection path, "simple-MRSF"
(`tools/simple_mrsf`, env `OPENQP_DFTB_SIMPLE_MRSF_REF`): it overrides the DFTB
ground state with an **all-electron** reference (S, C, ε, occupations,
AO→atom/l maps and the AO Fock matrices F_α, F_β in the Gaussian basis) and
keeps the DFTB γ kernel for the response.  So the ML target is exactly that
reference, in OpenQP's own AO basis:

    F_eff   = S C ε Cᵀ S   (ROKS effective Fock; eigenvectors = canonical MOs)
    F_alpha, F_beta        (OQP::FOCK_A / FOCK_B; the response's A-matrix diagonal)

learned as a delta over the one-electron Hamiltonian, ΔF = F − Hcore, which
OpenQP builds in milliseconds together with S.  `Orbitals.write_reference`
writes the binary the loader reads.

## Verified against real OpenQP (tests/test_openqp.py, examples/water_demo.py)

* AO conventions measured from OpenQP overlaps of rotated molecules:
  p = (x, y, z); Cartesian d = (xx, yy, zz, xy, xz, yz) with √3 on cross terms;
  `OQP::VEC_MO_A` is MO-major.  Rotation matrices reproduce S and Hcore of a
  rotated water to 1e-10.
* ROKS-triplet BHHLYP/6-31G* water, 40 training / 10 held-out displaced
  geometries, 200 epochs (2 min CPU):

  | | ML ΔFock | Hcore guess |
  |---|---|---|
  | orbital-energy RMSE (eV) | 0.40 | 203 |
  | closed / SOMO / virtual fidelity | 0.9999 / 0.998 / 0.9996 | 0.87 / 0.52 / 0.90 |

## Layout

| file | what |
|---|---|
| `mlfock/basis.py`    | general Cartesian s/p/d layouts, `shells_from_openqp`, AO rotation matrices (reps of SO(3), not orthogonal for Cartesian d) |
| `mlfock/extract.py`  | records from a converged OpenQP molecule; simple-MRSF reference writer/reader |
| `mlfock/features.py` | pair local frames (covariant fallbacks), invariant features |
| `mlfock/model.py`    | `DeltaFockModel`: multi-channel pair blocks in local frames, exact permutation symmetry |
| `mlfock/esen_backbone.py`, `esen_model.py` | optional Meta FAIR eSEN/UMA backbone as feature extractor |
| `mlfock/predict.py`  | assemble, `eigh(F_eff, S)`, ensemble uncertainty, subspace fidelities |
| `mlfock/onthefly.py` | uncertainty-gated oracle calls with background refits |
| `mlfock/oqp_bridge.py` | `OpenQPOracle` (ROKS in OpenQP), `run_mrsf_tddftb_with_reference` (needs openqp-dftb) |
| `tests/` | synthetic equivariance/permutation/learning tests + real-OpenQP tests |

## Use

    pip install -e .[test] && pytest tests -q
    python examples/water_demo.py 40 10 200                 # the table above
    python examples/generate_and_train.py traj.xyz records/ --train
    python -m mlfock.train --data records/ --backbone esen-sm-direct-all-omol --spin 3   # optional

```python
from mlfock import DeltaFockModel, FockPredictor
orb = FockPredictor([DeltaFockModel.load("model.pt")]).predict(Z, pos_bohr, S, Hcore, na, nb)
orb.write_reference("ref.bin", layout, na, nb)      # -> OPENQP_DFTB_SIMPLE_MRSF_REF
```

## Open points

* **Uncertainty.** Orbitals from the predicted F are trivially self-consistent
  with F; a true residual needs one real Fock build (one SCF iteration).
  Default gate is ensemble disagreement; `FockPredictor(fock_builder=...)`
  adds the real check.
* **Gradients.** simple-MRSF rejects gradient requests (the native gradient
  differentiates DFTB integrals, not injected orbitals).  For NAMD with ML
  orbitals a gradient consistent with the injected reference is needed on
  the openqp-dftb side.
* **MRSF-TDDFTB numbers** with ML orbitals could not be produced here: the
  openqp-dftb native library is not built in this container.  `run_mrsf_tddftb_with_reference`
  is the call to make on a machine that has it.
