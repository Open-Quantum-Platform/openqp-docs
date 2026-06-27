# Geometry Optimization

The default optimizer backend is the native OpenQP optimizer:

```ini
[optimize]
lib=oqp
```

The native backend uses redundant internal coordinates, DLC/TRIC-style
coordinate handling, and restricted-step RFO/P-RFO style steps. It supports
minima, transition states, MECI/MECP/TCI, NEB, IRC, and MEP workflows where the
corresponding run type is implemented.

## Native Minimum Search

Input style:

```ini
[input]
runtype=optimize
method=hf
functional=bhhlyp
basis=6-31g*

[scf]
type=rhf
multiplicity=1

[optimize]
lib=oqp
istate=0
maxit=10

[oqp]
coordsys=tric
trust=0.2
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_opt", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory("dft", functional="bhhlyp", basis="6-31g*")
job.workflow.optimize(
    lib="oqp",
    istate=0,
    maxit=10,
    coordsys="tric",
    trust=0.2,
)

mol = job.run()
```

Runnable input:
[`examples/OPT/H2O_RHF-DFT_OPTIMIZE_OQP.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/OPT/H2O_RHF-DFT_OPTIMIZE_OQP.inp).

## geomeTRIC Backend

Use geomeTRIC when you need a workflow or constraint style that is best handled
by that external optimizer:

```ini
[optimize]
lib=geometric

[geometric]
coordsys=tric
trust=0.1
constraints_file=my.constraints
```

Python style uses `job.workflow.optimize(...)` for the optimizer selection and routes the
backend options to geomeTRIC:

```python
job.workflow.optimize(
    lib="geometric",
    coordsys="tric",
    trust=0.1,
    constraints_file="my.constraints",
)
```

Runnable geomeTRIC inputs are available in
[`examples/OPT`](https://github.com/Open-Quantum-Platform/openqp/tree/main/examples/OPT),
including
[`H2O_RHF-DFT_OPTIMIZE_GEOMETRIC.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/OPT/H2O_RHF-DFT_OPTIMIZE_GEOMETRIC.inp).

## Crossing Points

MECI and related workflows select the state pair or triplet in `[optimize]`:

Input style:

```ini
[input]
runtype=meci
method=tdhf
functional=bhhlyp

[tdhf]
type=mrsf
nstate=5

[optimize]
lib=oqp
istate=1
jstate=2
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("meci_mrsf", silent=1)
job.molecule("reactant.xyz", charge=0)
job.theory("mrsf-tddft", functional="bhhlyp", basis="6-31g*", nstate=5)
job.workflow.meci(lib="oqp", istate=1, jstate=2)

mol = job.run()
```

Runnable inputs are available in
[`examples/OPT`](https://github.com/Open-Quantum-Platform/openqp/tree/main/examples/OPT).
