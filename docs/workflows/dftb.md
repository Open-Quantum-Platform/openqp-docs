# DFTB (ground state)

Ground-state **density-functional tight binding** is a first-class OpenQP
method, selected with [`[input] method=dftb`](../keywords/input.md#method). It
comes in two families:

- **DFTB2** — the self-consistent-charge model (`[dftb] type=ground`). This is
  the default ground-state DFTB.
- **DFTB0** — the non-self-consistent model (`[dftb] type=dftb0`), useful as a
  fast zeroth-order reference.

Both deliver single-point **energies**, analytic **gradients**, and **geometry
optimization** at tight-binding cost. Excited states are covered by the
[TD-DFTB](tddftb.md) and [MRSF-TDDFTB](mrsf-tddftb.md) manuals; all `[dftb]`
keywords are documented in the [`[dftb]` reference](../keywords/dftb.md).

!!! warning "Development preview"
    The DFTB method is provided by the optional **OpenQP-DFTB** library and is
    not part of OpenQP 1.2.0; the one-line `.oqp` format is likewise a
    development-branch input style (see [One-line `.oqp`](../oqp-input.md)).
    Install and build details are in the [`[dftb]`
    reference](../keywords/dftb.md).

Every example below is shown in all three input formats. Two DFTB conventions
apply throughout:

- `basis=` is a **required-but-ignored placeholder** (the Slater–Koster minimal
  basis is always used); `functional=` must be **empty**. The one-line `.oqp`
  route carries neither.
- The ground state is **state 0** (`grad`/`istate` count from `0`).

## Energy

DFTB2 single-point energy:

**`.inp`**

```ini
[input]
method=dftb
runtype=energy
charge=0
basis=sto-3g
functional=
system=
  O  0.000000  0.000000  0.000000
  H  0.000000  0.757160  0.586260
  H  0.000000 -0.757160  0.586260

[dftb]
backend=native
type=ground
parameter_path=/path/to/params.opdftb
```

**`.oqp`** (route `dftb`; the geometry file sits beside the `.oqp` file)

```text
dftb geom="h2o.xyz" energy dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="ground", parameter_path="params.opdftb")
job.workflow.energy()
job.run()
```

## Gradient

Add `[properties] grad=0` (the ground state is state 0):

**`.inp`**

```ini
[input]
method=dftb
runtype=grad
charge=0
basis=sto-3g
functional=
system=
  O  0.000000  0.000000  0.000000
  H  0.000000  0.757160  0.586260
  H  0.000000 -0.757160  0.586260

[dftb]
backend=native
type=ground
parameter_path=/path/to/params.opdftb

[properties]
grad=0
```

**`.oqp`**

```text
dftb geom="h2o.xyz" grad dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb_grad")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="ground", parameter_path="params.opdftb")
job.workflow.gradient(state=0)
job.run()
```

## Geometry optimization

`runtype=optimize` with the native optimizer (`[optimize] lib=oqp`) on the
ground state (`istate=0`):

**`.inp`**

```ini
[input]
method=dftb
runtype=optimize
charge=0
basis=sto-3g
functional=
system=
  O  0.000000  0.000000  0.000000
  H  0.000000  0.757160  0.586260
  H  0.000000 -0.757160  0.586260

[dftb]
backend=native
type=ground
parameter_path=/path/to/params.opdftb

[optimize]
lib=oqp
istate=0
maxit=100
```

**`.oqp`**

```text
dftb geom="h2o.xyz" opt dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb_opt")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="ground", parameter_path="params.opdftb")
job.workflow.optimize(istate=0, maxit=100)
job.run()
```

!!! note "Ground state and the `[tdhf]` block"
    A hand-written ground-state deck needs no `[tdhf]` or `[scf]` section. The
    Python builder always emits an inert `[tdhf] type=tda` block even for
    `response_type="ground"`; it is ignored by the ground-state DFTB path.

## DFTB0 (non-SCC)

DFTB0 is the same ground-state method without charge self-consistency. Switch
`[dftb] type=ground` → `type=dftb0`, the `.oqp` route `dftb` → `dftb0`, and the
Python `response_type="ground"` → `"dftb0"`. Energy, gradient, and optimization
work identically (state 0 only):

**`.inp`**

```ini
[input]
method=dftb
runtype=energy
charge=0
basis=sto-3g
functional=
system=
  O  0.000000  0.000000  0.000000
  H  0.000000  0.757160  0.586260
  H  0.000000 -0.757160  0.586260

[dftb]
backend=native
type=dftb0
parameter_path=/path/to/params.opdftb
```

**`.oqp`** (aliases `dftb-noscc`, `dftb-nonscc` are also accepted)

```text
dftb0 geom="h2o.xyz" energy dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb0")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="dftb0", parameter_path="params.opdftb")
job.workflow.energy()
job.run()
```

`parameter_path` accepts either a single combined `.opdftb` file or a directory
of Slater–Koster `<El>-<El>.skf` files. There is no MECI task for a ground-state
method (it targets a single state); for conical intersections use
[MRSF-TDDFTB](mrsf-tddftb.md#conical-intersections-meci).
