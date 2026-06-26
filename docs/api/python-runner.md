# Python Runner

`oqp.pyoqp.Runner` is the main Python entry point for OpenQP calculations. It
loads the same configuration used by input files, runs the selected workflow,
and keeps the resulting `Molecule` object available as `runner.mol`.

For a user-level guide with complete scripts, see
[Run OpenQP from Python](../python-scripting.md).

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

## Signature

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

## File-Based Runs

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

## In-Memory Runs

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

## MRSF-TDDFT Example

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

## Runtime Methods

| Method | Returns | Use |
| --- | --- | --- |
| `run(test_mod=False)` | `None` | Executes the calculation selected by `[input] runtype`. |
| `results()` | `dict` | Returns a Python summary with atoms, coordinates, energies, gradients, NAC, SOC, and raw data tags. |
| `reload()` | `None` | Reloads guess data when the selected guess mode asks for JSON data. |
| `back_door(data)` | `None` | Supplies previous-state data for advanced internal workflows. |
| `test()` | `(message, diff)` | Compares against reference data in OpenQP test mode. |

## Convenience Wrapper

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

This wrapper is useful for compact scripts and front-end prototypes. For
production automation, prefer `Runner` directly because it is the canonical
execution API.
