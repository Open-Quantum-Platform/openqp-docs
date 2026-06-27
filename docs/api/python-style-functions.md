# Python-Style API Function Reference

This page lists the user-facing functions in the high-level
`oqp.openqp.OpenQP` API. It is a compact reference for scripts that use the
Python-style setup:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf")
job.molecule(geometry="water", charge=0)
job.theory("mrsf-tddft", functional="bhhlyp", basis="6-31g*", nstate=3)
job.workflow.gradient(state=1)
job.control(usempi=False, omp_threads=8)
mol = job.run()
```

For complete examples, see [Run OpenQP from Python](../python-scripting.md).
For direct file or dictionary execution, see [Python Runner](python-runner.md).

## Top-Level Model

| Namespace | Purpose |
| --- | --- |
| `job.molecule(...)` | Geometry, charge, multiplicity, and optional second geometry. |
| `job.theory(...)` | Quantum theory, including method, functional, ordinary basis, reference, and response-state count. |
| `job.workflow.*(...)` | Calculation type: gradient, Hessian, optimization, SOC, NACME, EKT, PCM, NMR, and related workflows. |
| `job.control(...)` | Hardware/runtime controls such as MPI and OpenMP thread settings. |
| `job.settings.*(...)` | Specialized detailed settings, such as atom-wise basis assignment or direct section overrides. |
| `job.run()` | Execute the configured OpenQP calculation. |

## Imports

| Name | Import | Use |
| --- | --- | --- |
| `OpenQP` | `from oqp.openqp import OpenQP` | Recommended high-level Python-style API. |
| `OQP` | `from oqp.openqp import OQP` | Short alias for `OpenQP`. |
| `OPENQP` | `from oqp.openqp import OPENQP` | Legacy dotted-key wrapper retained for older scripts. |
| `get_geometry` | `from oqp.openqp import get_geometry` | Resolve a named molecule to OpenQP geometry text. |

## Object Construction

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `OpenQP(project="oqp_project", log=None, silent=0, usempi=True, config=None, **sections)` | `OpenQP` | Initializes a validated OpenQP input dictionary. | `project` may be positional. Prefer `job.control(usempi=...)` for high-level scripts. |
| `OpenQP.from_pyscf(mol, **kwargs)` | `OpenQP` | Reads PySCF-like `atom`, `basis`, `charge`, `spin`, and `unit`. | PySCF `spin` is `2S`, so OpenQP multiplicity is `spin + 1`. Bohr units include `Bohr`, `B`, `b`, `au`, and `a.u.`. |

Runtime keyword arguments accepted by `from_pyscf(...)` are `project`, `log`,
`silent`, `usempi`, and `config`. Any remaining keyword arguments are applied
with `job.update(...)`.

## Molecule Functions

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `job.molecule(system=None, system2=None, basis=None, charge=None, multiplicity=None, unit="Angstrom", geometry=None, geometry2=None, source="auto", timeout=10, **kwargs)` | `OpenQP` | `[input] system`, optional `[input] system2`, `[input] charge`, optional `[scf] multiplicity`, and extra `[input]` keywords. | Use either `system` or `geometry`, not both. `basis=...` remains accepted for compatibility; new scripts should put ordinary basis selection in `job.theory(...)`. |
| `get_geometry(query, source="auto", timeout=10)` | `str` | None. | Resolves a built-in molecule first, then PubChem when `source="auto"`. |
| `builtin_geometry(query)` | `str` | None. | Uses OpenQP's local small-molecule table. |
| `pubchem_geometry(query, timeout=10)` | `str` | None. | Fetches a 3D conformer from PubChem. Requires network access. |
| `geometry_from_sdf(sdf, query)` | `str` | None. | Converts a V2000 SDF block to OpenQP inline geometry text. |
| `normalize_system(system, unit="Angstrom")` | `str` | None. | Normalizes inline atom rows, semicolon-separated rows, lists, tuples, or file paths. |

`geometry=...` currently recognizes common names such as `water`, `h2o`, `h2`,
`ch4`, `methane`, `nh3`, `ammonia`, `co2`, and `carbon dioxide` from the local
table before trying PubChem.

## Theory Functions

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `job.theory(method, functional=None, basis=None, runtype=None, nstate=3, reference=None, **keywords)` | `OpenQP` | Dispatches to HF, DFT, TDHF, TDDFT, SF-TDDFT, or MRSF-TDDFT setup. | Recommended entry point for ordinary method setup. `basis`, `functional`, and `nstate` belong here. |
| `job.hf(reference="rhf", runtype=None, multiplicity=None, basis=None, **scf_keywords)` | `OpenQP` | `[input] method=hf`, clears `[input] functional`, optional `[input] runtype`, optional `[input] basis`, and `[scf]` keywords. | Clears any old DFT functional so reused jobs become true HF jobs. |
| `job.dft(functional, reference="rhf", runtype=None, multiplicity=None, basis=None, **scf_keywords)` | `OpenQP` | `[input] method=hf`, `[input] functional`, optional `[input] runtype`, optional `[input] basis`, and `[scf]` keywords. | OpenQP uses `method=hf` plus non-empty `functional` for DFT. |
| `job.tddft(functional, reference="rhf", runtype=None, multiplicity=1, basis=None, nstate=3, **tdhf_keywords)` | `OpenQP` | `[input] method=tdhf`, `[input] functional`, optional `[input] basis`, `[scf]` reference, and `[tdhf] nstate`. | Equivalent to `job.theory("tddft", ...)`. |
| `job.sf_tddft(functional, reference="rohf", runtype=None, multiplicity=3, basis=None, nstate=3, **tdhf_keywords)` | `OpenQP` | TDDFT response setup with `[tdhf] type=sf`. | Equivalent to `job.theory("sf-tddft", ...)`. |
| `job.mrsf(nstate=3, reference="rohf", multiplicity=3, runtype=None, functional=None, basis=None, **tdhf_keywords)` | `OpenQP` | `[input] method=tdhf`, optional functional/basis/runtype, `[scf] type`, `[scf] multiplicity`, `[tdhf] type=mrsf`, `[tdhf] nstate`, and extra `[tdhf]` keywords. | Used by `job.theory("mrsf-tddft", ...)`; the usual ROHF triplet reference is implicit in the high-level API. |
| `job.soc(nstate=3, functional=None, reference="rohf", reference_multiplicity=3, soc_2e=1, basis=None, **tdhf_keywords)` | `OpenQP` | Full legacy compact MRSF-SOC setup. | New scripts should prefer `job.theory("mrsf-tddft", ...); job.workflow.soc(...)`. |

## Workflow Namespace

Workflow calls live under `job.workflow`. Plain energy calculations do not need
a workflow call.

| Function | Returns | Runtype | Writes or changes | Constraints |
| --- | --- | --- | --- | --- |
| `job.workflow.energy()` | `OpenQP` | `energy` | `[input] runtype=energy`. | Optional; energy is already the default. |
| `job.workflow.gradient(state=None, grad=None, **kwargs)` | `OpenQP` | `grad` | `[properties] grad` plus extra `[properties]` keywords. | Prefer `state=...`; `grad=...` is legacy. Use one or the other. |
| `job.workflow.hess(**kwargs)` | `OpenQP` | `hess` | `[hess]` keywords. | Alias: `job.workflow.hessian(...)`. |
| `job.workflow.hessian(**kwargs)` | `OpenQP` | `hess` | `[hess]` keywords. | Same as `job.workflow.hess(...)`. |
| `job.workflow.optimize(runtype=None, **kwargs)` | `OpenQP` | `optimize` by default | `[optimize]` plus selected backend section. | Routes backend options such as `coordsys`, `trust`, and `constraints_file` to `[oqp]` or `[geometric]`. |
| `job.workflow.meci(**kwargs)` | `OpenQP` | `meci` | `[optimize]` plus backend section. | Crossing-search optimizer workflow. |
| `job.workflow.mecp(**kwargs)` | `OpenQP` | `mecp` | `[optimize]` plus backend section. | Crossing-search optimizer workflow. |
| `job.workflow.tci(**kwargs)` | `OpenQP` | `tci` | `[optimize]` plus backend section. | Crossing-search optimizer workflow. |
| `job.workflow.mep(**kwargs)` | `OpenQP` | `mep` | `[optimize]` plus backend section. | Reaction-path workflow. |
| `job.workflow.ts(**kwargs)` | `OpenQP` | `ts` | `[optimize]` plus backend section. | Transition-state workflow. |
| `job.workflow.irc(**kwargs)` | `OpenQP` | `irc` | `[optimize]` plus backend section. | Reaction-path workflow. |
| `job.workflow.neb(**kwargs)` | `OpenQP` | `neb` | `[optimize]` plus backend section. | NEB workflow. |
| `job.workflow.nac(**kwargs)` | `OpenQP` | `nac` | `[nac]` keywords. | Currently requires MRSF-TDDFT. |
| `job.workflow.nacme(**kwargs)` | `OpenQP` | `nacme` | `[nac]` keywords. | Currently requires MRSF-TDDFT. |
| `job.workflow.ekt(ip=False, ea=False, **kwargs)` | `OpenQP` | `ekt` | `[ekt]` keywords. | Currently requires MRSF-TDDFT and at least one of `ip=True` or `ea=True`. |
| `job.workflow.soc(soc_2e=1, **tdhf_keywords)` | `OpenQP` | `soc` | `[input] soc_2e` and optional `[tdhf]` keywords. | Requires MRSF-TDDFT. Do not pass `multiplicity`; SOC computes singlet and triplet roots internally. |
| `job.workflow.pcm(**kwargs)` | `OpenQP` | `energy` | `[pcm]` keywords. | Current production path requires HF/DFT reference-SCF, RHF/ROHF, `backend="ddx"`, and `mode="reference_scf"`. |
| `job.workflow.nmr(gauge=None, **kwargs)` | `OpenQP` | `energy` | `[properties] scf_prop=nmr`, `[properties] nmr_gauge`, and extra `[properties]` keywords. | Requires HF/DFT reference-SCF. CGO is RHF-only; use GIAO for open-shell references. |
| `job.workflow(runtype=None, **kwargs)` | `OpenQP` | selected `runtype` | Delegates to `job.control(...)`. | Compatibility form; prefer named workflow calls. |

## Settings Namespace

`job.settings` is for detailed settings that are too specialized for the common
molecule/theory/workflow path.

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `job.settings.basis(basis=None, **tags)` | `OpenQP` | Atom-wise `[input] basis` assignment. | Use an ordered list or semicolon-separated string for atom-order basis assignment. Use keyword tags for `basis=library`. A single global basis belongs in `job.theory(..., basis=...)`. |
| `job.settings.<section>(**kwargs)` | `OpenQP` | The named OpenQP input section. | Direct section access for advanced keywords such as `job.settings.scf(conv=1.0e-8)`. |
| `job.settings.<section>.<option> = value` | None | One OpenQP keyword. | Attribute assignment form for detailed edits. |

Examples:

```python
job.settings.basis(["LANL2DZ", "6-31g*"])
job.settings.basis(c1="cc-pvdz", h1="6-31g*")
job.settings.scf(conv=1.0e-8)
job.settings.tdhf(target=2)
```

## Control Namespace

`job.control(...)` is for runtime controls and compatibility routing, not for
choosing the electronic structure method.

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `job.control(runtype=None, omp_threads=None, usempi=None, **kwargs)` | `OpenQP` | Optional `[input] runtype`, optional `[input] omp_threads`, and runtime-only `usempi`. | If `kwargs` are supplied, they are routed according to the active runtype. |

Examples:

```python
job.control(usempi=False, omp_threads=8)
job.control(runtype="optimize", lib="oqp", coordsys="tric", trust=0.2)
job.control(runtype="grad", state=0)
```

For new scripts, prefer `job.workflow.optimize(...)`,
`job.workflow.gradient(...)`, and other named workflow calls when setting
workflow-specific keywords.

## Section and Config Functions

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `job.section(section, **kwargs)` | `OpenQP` | The named OpenQP section. | Raises `KeyError` for unknown sections. |
| `job.set(**kwargs)` | `OpenQP` | Dotted OpenQP keywords or section dictionaries. | Accepts forms such as `job.set(**{"input.method": "tdhf"})` and `job.set(input={"method": "tdhf"})`. |
| `job.update(config=None, **kwargs)` | `OpenQP` | Merges a sectioned dictionary plus optional overrides. | Useful when another program already builds `{section: {keyword: value}}`. |
| `job.to_input_dict()` | `dict` | None. | Returns a copy of the exact sectioned dictionary passed to `Runner`. |
| `job.run(run_type=None)` | `Molecule` | Creates `job.runner`, runs OpenQP, stores `job.mol`. | `run_type` is a final override for `[input] runtype`. |

## Top-Level Section Proxies

The high-level object also exposes native section helpers directly:

```python
job.input(method="tdhf", functional="bhhlyp")
job.scf(type="rohf", multiplicity=3)
job.tdhf(type="mrsf", nstate=5)
job.tdhf.nstate = 7
```

These are kept for users who want a Python spelling of the input file. The
preferred compact style is:

```python
job.molecule(...)
job.theory(...)
job.workflow(...)
job.control(...)
job.settings.basis(...)
job.run()
```

## State Numbering

| Method family | Python gradient state | Input keyword value |
| --- | --- | --- |
| HF/DFT | `job.workflow.gradient(state=0)` | `[properties] grad=0` means the reference ground state. |
| TDHF/TDDFT | `job.workflow.gradient(state=1)` | `[properties] grad=1` means the first excited state. |
| SF-TDDFT/MRSF-TDDFT | `job.workflow.gradient(state=1)` | `[properties] grad=1` means the lowest spin-flip/MRSF target state, which can be the multiconfigurational ground state. |

## Legacy Wrapper

`OPENQP` accepts dotted keyword names and constructs a `Runner` immediately.
It is retained for existing scripts.

| Function | Returns | Writes or changes | Notes |
| --- | --- | --- | --- |
| `OPENQP(cfg)` | `OPENQP` | Builds a `Runner` from dotted keys such as `input.system` and `scf.type`. | New scripts should prefer `OpenQP`. |
| `op.set(**kwargs)` | `OPENQP` | Updates dotted keys and reloads the current `Molecule` config. | Legacy behavior. |
| `op.run(run_type=None)` | `Molecule` | Runs the existing `Runner`. | Legacy behavior. |
