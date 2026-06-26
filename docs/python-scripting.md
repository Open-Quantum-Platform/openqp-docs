# Run OpenQP from Python

OpenQP can be driven entirely from Python. The Python API is meant to feel like
an OpenQP input file expressed as a script: define the molecule, choose the
workflow, run the calculation, and read results.

The recommended high-level entry point is `oqp.openqp.OpenQP`. It keeps the
native OpenQP section names available, while giving MRSF-TDDFT and ordinary HF
jobs compact workflow helpers.

## Minimal MRSF-TDDFT Script

MRSF-TDDFT is a central OpenQP workflow. The compact helper sets the standard
MRSF blocks while leaving the detailed OpenQP keywords available.

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf", silent=1)

job.molecule(
    """
O   0.000000000   0.000000000  -0.041061554
H  -0.533194329   0.533194329  -0.614469223
H   0.533194329  -0.533194329  -0.614469223
""",
    basis="6-31g*",
    charge=0,
)
job.mrsf(nstate=3)

mol = job.run()
results = mol.get_results()

print("Ground/reference energy:", results["energy"])
print("TD energies:", results["td_energies"])
```

`job.mrsf(nstate=3)` sets:

```ini
[input]
method = tdhf
runtype = energy

[scf]
type = rohf
multiplicity = 3

[tdhf]
type = mrsf
nstate = 3
```

## Minimal HF Script

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_hf", silent=1, usempi=False)

job.molecule(
    """
O   0.000000000   0.000000000  -0.041061554
H  -0.533194329   0.533194329  -0.614469223
H   0.533194329  -0.533194329  -0.614469223
""",
    basis="6-31g*",
    charge=0,
)
job.hf()

mol = job.run()
print("SCF energy:", mol.get_scf_energy())
```

For the shortest ordinary HF input, `job.hf()` sets:

```ini
[input]
method = hf
runtype = energy

[scf]
type = rhf
```

Every value can still be overridden through the section API.

## OpenQP Section Style

For precise control, use section calls. These map directly to OpenQP input
sections.

```python
job = OpenQP("custom_mrsf")

job.molecule("H 0 0 0; H 0 0 0.74", basis="6-31g*", charge=0)
job.input(method="tdhf", runtype="energy")
job.scf(type="rohf", multiplicity=3, conv=1.0e-7)
job.tdhf(type="mrsf", nstate=5, target=2)

mol = job.run()
```

Attribute assignment is also available for small edits:

```python
job.tdhf.nstate = 7
job.input.runtype = "grad"
```

Dotted keywords and sectioned dictionaries remain useful when another program
generates the input:

```python
job.set(**{
    "input.method": "tdhf",
    "scf.type": "rohf",
    "tdhf.type": "mrsf",
})

job.update({
    "input": {"method": "tdhf", "runtype": "energy"},
    "scf": {"type": "rohf", "multiplicity": 3},
    "tdhf": {"type": "mrsf", "nstate": 3},
})
```

## Molecular Geometry

`job.molecule(...)` accepts the same inline geometry forms used by the legacy
wrapper.

```python
job.molecule("H 0 0 0; H 0 0 0.74", basis="6-31g*")

job.molecule([
    ("H", 0.0, 0.0, 0.0),
    ("H", 0.0, 0.0, 0.74),
])

job.molecule("h2.xyz", basis="cc-pvdz")
```

Inline coordinates are Angstrom by default. If a script supplies Bohr
coordinates, pass `unit="Bohr"` and OpenQP will convert the geometry text before
loading it.

```python
job.molecule("H 0 0 0; H 0 0 1.4", unit="Bohr", basis="6-31g*")
```

## PySCF Conversion Bridge

OpenQP does not use PySCF-style constructor keywords as its main scripting
language. For mixed workflows, use the explicit conversion bridge:

```python
from oqp.openqp import OpenQP

job = OpenQP.from_pyscf(pyscf_mol, project="mixed_workflow")
job.mrsf(nstate=5)

mol = job.run()
```

The bridge reads common PySCF-like molecule attributes (`atom`, `basis`,
`charge`, `spin`, and `unit`) and translates them into OpenQP sections. After
conversion, use normal OpenQP workflow and section calls.

## Existing Input Files

If you already have an `.inp` file, run it directly with `Runner`.

```python
from pathlib import Path
from oqp.pyoqp import Runner

input_file = Path("h2o_mrsf.inp").resolve()
project = input_file.stem

runner = Runner(
    project=project,
    input_file=str(input_file),
    log=f"{project}.log",
)
runner.run()

print(runner.results()["energy"])
```

This path is closest to command-line OpenQP and is the best choice when the
input file itself is the reproducible record.

## Sectioned Runner Input

`Runner` also accepts an in-memory sectioned dictionary. This is the canonical
lower-level API used by front ends and by the high-level `OpenQP` wrapper.

```python
from oqp.pyoqp import Runner

config = {
    "input": {
        "system": "\nH 0.0 0.0 0.0\nH 0.0 0.0 0.74",
        "basis": "6-31g*",
        "method": "hf",
        "runtype": "energy",
    },
    "scf": {
        "type": "rhf",
        "multiplicity": "1",
    },
}

runner = Runner(
    project="h2",
    input_dict=config,
    log="h2.log",
    silent=1,
    usempi=False,
)
runner.run()
print(runner.results()["energy"])
```

Values may be strings; OpenQP validates and converts them through the same input
schema used by text input files.

## Reading Results

`job.run()` returns the OpenQP `Molecule` object and also stores it as `job.mol`.

```python
mol = job.run()

energy = mol.get_scf_energy()
coordinates_bohr = mol.get_system()
gradient = mol.get_grad()
raw_data = mol.get_data()
```

For orbital and matrix data, OpenQP creates tag-based accessors such as
`get_dm_a()`, `get_fock_a()`, `get_e_mo_a()`, `get_vec_mo_a()`,
`get_td_energies()`, and `get_soc_eval()` when the corresponding data are
available.

`Runner` gives two convenient result paths.

| Access pattern | Use |
| --- | --- |
| `runner.results()` | Compact Python summary with atoms, coordinates, energy, gradients, NAC, SOC, and raw data tags. |
| `runner.mol.get_results()` | JSON-friendly calculation summary similar to OpenQP output records. |
| `runner.mol` getters | Direct access to selected quantities and native OpenQP data tags. |

## Threading and MPI

For ordinary Python scripts, set `usempi=False` unless the script is launched in
an MPI environment.

OpenMP threads can be controlled through the OpenQP input schema:

```python
job = OpenQP("h2", usempi=False)
job.molecule("H 0 0 0; H 0 0 0.74", basis="6-31g*")
job.hf()
job.input.omp_threads = 8
job.run()
```

For large MPI jobs, keep the same Python API but launch the script with the MPI
launcher used on the machine.

## Validating Inputs

`Runner` validates input before dispatching expensive kernels. Front ends and
custom scripts can call the input checker directly when they need a preflight
report. See [Input Validation](api/input-validation.md) for the structured
diagnostic API.

For lower-level API details, see [Python API](api/python-runner.md) and
[Results and Molecule Data](api/results.md).
