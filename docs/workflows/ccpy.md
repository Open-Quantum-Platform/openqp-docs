# CCpy Coupled Cluster (external library)

`oqp.interop.ccpy` runs the coupled-cluster methods of the external
[CCpy](https://github.com/piecuch-group/ccpy) library on converged OpenQP
Hartree-Fock orbitals. The one- and two-electron integrals, the molecular
orbitals and the orbital energies are taken from the OpenQP calculation, so
CCpy correlates exactly the reference that OpenQP converged.

CCpy provides CCSD, CR-CC(2,3), CC(P;Q), equation-of-motion CC (EOM-CC),
ionization-potential and electron-attachment EOM-CC (IP/EA-EOM-CC) and
spin-flip EOM-CC. OpenQP returns a CCpy `Driver` object; every CCpy method is
then called through that object, as described in the CCpy documentation.

CCpy is distributed under GPL-3.0. OpenQP does not include, redistribute or
link it. It is downloaded and built into the user's Python environment the
first time it is needed.

This route is available from Python only. There is no `.oqp` or `.inp`
keyword for it. For OpenQP's own coupled-cluster implementation, which runs
from an input file, see [Coupled Cluster](coupled-cluster.md).

## Supported references

| Requirement | Detail |
| --- | --- |
| Reference | `[scf] type=rhf`, `rohf` or `uhf` |
| Method | `[input] method=hf`, with no `functional`. Kohn-Sham orbitals and the molecule of a correlated run (for example `method=ccsd`) are rejected. |
| Convergence | The OpenQP SCF must be converged. |
| Reference energy | The determinant energy is rebuilt from the OpenQP integrals and must agree with the OpenQP SCF energy to 1e-6 Eh; otherwise the call stops with an error. |
| Point group | C1. The OpenQP point-group symmetry is not passed to CCpy. |

For an ROHF reference the orbital energies passed to CCpy come from the
Guest-Saunders canonicalization (`rohf_canonicalization`, the CCpy argument,
selects another one). For a UHF reference OpenQP sets the CCpy option
`RHF_symmetry=False`, so that a broken-symmetry UHF singlet with equal alpha
and beta electron counts is not treated as a closed-shell RHF case.

These conditions are checked before CCpy is downloaded and before any
integral is built.

## Installation

On the first call OpenQP runs

```bash
python -m pip install 'coupled-cluster-py @ git+https://github.com/piecuch-group/ccpy@cf72da4865e054f7a935e2df27e920cf5e335435'
```

in the running Python environment, at this pinned CCpy commit. The build
requires:

- Python 3.10 or newer (OpenQP itself accepts Python 3.9);
- numpy 2.0 or newer, already installed. OpenQP does not upgrade numpy or scipy
  during the CCpy installation: pip runs with a constraints file that pins the
  installed numpy and scipy versions. With an older numpy the call stops with
  an error; upgrade numpy and scipy in a separate step and restart Python;
- `git`, a Fortran compiler and OpenBLAS. CCpy links its own 32-bit-integer
  OpenBLAS, separate from the 64-bit-integer (ILP64) BLAS/LAPACK used by OpenQP.
  On Debian or Ubuntu install `libopenblas-dev`; on macOS the keg-only Homebrew
  `openblas` is located automatically.

Set `OPENQP_CCPY_AUTO_INSTALL=0` to forbid the download. A missing CCpy is then
an `ImportError` whose message gives the `pip` command above. Concurrent
calculations that use the same Python environment share one installation:
a file lock lets the first one build CCpy while the others wait.

The download and build took about 70 s on an Apple Silicon Mac (a single
measurement).

## Python

### Compact API

```python
from oqp.openqp import OpenQP

driver = OpenQP("h2o").molecule(geometry="water", basis="cc-pvdz").ccpy(nfrozen=1)
driver.run_cc(method="ccsd")
print(driver.system.reference_energy + driver.correlation_energy)
```

`ccpy(nfrozen=0, ndelete=0, **kwargs)` runs the Hartree-Fock calculation when
the job has not run yet, or when its configuration changed after the last run,
and returns the CCpy `Driver`, not the `OpenQP` object. `job.workflow.ccpy(...)`
is the same call. For an open-shell reference, select it with the usual
Hartree-Fock theory call:

```python
job = OpenQP("h2o_cation").molecule(geometry="water", charge=1, multiplicity=2)
job.theory.hf(basis="6-31g*", reference="uhf")
driver = job.ccpy()
```

### From a finished OpenQP run

`driver_from_openqp(mol, nfrozen=0, ndelete=0, reference=None)` accepts the
molecule of any converged `method=hf` run, for example `Runner.mol`:

```python
from oqp.interop.ccpy import driver_from_openqp
from oqp.pyoqp import Runner

runner = Runner(project="h2o", input_file="h2o.inp", log="h2o.log")
runner.run()

driver = driver_from_openqp(runner.mol, nfrozen=1)
driver.run_cc(method="ccsd")
driver.run_hbar(method="ccsd")
driver.run_leftcc(method="left_ccsd")
driver.run_ccp3(method="crcc23")
e_ccsd = driver.system.reference_energy + driver.correlation_energy
e_crcc23 = e_ccsd + driver.deltap3[0]["D"]
```

| Argument | Meaning |
| --- | --- |
| `nfrozen` | Number of frozen core orbitals. At most the number of doubly occupied (beta) orbitals. |
| `ndelete` | Number of highest virtual orbitals removed from the correlation treatment. At most the number of alpha virtual orbitals. |
| `reference` | `rhf`, `rohf` or `uhf`. Defaults to the `[scf] type` of the OpenQP run. |

`hamiltonian_from_openqp(mol, ...)` returns the CCpy `(system, hamiltonian)`
pair with the same checks. A `Driver` built from that pair directly does not
receive the UHF setting `RHF_symmetry=False`; use `driver_from_openqp`, or set
the option yourself.

The example `examples/CC/ccpy_h2o.py` in the OpenQP repository runs CCSD and
CR-CC(2,3) for H2O/STO-3G with one frozen core orbital:

```bash
python ccpy_h2o.py h2o_rhf_sto-3g_ccpy.inp
```

## Memory

The AO and MO two-electron integrals are held in memory as dense arrays of
`8 nbf^4` bytes each, and a UHF reference keeps three spin blocks. The peak is
several times `8 nbf^4` bytes; the estimate from this formula is 2-3 GB at
`nbf = 100`. This route is therefore intended for small molecules.

## Verification

OpenQP energies obtained through this route were compared with the same CCpy
commit driven from PySCF orbitals (`Driver.from_pyscf`) for identical basis
sets. All energies agree to 1e-8 Eh:

| System | Reference | Quantities compared |
| --- | --- | --- |
| H2O, 6-31G* | RHF, all electrons and one frozen core | E(RHF), E(CCSD), E(CR-CC(2,3)_D) |
| H2O, cc-pVDZ (spherical) | RHF | E(RHF), E(CCSD) |
| CH2 ³B₁, 6-31G* | UHF, all electrons and one frozen core | E(UHF), E(CCSD) |
| CH2 triplet, 6-31G* | ROHF | E(ROHF), E(CCSD), three SF-EOMCCSD singlet excitation energies |

These cases are part of `tests/test_ccpy_interop.py` in the OpenQP repository
and were run on Apple Silicon macOS. The CCpy build on x86-64 Linux next to
the OpenQP ILP64 BLAS is performed by the OpenQP continuous-integration test
job. Intel macOS and Windows have not been tested.
