# Run OpenQP from Python

OpenQP can be driven entirely from Python. The Python API is meant to feel like
an OpenQP calculation expressed as a script: define the molecule, choose the
quantum theory, choose the workflow when it is not a plain energy calculation,
run the calculation, and read results.

The recommended high-level entry point is `oqp.openqp.OpenQP`. It keeps the
native OpenQP section names available for advanced cases, while keeping normal
scripts organized around six top-level ideas.

## API Shape

| Top-level call | Purpose |
| --- | --- |
| `job.molecule(...)` | Molecular identity: geometry, charge, multiplicity, and optional second geometry. |
| `job.theory.<model>(...)` | Quantum theory: HF, DFT, TDHF, TDDFT, SF-TDDFT, MRSF-TDDFT, functional, basis, response states, and reference type. |
| `job.workflow.*(...)` | Calculation type: gradient, Hessian, optimization, SOC, NACME, EKT, PCM, NMR, and related job workflows. Plain energy calculations need no workflow call. |
| `job.control(...)` | Hardware and runtime controls such as `usempi` and `omp_threads`. |
| `job.settings.*(...)` | Specialized detailed settings that are not part of ordinary molecule/theory/workflow setup, such as atom-wise basis assignment. |
| `job.run()` | Execute the calculation and return the OpenQP `Molecule` result object. |

## Minimal MRSF-TDDFT Script

MRSF-TDDFT is a central OpenQP workflow. The compact helper sets the standard
MRSF blocks while leaving the detailed OpenQP keywords available.

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

## Minimal HF Script

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_hf", silent=1)

job.molecule(
    """
O   0.000000000   0.000000000  -0.041061554
H  -0.533194329   0.533194329  -0.614469223
H   0.533194329  -0.533194329  -0.614469223
""",
    charge=0,
    multiplicity=1,
)
job.theory.hf(basis="6-31g*")

mol = job.run()
print("SCF energy:", mol.get_scf_energy())
```

Every value can still be overridden through detailed settings when needed.

## Minimal DFT Script

DFT uses its own helper so HF and Kohn-Sham jobs stay visually distinct.

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_pbe", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.dft(functional="pbe", basis="6-31g*")

mol = job.run()
print("DFT energy:", mol.get_scf_energy())
```

## Theory, Workflow, And Settings

The distinction is intentional: `theory` chooses the quantum model, `workflow`
chooses the kind of calculation to run, and `settings` holds specialized
low-level details.

```python
job = OpenQP("custom_mrsf")

job.molecule("H 0 0 0; H 0 0 0.74", charge=0)
job.theory.mrsf(
    functional="bhhlyp",
    basis="6-31g*",
    nstate=5,
)
job.settings.tdhf(target=2)
job.workflow.gradient(state=3)

mol = job.run()
```

Ordinary basis selection belongs with the theory:

```python
job.theory.dft(functional="pbe0", basis="def2-svp")
job.theory.tddft(functional="b3lyp5", basis="6-31g*", nstate=3)
job.theory.sf_tddft(functional="bhhlyp", basis="6-31g*", nstate=3)
```

For existing scripts, `job.theory("mrsf-tddft", ...)` and related string
dispatch calls remain supported. New examples prefer `job.theory.mrsf(...)`,
`job.theory.dft(...)`, and the other model-specific helpers.

For gradients, Python uses `state=...` even though the input-file keyword is
`[properties] grad`. HF/DFT reference gradients use `state=0`. Ordinary
TDHF/TDDFT state `1` is the first excited state. SF-TDDFT and MRSF-TDDFT state
`1` is the lowest spin-flip/MRSF target state, which can be the
multiconfigurational ground state.

Specialized atom-wise basis assignment belongs in `settings`:

```python
job.molecule("Br 0 0 0; H 0 0 1.4", charge=0, multiplicity=1)
job.theory.dft(functional="bhhlyp")
job.settings.basis(["LANL2DZ", "6-31g*"])
```

