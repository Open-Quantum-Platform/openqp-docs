# `[input]`

The `[input]` section defines the molecule, electronic-structure method, run
type, basis convention, and process-level threading. Most workflows require this
section.

## Minimal Example

```ini
[input]
system=
   O   0.000000000   0.000000000  -0.041061554
   H  -0.533194329   0.533194329  -0.614469223
   H   0.533194329  -0.533194329  -0.614469223
charge=0
runtype=energy
method=hf
basis=6-31g*
```

## Keywords

### `system`

| Field | Value |
| --- | --- |
| Type | string or multiline coordinate block |
| Default | empty |
| Values | XYZ file path, or inline atom coordinates |
| Used by | all molecular workflows |

Defines the molecular geometry. When `system` is a single non-empty line, OpenQP
interprets it as a file path. When `system=` is followed by indented atom lines,
OpenQP reads those lines as inline coordinates.

Inline coordinates use one atom per line:

```ini
[input]
system=
   O   0.000000000   0.000000000  -0.041061554
   H  -0.533194329   0.533194329  -0.614469223
   H   0.533194329  -0.533194329  -0.614469223
```

Each atom line must contain at least `symbol x y z`. Numeric atomic labels are
also accepted by existing examples. When `basis=library`, each atom line must
also include a tag column.

### `system2`

| Field | Value |
| --- | --- |
| Type | string or multiline coordinate block |
| Default | empty |
| Values | second XYZ file path, or second inline geometry |
| Used by | NACME and previous-geometry workflows |

Provides a second geometry. NACME uses it as the displaced or previous-step
geometry when `[guess] file2` is not supplied.

### `charge`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | electron count for all workflows |

Sets the total molecular charge. Keep `charge`, `[scf] multiplicity`, and the
chosen reference type physically consistent.

### `method`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `hf` |
| Values | `hf`, `tdhf` |
| Used by | workflow dispatch |

Selects the electronic-structure driver. Use `method=hf` for HF and DFT
reference calculations. Use `method=tdhf` for TDHF, TDDFT, SF-TDDFT,
MRSF-TDDFT, SOC, NACME, and MRSF-EKT workflows.

DFT calculations still use `method=hf`; the functional is selected separately
with `functional`.

### `functional`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | DFT and TDDFT-style calculations |

Selects a density functional. An empty value means Hartree-Fock. Examples use
values such as `bhhlyp`, `pbe0`, and DTCAM-series functionals where supported.

Some property implementations have functional restrictions. For example, NMR
shielding does not support range-separated or meta-GGA functionals in the
current checker.

### `basis`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `6-31g*` |
| Values | basis name, semicolon-separated per-atom names, or `library` |
| Used by | AO basis setup |

Sets the orbital basis. A single basis name applies to every atom:

```ini
basis=6-31g*
```

Per-atom basis names can be supplied in atom order with semicolons:

```ini
basis=aug-cc-pVDZ-PP;aug-cc-pVDZ
```

For tagged basis assignment, set `basis=library`, add a tag after each atom, and
define the tag mapping with `library`.

### `library`

| Field | Value |
| --- | --- |
| Type | multiline string |
| Default | empty |
| Used by | tagged basis assignment when `basis=library` |

Maps atom tags to basis names:

```ini
[input]
system=
 C    1.6062782722   1.5141391221  -1.8538091464  c1
 H    0.7846511041   1.8564598303  -1.2260835006  h1
basis=library
library=
 c1 6-31g
 h1 6-31g*
```

When `basis=library`, every atom line must include a tag and every tag must have
a mapping.

### `runtype`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `energy` |
| Values | `energy`, `grad`, `hess`, `nac`, `nacme`, `bp`, `optimize`, `meci`, `mecp`, `tci`, `mep`, `ts`, `irc`, `neb`, `prop`, `data`, `ekt`, `soc` |
| Used by | top-level workflow dispatch |

Selects the calculation workflow.

Common values:

| Value | Meaning |
| --- | --- |
| `energy` | Single-point energy and requested properties. |
| `grad` | Energy plus gradient. |
| `hess` | Hessian and frequency workflow. |
| `nacme` | Nonadiabatic coupling matrix element workflow. |
| `soc` | Spin-orbit coupling workflow. |
| `ekt` | MRSF-EKT ionization/electron-affinity workflow. |
| `optimize` | Geometry optimization. |
| `meci`, `mecp`, `tci` | Crossing-point searches. |
| `ts`, `irc`, `neb`, `mep` | Reaction-path workflows. |
| `prop`, `data` | Multi-state property/data workflows for downstream drivers. |

`md` is recognized by validation code but is not implemented as a production
workflow in this repository.

### `ispher`

| Field | Value |
| --- | --- |
| Type | string mode |
| Default | `auto` |
| Values | `auto`, `true`, `false` |
| Used by | AO basis shell convention |

Controls pure spherical harmonic versus Cartesian AO shells.

| Value | Meaning |
| --- | --- |
| `auto` | Follow basis-set metadata where possible. |
| `true` | Force pure spherical shells, such as 5d and 7f. |
| `false` | Force Cartesian shells, such as 6d and 10f. |

Use this explicitly when reproducing a calculation from another program or when
a workflow is validated for one convention.

### `d4`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | DFT-D4 dispersion correction |

Enables the DFT-D4 dispersion correction where supported. The input checker
requires a DFT functional when `d4=true`.

### `soc_2e`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Values | `0`, `1` |
| Used by | `runtype=soc` |

Controls whether mean-field two-electron SOC terms are included.

| Value | Meaning |
| --- | --- |
| `0` | One-electron SOC terms only. |
| `1` | One-electron plus mean-field two-electron SOC terms. |

The option lives in `[input]` because it gates the whole SOC workflow rather
than a response-solver detail.

Spin-orbit coupling is a relativistic interaction that mixes spin-free states of
different spin character. OpenQP's documented SOC workflow is an MRSF-TDDFT
workflow selected with `runtype=soc`; `soc_2e=1` adds the mean-field
two-electron SOC contribution used in practical molecular SOC calculations.
Scalar relativistic DKH correction is a separate spin-free Hamiltonian option
controlled by `[scf] scal_rel`. See
[References](../references.md#spin-orbit-coupling) for OpenQP's relativistic
MRSF-TDDFT SOC method and mean-field SOC operator background.

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("soc_keywords")
job.molecule(geometry="water", charge=0)
job.theory.mrsf(functional="bhhlyp", basis="6-31G(2df,p)", nstate=12)
job.workflow.soc(soc_2e=1, scal_rel=2)
```

For Python SOC workflows, `job.workflow.soc(...)` sets `[scf] scal_rel=2` by
default. Override it with `scal_rel=0`, `1`, or `2` when needed.

### `omp_threads`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | OpenMP runtime setup |

Sets OpenMP threads per process or MPI rank. `0` means leave the environment or
compiled default unchanged.

Precedence is:

1. command-line `--omp`
2. `[input] omp_threads`
3. `OMP_NUM_THREADS`
4. OpenQP built-in default

Example:

```ini
[input]
omp_threads=16
```

### `perf`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | unset (legacy behaviour) |
| Values | `0`, `1`, `2`, `3` |
| Used by | the performance preset (see [Performance](../performance.md)) |

Opt-in performance preset that bundles the performance input keys into one
accuracy↔speed dial: `0` strict reference, `1` recommended production (exact),
`2` faster (tiny degradation), `3` aggressive (small degradation allowed).
Explicit performance input keys override the preset. Unset = unchanged default.
