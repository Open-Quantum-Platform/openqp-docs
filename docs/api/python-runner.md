# Python API

OpenQP exposes two Python layers.

| Layer | Import | Use |
| --- | --- | --- |
| High-level wrapper | `from oqp.openqp import OpenQP` | OpenQP-native scripts with molecule, workflow, and section-style keyword setup. |
| Runner | `from oqp.pyoqp import Runner` | Existing input files, explicit sectioned dictionaries, and front ends that already build OpenQP input data. |

Both layers use the same OpenQP input schema and the same native calculation
engine. `OpenQP` builds a sectioned dictionary and passes it to `Runner`.

For a user-level guide with complete scripts, see
[Run OpenQP from Python](../python-scripting.md).

## High-Level OpenQP Wrapper

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf", silent=1)
job.molecule(
    """
O   0.000000   0.000000  -0.041062
H  -0.533194   0.533194  -0.614469
H   0.533194  -0.533194  -0.614469
""",
    basis="6-31g*",
)
job.mrsf(nstate=3)

mol = job.run()
print(mol.get_results()["td_energies"])
```

### Constructor

```python
OpenQP(
    project="oqp_project",
    log=None,
    silent=0,
    usempi=True,
    config=None,
    **sections,
)
```

| Argument | Meaning |
| --- | --- |
| `project` | Project name used in logs and output files. It can be passed positionally, as in `OpenQP("h2o")`. |
| `log` | Log file path. Defaults to `<project>.log`. |
| `silent` | `0` prints parsed input and normal messages; `1` suppresses them. |
| `usempi` | Enables MPI-aware behavior when the runtime supports it. |
| `config` | Optional sectioned OpenQP input dictionary. |
| `**sections` | Optional section dictionaries, for example `input={...}` or `scf={...}`. |

The constructor is intentionally runtime-focused. Molecule and method setup use
OpenQP-native methods after construction.

### Molecule Setup

```python
job.molecule(
    "H 0 0 0; H 0 0 0.74",
    basis="6-31g*",
    charge=0,
)
```

```python
job.molecule([
    ("H", 0.0, 0.0, 0.0),
    ("H", 0.0, 0.0, 0.74),
])
```

| Method | Returns | Use |
| --- | --- | --- |
| `molecule(system, basis=None, charge=None, unit="Angstrom", **kwargs)` | `OpenQP` | Writes molecular data into `[input]`, including `system`, `basis`, `charge`, and any extra input-section keyword. |

Inline coordinates are Angstrom by default. Use `unit="Bohr"` for Bohr input
coordinates.

### Workflow Helpers

```python
job.mrsf(nstate=3)
job.hf()
```

| Method | Returns | Use |
| --- | --- | --- |
| `hf(reference="rhf", runtype="energy", multiplicity=None, **scf_keywords)` | `OpenQP` | Sets `[input] method=hf`, `[input] runtype`, and `[scf] type`. |
| `mrsf(nstate=3, reference="rohf", multiplicity=3, runtype="energy", **tdhf_keywords)` | `OpenQP` | Sets the standard MRSF-TDDFT `[input]`, `[scf]`, and `[tdhf]` blocks. |

These helpers are only shorthand for OpenQP sections. Advanced calculations can
always override or extend the sections directly.

### Section Updates

```python
job.input(method="tdhf", runtype="energy")
job.scf(type="rohf", multiplicity=3)
job.tdhf(type="mrsf", nstate=3)

job.tdhf.nstate = 5

job.set(**{"input.method": "tdhf", "tdhf.type": "mrsf"})
job.update({"scf": {"type": "rohf", "multiplicity": 3}})
```

| Method | Returns | Use |
| --- | --- | --- |
| `section(name, **kwargs)` | `OpenQP` | Updates one OpenQP input section. |
| `set(**kwargs)` | `OpenQP` | Updates dotted OpenQP keywords or section dictionaries. |
| `update(config=None, **kwargs)` | `OpenQP` | Merges a sectioned dictionary plus optional section overrides. |
| `to_input_dict()` | `dict` | Returns the sectioned dictionary that will be passed to `Runner`. |
| `run(run_type=None)` | `Molecule` | Builds `Runner`, executes the calculation, stores `job.runner` and `job.mol`, and returns the `Molecule`. |

`oqp.openqp.OQP` is an alias for `OpenQP`.

### PySCF Conversion

`OpenQP.from_pyscf(mol, **kwargs)` is an explicit compatibility bridge. It
reads `atom`, `basis`, `charge`, `spin`, and `unit` attributes from a PySCF-like
object, translates them into OpenQP sections, and returns an `OpenQP` job.

```python
job = OpenQP.from_pyscf(pyscf_mol, project="mixed_workflow")
job.mrsf(nstate=5)
mol = job.run()
```

After conversion, use normal OpenQP workflow and section calls.

## Runner

`oqp.pyoqp.Runner` loads the same configuration used by input files, runs the
selected workflow, and keeps the resulting `Molecule` object available as
`runner.mol`.

```python
from oqp.pyoqp import Runner

