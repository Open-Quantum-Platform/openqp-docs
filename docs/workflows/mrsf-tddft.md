# MRSF-TDDFT

MRSF-TDDFT uses `[input] method=tdhf`, `[tdhf] type=mrsf`, and usually a triplet
ROHF reference. Although it is configured through the TDHF/TDDFT response
section, MRSF-TDDFT is used for multiconfigurational ground-state surfaces as
well as excited-state surfaces.

MRSF-TDDFT combines the two high-spin spin-flip reference components into a
mixed-reference response problem. This keeps the linear-response workflow close
to TDDFT while reducing the spin contamination that can obscure ordinary
spin-flip TDDFT roots. See the [References](../references.md#mrsf-tddft) page
for the original theory, analytic-gradient implementation, and recent accounts.

## Energy

Input style:

```ini
[input]
runtype=energy
method=tdhf
functional=bhhlyp
basis=6-31g*

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=3
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf", silent=1)
job.molecule(geometry="water", charge=0)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=3)

mol = job.run()
results = mol.get_results()
print("Ground/reference energy:", results["energy"])
print("TD energies:", results["td_energies"])
```

Runnable input:
[`examples/MRSF-TDDFT/H2O_BHHLYP-MRSFTDDFT_ENERGY.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/MRSF-TDDFT/H2O_BHHLYP-MRSFTDDFT_ENERGY.inp).

## Gradient

Use `runtype=grad` and select the state through `[properties] grad`.

Input style:

```ini
[input]
runtype=grad
method=tdhf
functional=bhhlyp
basis=6-31g*

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=3

[properties]
grad=3
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf_grad", silent=1)
job.molecule(geometry="water", charge=0)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=3)
job.workflow.gradient(state=3)

mol = job.run()
gradient = mol.get_grad()
```

Runnable input:
[`examples/MRSF-TDDFT/H2O_BHHLYP-MRSFTDDFT_GRADIENT.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/MRSF-TDDFT/H2O_BHHLYP-MRSFTDDFT_GRADIENT.inp).

## Notes

- In Python, `job.theory.mrsf(...)` supplies the usual ROHF triplet
  reference for MRSF-TDDFT. Raw input files still show `[scf] multiplicity=3`
  explicitly because they are the direct OpenQP keyword form.
- MRSF state numbering follows the spin-flip/MRSF target-state list. `state=1`
  in Python, or `grad=1` in `[properties]`, means the lowest MRSF target state,
  which can be the multiconfigurational ground state. This differs from
  ordinary TDHF/TDDFT, where state `1` means the first excited state.
- `[tdhf] nstate` must include every state requested by gradients, NACME, SOC,
  or EKT analysis.
- For ordinary TDDFT, see [TDDFT and TDHF](tddft.md).
- For spin-flip TDDFT without mixed-reference correction, use
  [SF-TDDFT](sf-tddft.md).
- UMRSF-TDDFT uses `[tdhf] type=umrsf` with a UHF reference and is currently an
  energy-only workflow.
