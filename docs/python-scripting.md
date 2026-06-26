# Run OpenQP from Python

OpenQP can be driven entirely from a Python script. The `openqp` command-line
program and the Python runner use the same input schema and the same native
OpenQP engine; the Python path simply lets the script create inputs, launch the
calculation, and read results without leaving Python.

Use Python scripting when you want to:

- generate many related OpenQP inputs programmatically
- run OpenQP inside notebooks, tests, services, or workflow managers
- collect energies, gradients, SOC, NAC, TDDFT, or raw matrix data for analysis
- connect OpenQP to optimizers, sampling loops, or custom post-processing code

The main user-facing entry point is `oqp.pyoqp.Runner`.

## Complete Minimal Script

This script builds a water HF input in Python, runs OpenQP, and prints the final
SCF energy.

```python
from oqp.pyoqp import Runner

config = {
    "input": {
        "system": """
O   0.000000000   0.000000000  -0.041061554
H  -0.533194329   0.533194329  -0.614469223
H   0.533194329  -0.533194329  -0.614469223
""",
        "charge": "0",
        "basis": "6-31g*",
        "method": "hf",
        "runtype": "energy",
    },
    "guess": {
        "type": "huckel",
    },
    "scf": {
        "type": "rhf",
        "multiplicity": "1",
    },
}

runner = Runner(
    project="h2o_hf",
    input_dict=config,
    log="h2o_hf.log",
    silent=1,
    usempi=False,
)
runner.run()

mol = runner.mol
print("SCF energy:", mol.get_scf_energy())
```

The dictionary follows the same section names and keyword names as an OpenQP
input file. Values may be strings; OpenQP converts them through the normal input
schema before the calculation starts.

## Running an Existing Input File

If you already have an `.inp` file, a Python script can run it directly.

```python
from pathlib import Path
from oqp.pyoqp import Runner

input_file = Path("h2o.inp").resolve()
project = input_file.stem

runner = Runner(
    project=project,
    input_file=str(input_file),
    log=f"{project}.log",
)
runner.run()

print(runner.results()["energy"])
```

This is useful for batch scripts that prepare a list of input files and run them
under Python control.

## MRSF-TDDFT Script

MRSF-TDDFT workflows can also be launched from Python. The example below uses an
ROHF triplet reference and asks for three MRSF-TDDFT states.

```python
from oqp.pyoqp import Runner

config = {
    "input": {
        "system": """
O   0.000000000   0.000000000  -0.041061554
H  -0.533194329   0.533194329  -0.614469223
H   0.533194329  -0.533194329  -0.614469223
""",
        "charge": "0",
        "basis": "6-31g*",
        "method": "tdhf",
        "runtype": "energy",
    },
    "guess": {
        "type": "huckel",
    },
    "scf": {
        "type": "rohf",
        "multiplicity": "3",
    },
    "tdhf": {
        "type": "mrsf",
        "nstate": "3",
    },
}

runner = Runner(
    project="h2o_mrsf",
    input_dict=config,
    log="h2o_mrsf.log",
    silent=1,
)
runner.run()

results = runner.mol.get_results()
print("Ground/reference energy:", results["energy"])
print("TD energies:", results["td_energies"])
```

The same pattern applies to gradients, optimization, MECI/MECP/TCI, NACME, SOC,
MRSF-EKT, Hessians, and property calculations: set `[input] runtype` and the
needed workflow sections exactly as in an input file.

## Reading Results

`Runner` gives two convenient result paths.

| Access pattern | Use |
| --- | --- |
| `runner.results()` | Compact Python summary with atoms, coordinates, energy, gradients, NAC, SOC, and raw data tags. |
| `runner.mol.get_results()` | JSON-friendly calculation summary similar to OpenQP output records. |
| `runner.mol` getters | Direct access to selected quantities and native OpenQP data tags. |

Common getters include:

```python
mol = runner.mol

energy = mol.get_scf_energy()
coordinates_bohr = mol.get_system()
gradient = mol.get_grad()
raw_data = mol.get_data()
```

For orbital and matrix data, OpenQP creates tag-based accessors such as
`get_dm_a()`, `get_fock_a()`, `get_e_mo_a()`, `get_vec_mo_a()`,
`get_td_energies()`, and `get_soc_eval()` when the corresponding data are
available.

## Threading and MPI

For ordinary Python scripts, set `usempi=False` unless the script is launched in
an MPI environment.

OpenMP threads can be controlled inside the Python input dictionary:

```python
config = {
    "input": {
        "system": "\nH 0 0 0\nH 0 0 0.74",
        "basis": "6-31g*",
        "method": "hf",
        "runtype": "energy",
        "omp_threads": "8",
    },
    "scf": {
        "type": "rhf",
    },
}
```

For large MPI jobs, keep the same `Runner` pattern but launch the script with
the MPI launcher used on the machine.

## Validating Inputs Before Running

`Runner` validates input before dispatching expensive kernels. Front ends and
custom scripts can call the input checker directly when they need a preflight
report. See [Input Validation](api/input-validation.md) for the structured
diagnostic API.

For the lower-level API details, see [Python Runner](api/python-runner.md) and
[Results and Molecule Data](api/results.md).