runner = Runner(
    project="water_mrsf",
    input_file="water_mrsf.inp",
    log="water_mrsf.log",
    silent=0,
    usempi=True,
)
runner.run()

summary = runner.results()
print(summary["energy"])
```

### Signature

```python
Runner(
    project=None,
    input_file=None,
    log=None,
    input_dict=None,
    silent=0,
    usempi=True,
)
```

| Argument | Type | Meaning |
| --- | --- | --- |
| `project` | `str` or `None` | Project name used in logs and output files. |
| `input_file` | `str` or `None` | Path to an OpenQP input file. |
| `log` | `str` or `None` | Log file path. |
| `input_dict` | `dict` or `None` | Sectioned input dictionary. If supplied, it is used instead of `input_file`. |
| `silent` | `int` | `0` prints parsed input and normal messages; `1` suppresses them. |
| `usempi` | `bool` | Enables MPI-aware behavior when the runtime supports it. |

`Runner` validates the parsed input before the calculation starts. A validation
failure prints an input-check report and exits before expensive kernels run.

### File-Based Runs

File-based runs are closest to command-line OpenQP:

```python
from pathlib import Path
from oqp.pyoqp import Runner

input_file = Path("examples/HF/H2O_RHF-HF_ENERGY.inp").resolve()
project = input_file.stem

runner = Runner(
    project=project,
    input_file=str(input_file),
    log=f"{project}.log",
)
runner.run()
```

Use this pattern when you want reproducible inputs, logs, JSON restart files,
and output files on disk.

### In-Memory Runs

For notebooks, tests, services, or agents, pass a sectioned dictionary through
`input_dict`.

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

The dictionary is organized as `{section: {keyword: value}}`, matching the input
file sections. Values can be strings; the OpenQP parser converts them using the
same schema used by file inputs.

### MRSF-TDDFT Example

MRSF-TDDFT normally starts from an open-shell reference. This compact example
uses an ROHF triplet reference and asks for MRSF-TDDFT states.

```python
from oqp.pyoqp import Runner

config = {
    "input": {
        "system": "\nO 0.000000 0.000000 -0.041062\nH -0.533194 0.533194 -0.614469\nH 0.533194 -0.533194 -0.614469",
        "basis": "6-31g*",
        "method": "tdhf",
        "runtype": "energy",
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

runner = Runner(project="water_mrsf", input_dict=config, log="water_mrsf.log")
runner.run()

mol = runner.mol
print(mol.get_results()["td_energies"])
```

### Runtime Methods

| Method | Returns | Use |
| --- | --- | --- |
| `run(test_mod=False)` | `None` | Executes the calculation selected by `[input] runtype`. |
| `results()` | `dict` | Returns a Python summary with atoms, coordinates, energies, gradients, NAC, SOC, and raw data tags. |
| `reload()` | `None` | Reloads guess data when the selected guess mode asks for JSON data. |
| `back_door(data)` | `None` | Supplies previous-state data for advanced internal workflows. |
| `test()` | `(message, diff)` | Compares against reference data in OpenQP test mode. |

## Legacy Dotted-Keyword Wrapper

`oqp.openqp.OPENQP` accepts dotted keyword names such as `input.system` and
`scf.type`, normalizes inline geometries, and then constructs a `Runner`.

```python
from oqp.openqp import OPENQP

op = OPENQP({
    "input.system": "H 0 0 0; H 0 0 0.74",
    "input.basis": "6-31g*",
    "input.method": "hf",
    "input.runtype": "energy",
    "scf.type": "rhf",
})
mol = op.run()
```

This wrapper is retained for existing scripts. New scripts should prefer
`OpenQP` for OpenQP-native scripting or `Runner` for direct input-file and
section-dictionary execution.
