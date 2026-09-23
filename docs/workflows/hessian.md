# Hessian and Frequencies

Hessian workflows use `[input] runtype=hess` and are controlled by `[hess]`.
OpenQP supports analytical Hessians for supported HF/DFT ground states and for
the lowest isolated singlet state of restricted TDHF and selected TDDFT
functionals. Numerical Hessians remain available for broader method and state
combinations.

Frequency, IR, Raman, and thermochemistry analysis are built from Hessian data
when the selected workflow produces the required derivatives.

The generated `.hess.json` and `.freq.molden` files contain portable normal
modes and, for supported bases, the SCF molecular orbitals needed to view MO
surfaces and vibrational animation together. See
[Orbital and Vibrational Output](orbital-vibrational-output.md).

In Python scripts, start from a compact HF, DFT, or MRSF-TDDFT theory setup and
then select the Hessian workflow with `job.workflow.hessian(...)`.

## Analytical HF/DFT Hessian

`.oqp`:

```text
dft/bhhlyp/6-31g* hess(S0,type=analytical,clean=true)
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_dft_hess", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.dft(functional="bhhlyp", basis="6-31g*")
job.workflow.hessian(type="analytical", state=0, clean=True)

mol = job.run()
hessian = mol.get_hess()
```

Legacy `.inp`:

```ini
[input]
runtype=hess
method=hf
functional=bhhlyp
basis=6-31g*

[scf]
type=rhf
multiplicity=1

[hess]
type=analytical
state=0
clean=True
```

Runnable `.oqp`:
[`examples/HESS/H2O_RHF-DFT_ANA_HESS.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2O_RHF-DFT_ANA_HESS.oqp).
The same-stem `.inp` file is retained for legacy use.

## Analytical TDHF/TDDFT Hessian

The analytical excited-state Hessian is restricted to a closed-shell RHF
reference, full-response singlet RPA, and the lowest excited state
(`state=1`). Set `[tdhf] nstate` to at least `2`; the lowest state must be
separated from the second calculated state by more than `1.0e-10` hartree.
Canonical occupied and virtual orbital spaces
must also have no pair separated by `1.0e-10` hartree or less. These conditions
avoid an arbitrary response within a degenerate state or orbital subspace.

The verified functional names are `SVWN`, `SVWN5`, `LDA`, `BLYP`, `PBE`,
`PBEPBE`, `B3LYP5`, and `B3LYPV5`; an empty functional selects TDHF. `PBE` and
`PBEPBE` are equivalent, as are `B3LYP5` and `B3LYPV5`. The bare `B3LYP` name
is not accepted because it is not an unambiguous Libxc functional identifier.
TDA, triplet targets, higher excited states, range-separated functionals,
meta-GGA functionals, and calculations with more than one MPI rank must use a
numerical Hessian.

Legacy `.inp`:

```ini
[input]
runtype=hess
method=tdhf
basis=6-31g

[scf]
type=rhf
multiplicity=1
conv=1.0e-10

[tdhf]
type=rpa
multiplicity=1
nstate=2
conv=1.0e-10
zvconv=1.0e-10

[hess]
type=analytical
state=1
clean=True
```

The H2 analytical and numerical examples include both the primary regression
JSON and the `.hess.json` frequency sidecar:

- [`H2_RHF_RPA_ANA_HESS.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2_RHF_RPA_ANA_HESS.inp)
- [`H2_RHF_RPA_NUM_HESS.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2_RHF_RPA_NUM_HESS.inp)

For the committed 6-31G H2 references, the analytical and numerical Hessians
are compared directly in the example regression calculation. The calculated
S1-S2 separation is `0.4996771` hartree, and the maximum absolute Hessian
difference is approximately `9.0e-7` hartree/bohr².

## Numerical HF/DFT Hessian

Omit `type=analytical` to use the numerical finite-difference path.

`.oqp`:

```text
dft/bhhlyp/6-31g* hess(S0,clean=true)
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_dft_num_hess", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.dft(functional="bhhlyp", basis="6-31g*")
job.workflow.hessian(state=0, clean=True)
mol = job.run()
```

Legacy `.inp`:

```ini
[input]
runtype=hess
method=hf
functional=bhhlyp
basis=6-31g*

[scf]
type=rhf
multiplicity=1

[hess]
state=0
clean=True
```

For a symmetric molecule, `symmetry_unique=True` can reduce the numerical
finite-difference work to one displaced atom per symmetry-equivalent atom
orbit. It is an opt-in feature and falls back to the full displacement set
with an explanatory note whenever the current geometry or tolerance does not
support a complete symmetry reconstruction.

Runnable `.oqp`:
[`examples/HESS/H2O_RHF-DFT_NUM_HESS.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2O_RHF-DFT_NUM_HESS.oqp).
The same-stem `.inp` file is retained for legacy use.

## Numerical MRSF-TDDFT Hessian

MRSF-TDDFT Hessians use the numerical path in the documented examples. The
MRSF state numbering follows the MRSF target-state list; `state=1` is the
lowest MRSF target state, which can be the multiconfigurational ground state.

`.oqp`:

```text
mrsf(nstate=2)/bhhlyp/6-31g* hess(S0,clean=true)
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf_hess", silent=1)
job.molecule(geometry="water", charge=0)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=2)
job.workflow.hessian(state=1, clean=True)

mol = job.run()
```

Legacy `.inp`:

```ini
[input]
runtype=hess
method=tdhf
functional=bhhlyp
basis=6-31g*

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=2

[hess]
state=1
clean=True
```

Runnable `.oqp`:
[`examples/HESS/H2O_BHHLYP-MRSFTDDFT_NUM_HESS.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2O_BHHLYP-MRSFTDDFT_NUM_HESS.oqp).
The same-stem `.inp` file is retained for legacy use.

## Notes

- HF/DFT ground-state Hessians use `state=0`.
- TDHF/TDDFT Hessian target states use positive excited-state indices.
- Analytical TDHF/TDDFT Hessians currently require the lowest isolated singlet
  state (`state=1`) of an RHF full-response RPA calculation, at least two
  calculated excited states (`nstate>=2`), and one MPI rank.
- SF-TDDFT and MRSF-TDDFT use spin-flip/MRSF target-state ordering, where
  state `1` is the lowest target state.
- `[hess] restart=True` can continue a numerical Hessian workflow where the
  corresponding temporary files are available.
- `[hess] read=True` accepts only a current versioned `.hess.json` whose
  electronic-model configuration, state, atoms, geometry, and isotopic masses
  match the present job. Referenced file contents and the OpenQP binary are not
  content-fingerprinted, so regenerate the sidecar after changing either one.
  Unsigned legacy sidecars must be regenerated with `read=False`.
- `[hess] clean=True` removes temporary Hessian files where supported.
