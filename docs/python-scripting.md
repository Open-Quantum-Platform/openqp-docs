# Run OpenQP from Python

OpenQP can be driven entirely from Python. This is useful for notebooks, custom
workflows, high-throughput studies, and mixed OpenQP/PySCF scripts where a
program creates the molecule, chooses the method, launches the calculation, and
then reads the resulting data.

The recommended high-level entry point is `oqp.openqp.OpenQP`. It accepts a
small set of familiar molecular arguments and writes them into the normal
OpenQP input schema. The lower-level `oqp.pyoqp.Runner` interface remains
available when a script needs to pass an existing OpenQP input file or an
explicit sectioned dictionary.

## Minimal Script

```python
from oqp.openqp import OpenQP

job = OpenQP(
    atom=[
        ("O", 0.000000000, 0.000000000, -0.041061554),
        ("H", -0.533194329, 0.533194329, -0.614469223),
        ("H", 0.533194329, -0.533194329, -0.614469223),
    ],
    basis="6-31g*",
    charge=0,
    project="h2o_hf",
    silent=1,
    usempi=False,
)

job.input(method="hf", runtype="energy")
job.scf(type="rhf", multiplicity=1)

mol = job.run()
print("SCF energy:", mol.get_scf_energy())
```

`atom`, `basis`, and `charge` intentionally resemble common PySCF inputs, but
the calculation still uses OpenQP keywords internally. Section calls such as
`job.input(...)`, `job.scf(...)`, and `job.tdhf(...)` are shorthand for editing
the corresponding OpenQP input sections.

## MRSF-TDDFT Script

MRSF-TDDFT calculations normally use an open-shell reference. The example below
uses an ROHF triplet reference and requests three MRSF-TDDFT states.

```python
from oqp.openqp import OpenQP

job = OpenQP(
    atom="""
O   0.000000000   0.000000000  -0.041061554
H  -0.533194329   0.533194329  -0.614469223
H   0.533194329  -0.533194329  -0.614469223
""",
    basis="6-31g*",
    charge=0,
    project="h2o_mrsf",
    silent=1,
)

job.input(method="tdhf", runtype="energy")
job.scf(type="rohf", multiplicity=3)
job.tdhf(type="mrsf", nstate=3)

mol = job.run()
results = mol.get_results()

print("Ground/reference energy:", results["energy"])
print("TD energies:", results["td_energies"])
```

The same pattern applies to gradients, optimization, MECI/MECP/TCI, NACME, SOC,
MRSF-EKT, Hessians, and property calculations: set `[input] runtype` and the
needed workflow sections exactly as in an OpenQP input file.

## PySCF-Style Inputs

`OpenQP` accepts the most common PySCF molecular arguments directly:

| Argument | Meaning in OpenQP |
| --- | --- |
| `atom` or `system` | Written to `[input] system`. |
| `basis` | Written to `[input] basis`. |
| `charge` | Written to `[input] charge`. |
| `spin` | PySCF convention `2S`; converted to `[scf] multiplicity = spin + 1`. |
| `multiplicity` | Written directly to `[scf] multiplicity`. |
| `unit` | `Angstrom` by default; `Bohr` inputs are converted before OpenQP reads them. |

For a PySCF-like object, use `from_pyscf`:

```python
from oqp.openqp import OpenQP

# pyscf_mol may be a real pyscf.gto.Mole object or any object with
# atom, basis, charge, spin, and unit attributes.
job = OpenQP.from_pyscf(pyscf_mol, project="mixed_workflow")
job.input(method="tdhf", runtype="energy")
job.scf(type="rohf")
job.tdhf(type="mrsf", nstate=5)

mol = job.run()
```

This conversion is deliberately small. It helps scripts share molecular setup
between PySCF and OpenQP, while OpenQP-specific methods, grids, response
settings, and MRSF-TDDFT keywords stay explicit.

## Keyword Styles

All of the following forms update the same OpenQP input dictionary:

```python
job.input(method="tdhf", runtype="energy")
job.scf(type="rohf", multiplicity=3)
job.tdhf(type="mrsf", nstate=3)

job.tdhf.nstate = 5

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

Use section calls for ordinary scripts. Use dotted keywords or sectioned
dictionaries when generating inputs programmatically from another tool.

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

`Runner` gives two convenient result paths.

| Access pattern | Use |
| --- | --- |
| `runner.results()` | Compact Python summary with atoms, coordinates, energy, gradients, NAC, SOC, and raw data tags. |
| `runner.mol.get_results()` | JSON-friendly calculation summary similar to OpenQP output records. |
| `runner.mol` getters | Direct access to selected quantities and native OpenQP data tags. |

For the high-level wrapper, `job.run()` returns the same `Molecule` object and
also stores it as `job.mol`.

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

## Threading and MPI

For ordinary Python scripts, set `usempi=False` unless the script is launched in
an MPI environment.

OpenMP threads can be controlled through the OpenQP input schema:

```python
job = OpenQP(atom="H 0 0 0; H 0 0 0.74", basis="6-31g*", usempi=False)
job.input(method="hf", runtype="energy", omp_threads=8)
job.scf(type="rhf")
job.run()
```

For large MPI jobs, keep the same Python API but launch the script with the MPI
launcher used on the machine.

## Validating Inputs

`Runner` validates input before dispatching expensive kernels. Front ends and
custom scripts can call the input checker directly when they need a preflight
report. See [Input Validation](api/input-validation.md) for the structured
diagnostic API.

For lower-level API details, see [Python Runner](api/python-runner.md) and
[Results and Molecule Data](api/results.md).
