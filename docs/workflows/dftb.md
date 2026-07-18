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

Every example below leads with the recommended `.oqp` form, followed by Python
and the legacy `.inp` form. Two DFTB conventions
apply throughout:

- `basis=` is a **required-but-ignored placeholder** (the Slater–Koster minimal
  basis is always used); `functional=` must be **empty**. The `.oqp`
  route carries neither.
- The ground state is **state 0** (`grad`/`istate` count from `0`).

## Energy

DFTB2 single-point energy:

**`.oqp`** (route `dftb`; the geometry file sits beside the `.oqp` file)

```text
dftb
energy
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb")
job.molecule("h2o.xyz")
job.dftb(response_type="ground")
job.workflow.energy()
job.run()
```

**Legacy `.inp`**

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
```

## Gradient

Add `[properties] grad=0` (the ground state is state 0):

**`.oqp`**

```text
dftb
grad
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb_grad")
job.molecule("h2o.xyz")
job.dftb(response_type="ground")
job.workflow.gradient(state=0)
job.run()
```

**Legacy `.inp`**

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

[properties]
grad=0
```

## Geometry optimization

`runtype=optimize` with the native optimizer (`[optimize] lib=oqp`) on the
ground state (`istate=0`):

**`.oqp`**

```text
dftb
opt
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb_opt")
job.molecule("h2o.xyz")
job.dftb(response_type="ground")
job.workflow.optimize(istate=0)
job.run()
```

**Legacy `.inp`**

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

[optimize]
lib=oqp
istate=0
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

**`.oqp`** (aliases `dftb-noscc`, `dftb-nonscc` are also accepted)

```text
dftb0
energy
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_dftb0")
job.molecule("h2o.xyz")
job.dftb(response_type="dftb0")
job.workflow.energy()
job.run()
```

**Legacy `.inp`**

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
```

`parameter_path` is optional. To override the bundled parameters, point it to
a combined `.opdftb` file or a directory of Slater–Koster `<El>-<El>.skf`
files. There is no MECI task for a ground-state
method (it targets a single state); for conical intersections use
[MRSF-TDDFTB](mrsf-tddftb.md#conical-intersections-meci).
