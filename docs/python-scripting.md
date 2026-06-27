# Run OpenQP from Python

OpenQP can be driven entirely from Python. The Python API is meant to feel like
an OpenQP input file expressed as a script: define the molecule, choose the
workflow, run the calculation, and read results.

The recommended high-level entry point is `oqp.openqp.OpenQP`. It keeps the
native OpenQP section names available, while giving MRSF-TDDFT, HF, and DFT jobs
compact workflow helpers.

## Minimal MRSF-TDDFT Script

MRSF-TDDFT is a central OpenQP workflow. The compact helper sets the standard
MRSF blocks while leaving the detailed OpenQP keywords available.

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf", silent=1)

job.molecule(geometry="water", charge=0, multiplicity=3)
job.theory("mrsf-tddft", functional="bhhlyp", basis="6-31g*", nstate=3)

mol = job.run()
results = mol.get_results()

print("Ground/reference energy:", results["energy"])
print("TD energies:", results["td_energies"])
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
    charge=0,
    multiplicity=1,
)
job.theory("hf", basis="6-31g*")

mol = job.run()
print("SCF energy:", mol.get_scf_energy())
```

Every value can still be overridden through the section API.

## Minimal DFT Script

DFT uses its own helper so HF and Kohn-Sham jobs stay visually distinct.

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_pbe", silent=1, usempi=False)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory("dft", functional="pbe", basis="6-31g*")

mol = job.run()
print("DFT energy:", mol.get_scf_energy())
```

## OpenQP Section Style

For precise control, use section calls. These map directly to OpenQP input
sections.

```python
job = OpenQP("custom_mrsf")

job.molecule("H 0 0 0; H 0 0 0.74", charge=0, multiplicity=3)
job.control(runtype="energy")
job.input(method="tdhf", functional="bhhlyp")
job.input.basis = "6-31g*"
job.scf(type="rohf", multiplicity=3, conv=1.0e-7)
job.tdhf(type="mrsf", nstate=5, target=2)

mol = job.run()
```

Attribute assignment is also available for small edits:

```python
job.tdhf.nstate = 7
job.control(runtype="grad")
```

Dotted keywords and sectioned dictionaries remain useful when another program
generates the input:

```python
job.set(**{
    "input.method": "tdhf",
    "input.functional": "bhhlyp",
    "scf.type": "rohf",
    "tdhf.type": "mrsf",
})

job.update({
    "input": {"method": "tdhf", "functional": "bhhlyp", "runtype": "energy"},
    "scf": {"type": "rohf", "multiplicity": 3},
    "tdhf": {"type": "mrsf", "nstate": 3},
})
```

## Molecular Geometry

`job.molecule(...)` accepts named geometries, inline coordinates, atom lists,
file paths, and an optional second geometry for two-structure workflows such as
NACME. Keep method, functional, and basis setup in `job.theory(...)`.

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
job.molecule(system, system2, charge=0, multiplicity=3)
```

## PySCF Conversion Bridge

OpenQP does not use PySCF-style constructor keywords as its main scripting
language. For mixed workflows, use the explicit conversion bridge:

```python
from oqp.openqp import OpenQP

job = OpenQP.from_pyscf(pyscf_mol, project="mixed_workflow")
job.theory("mrsf-tddft", functional="bhhlyp", basis="6-31g*", nstate=5)

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

For ordinary Python scripts, set `usempi=False` unless the script is launched in
an MPI environment.

OpenMP threads can be controlled through `job.control(...)`:

```python
job = OpenQP("h2", usempi=False)
job.molecule("H 0 0 0; H 0 0 0.74", charge=0, multiplicity=1)
job.theory("hf", basis="6-31g*")
job.control(omp_threads=8)
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
