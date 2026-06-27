# SF-TDDFT

Spin-flip TDDFT uses a high-spin open-shell reference and `[tdhf] type=sf`.
It is useful for accessing low-spin target states from a high-spin reference.
MRSF-TDDFT is the recommended OpenQP route when the mixed-reference correction
is needed to reduce spin contamination and to describe multiconfigurational
ground-state surfaces.

In Python scripts, SF-TDDFT uses the native response-section helpers because
the high-spin reference and spin-flip response model are selected explicitly.

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
type=sf
nstate=3
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_sf", silent=1)
job.molecule(geometry="water", charge=0)
job.workflow.input(method="tdhf", functional="bhhlyp", basis="6-31g*")
job.workflow.scf(type="rohf", multiplicity=3)
job.workflow.tdhf(type="sf", nstate=3)

mol = job.run()
print("SF-TDDFT energies:", mol.get_td_energies())
```

Runnable input:
[`examples/SF-TDDFT/H2O_BHHLYP-SFTDDFT_ENERGY.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/SF-TDDFT/H2O_BHHLYP-SFTDDFT_ENERGY.inp).

## Gradient

SF-TDDFT gradients use `runtype=grad` and `[properties] grad`. In SF-TDDFT,
state `1` means the lowest spin-flip target state, not the first ordinary
TDDFT excited state.

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
type=sf
nstate=3

[properties]
grad=3
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_sf_grad", silent=1)
job.molecule(geometry="water", charge=0)
job.workflow.input(method="tdhf", functional="bhhlyp", basis="6-31g*")
job.workflow.scf(type="rohf", multiplicity=3)
job.workflow.tdhf(type="sf", nstate=3)
job.workflow.gradient(state=3)

mol = job.run()
gradient = mol.get_grad()
```

Runnable input:
[`examples/SF-TDDFT/H2O_BHHLYP-SFTDDFT_GRADIENT.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/SF-TDDFT/H2O_BHHLYP-SFTDDFT_GRADIENT.inp).

## Notes

- SF-TDDFT currently uses an ROHF high-spin reference in the documented
  production path.
- `[tdhf] nstate` must include the highest spin-flip state requested by a
  gradient or follow-up workflow.
- For the mixed-reference correction and OpenQP's main multistate workflow, use
  [MRSF-TDDFT](mrsf-tddft.md).