For tagged basis libraries, include atom tags in the geometry and map each tag:

```python
job.molecule(
    """
C  0.0  0.0  0.0  c1
H  0.0  0.0  1.0  h1
H  1.0  0.0  0.0  h1
""",
    charge=0,
)
job.theory.mrsf(functional="bhhlyp", nstate=5)
job.settings.basis(c1="cc-pvdz", h1="6-31g*")
```

Raw section updates remain useful when another program generates the input:

```python
job.settings.input(ispher="auto")
job.settings.scf(conv=1.0e-8)
job.settings.tdhf(target=2)

job.update({
    "input": {"method": "tdhf", "functional": "bhhlyp", "runtype": "energy"},
    "scf": {"type": "rohf", "multiplicity": 3},
    "tdhf": {"type": "mrsf", "nstate": 3},
})
```

## Molecular Geometry

`job.molecule(...)` accepts named geometries, inline coordinates, atom lists,
file paths, and an optional second geometry for two-structure workflows such as
NACME. Keep method, functional, and basis setup in `job.theory.<model>(...)`.

Named geometries keep small setup scripts short:

```python
job.molecule(geometry="water", charge=0, multiplicity=1)
job.molecule(geometry="h2o", charge=0, multiplicity=1)
job.molecule(geometry="ch4", charge=0, multiplicity=1)
```

OpenQP first checks a small built-in table for common molecules such as `water`,
`h2o`, `h2`, `ch4`, `methane`, `nh3`, and `co2`. If the name is not built in,
`source="auto"` tries PubChem.

```python
job.molecule(geometry="benzene", source="pubchem", charge=0, multiplicity=1)
```

To inspect or reuse the generated geometry text directly:

```python
from oqp.openqp import get_geometry

system = get_geometry("water")
job.molecule(system, charge=0, multiplicity=1)
```

Explicit molecular geometries still work as before:

```python
job.molecule("H 0 0 0; H 0 0 0.74", charge=0, multiplicity=1)

job.molecule([
    ("H", 0.0, 0.0, 0.0),
    ("H", 0.0, 0.0, 0.74),
])

job.molecule("h2.xyz", charge=0, multiplicity=1)
```

Inline coordinates are Angstrom by default. If a script supplies Bohr
coordinates, pass `unit="Bohr"` and OpenQP will convert the geometry text before
loading it.

```python
job.molecule("H 0 0 0; H 0 0 1.4", unit="Bohr", charge=0, multiplicity=1)
```

Two-geometry workflows can pass the second geometry directly:

```python
job.molecule(system, system2, charge=0)
```

## PySCF Conversion Bridge

OpenQP does not use PySCF-style constructor keywords as its main scripting
language. For mixed workflows, use the explicit conversion bridge:

```python
from oqp.openqp import OpenQP

job = OpenQP.from_pyscf(pyscf_mol, project="mixed_workflow")
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=5)

mol = job.run()
```

The bridge reads common PySCF-like molecule attributes (`atom`, `basis`,
`charge`, `spin`, and `unit`) and translates them into OpenQP sections. After
conversion, use normal OpenQP workflow and section calls.

## Existing Input Files and Lower-Level API

For direct `.inp` file execution or explicit sectioned dictionaries, use the
lower-level `Runner` API. Those examples are kept in the
[Python API](api/python-runner.md) reference so this manual page stays focused
on the compact `OpenQP` scripting style.

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

Runtime controls belong in `job.control(...)`. For ordinary Python scripts, use
`usempi=False` unless the script is launched in an MPI environment. OpenMP
threads can be set in the same call:

```python
job = OpenQP("h2")
job.molecule("H 0 0 0; H 0 0 0.74", charge=0, multiplicity=1)
job.theory.hf(basis="6-31g*")
job.control(usempi=False, omp_threads=8)
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
