# Spin-Orbit Coupling

OpenQP supports MRSF-TDDFT spin-orbit coupling through `runtype=soc`.
SOC mixes spin-free electronic states through relativistic one-electron terms
and, when requested, a mean-field treatment of the two-electron SOC operator.
This workflow is useful when intersystem crossing, phosphorescence, or
singlet-triplet mixing is important. See the
[References](../references.md#spin-orbit-coupling) page for SOC background and
the mean-field SOC operator reference.

Input style:

```ini
[input]
runtype=soc
method=tdhf
functional=bhhlyp
basis=6-31G(2df,p)
soc_2e=1

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=12
multiplicity=3
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_soc", silent=1)
job.molecule(geometry="water", basis="6-31G(2df,p)", charge=0)
job.input(soc_2e=1)
job.mrsf(nstate=12, functional="bhhlyp", runtype="soc")
job.tdhf.multiplicity = 3

mol = job.run()
soc = mol.get_soc()
```

Runnable inputs:

- [`examples/SOC/H2O_BHHLYP_SOC.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/SOC/H2O_BHHLYP_SOC.inp)
- [`examples/SOC/CH3Br-BHHLYP-SOC.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/SOC/CH3Br-BHHLYP-SOC.inp)

## SOC Terms

`[input] soc_2e` controls the SOC Hamiltonian:

| Value | Meaning |
| --- | --- |
| `0` | One-electron SOC terms only. |
| `1` | One-electron plus mean-field two-electron SOC terms. |

SOC workflows require a triplet ROHF reference and `[tdhf] type=mrsf`.
