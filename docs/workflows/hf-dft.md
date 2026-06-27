# HF and DFT

HF and DFT calculations use `[input] method=hf`. Set `[input] functional` only
for DFT; leaving it empty gives Hartree-Fock.

## Energy

Input style:

```ini
[input]
system=
   O   0.000000000   0.000000000  -0.041061554
   H  -0.533194329   0.533194329  -0.614469223
   H   0.533194329  -0.533194329  -0.614469223
charge=0
runtype=energy
basis=6-31g*
method=hf

[guess]
type=huckel

[scf]
type=rhf
multiplicity=1
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_hf", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory("hf", basis="6-31g*")

mol = job.run()
print("SCF energy:", mol.get_scf_energy())
```

Runnable input:
[`examples/HF/H2O_RHF-HF_ENERGY.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HF/H2O_RHF-HF_ENERGY.inp).

## Gradient

For a DFT gradient, request `runtype=grad`, set a functional, and use
`[properties] grad=0` for the reference-state gradient. In Python, the same
choice is written as `job.workflow.gradient(state=0)`.

Input style:

```ini
[input]
runtype=grad
method=hf
functional=bhhlyp
basis=6-31g*

[properties]
grad=0
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_dft_grad", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory("dft", functional="bhhlyp", basis="6-31g*")
job.workflow.gradient(state=0)

mol = job.run()
gradient = mol.get_grad()
```

Runnable input:
[`examples/DFT/H2O_RHF-DFT_GRADIENT.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/DFT/H2O_RHF-DFT_GRADIENT.inp).

## Hessian

HF/DFT Hessians are run with `runtype=hess` and controlled by `[hess]`.
Analytical and numerical Hessian examples are collected on the
[Hessian and Frequencies](hessian.md) workflow page.
