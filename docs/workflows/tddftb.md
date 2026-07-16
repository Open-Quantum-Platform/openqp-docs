# TD-DFTB

Conventional (spin-conserving) **TD-DFTB** is the DFTB analogue of linear-response
TDDFT. It is requested with [`[input] method=dftb`](../keywords/input.md#method),
a [`[tdhf] type`](../keywords/tdhf.md#type) of `rpa` or `tda`, and
[`[dftb] type=tddftb`](../keywords/dftb.md#type) (or `type=auto`, which resolves
to the same). Excited-state energies, analytic gradients, and geometry
optimizations are supported.

!!! warning "Development preview"
    The DFTB method (OpenQP-DFTB library) and the one-line `.oqp` format are
    development-branch features, not part of OpenQP 1.2.0. See the
    [`[dftb]` reference](../keywords/dftb.md) and
    [One-line `.oqp`](../oqp-input.md).

!!! note "RPA and TDA are identical for DFTB"
    The DFTB response does not distinguish full-response (RPA) from
    Tamm–Dancoff (TDA): `[tdhf] type=rpa` and `type=tda` map to the same
    tight-binding response. The Python builder always emits `type=tda` for
    `response_type="tddftb"`; add `job.settings.tdhf(type="rpa")` only if you
    want the literal `rpa` keyword in the generated file.

**State labels.** `S0` is the SCF ground state (**state 0**). Excited singlets
are `S1`, `S2`, … = response roots `1`, `2`, … (`grad`/`istate` count from `1`
for the excited states). Triplet response states are `T0`, `T1`, … in the
one-line form. As with all DFTB families, `basis=` is an ignored placeholder,
`functional=` is empty, and the `.oqp` route carries neither.

## Energy (excitation energies)

Three singlet roots (`S1`–`S3`) above the DFTB ground state:

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

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb
parameter_path=/path/to/params.opdftb
```

**`.oqp`** (route `tddftb(nstate=N)`; `tda-tddftb(nstate=N)` for TDA)

```text
tddftb(nstate=3) geom="h2o.xyz" energy dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="tddftb", nstate=3, parameter_path="params.opdftb")
job.workflow.energy()
job.run()
```

## Gradient

Gradient of the first excited singlet `S1` (response root 1 → `grad=1`):

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

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb
parameter_path=/path/to/params.opdftb

[properties]
grad=1
```

**`.oqp`**

```text
tddftb(nstate=3) geom="h2o.xyz" grad(S1) dftb(parameter_path="params.opdftb")
```

For a triplet-root gradient use the physical triplet label — `grad(T0)` is the
first triplet response state (`tda-tddftb` shown, but `tddftb` behaves the same):

```text
tda-tddftb(nstate=3) geom="h2o.xyz" grad(T0) dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb_grad")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="tddftb", nstate=3, parameter_path="params.opdftb")
job.workflow.gradient(state=1)
job.run()
```

## Geometry optimization

Optimize the `S1` excited-state minimum (`istate=1`):

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

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb
parameter_path=/path/to/params.opdftb

[optimize]
lib=oqp
istate=1
maxit=100
```

**`.oqp`**

```text
tddftb(nstate=3) geom="h2o.xyz" opt(S1) dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb_opt")
job.molecule("h2o.xyz", charge=0)
job.dftb(response_type="tddftb", nstate=3, parameter_path="params.opdftb")
job.workflow.optimize(istate=1, maxit=100)
job.run()
```

## MECI

A minimum-energy conical intersection between two excited singlets of the same
multiplicity — here `S1`/`S2` (`istate=1`, `jstate=2`) — using the penalty
optimizer:

**`.inp`**

```ini
[input]
method=dftb
runtype=meci
charge=0
basis=sto-3g
functional=
system=guess.xyz

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb
parameter_path=/path/to/params.opdftb

[optimize]
lib=oqp
istate=1
jstate=2
meci_search=penalty
pen_sigma=1.0
pen_incre=1.2
energy_gap=1.0e-4
```

**`.oqp`**

```text
tddftb(nstate=3) geom="guess.xyz" meci(S1,S2) dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="tddftb_meci")
job.molecule("guess.xyz", charge=0)
job.dftb(response_type="tddftb", nstate=3, parameter_path="params.opdftb")
job.workflow.meci(istate=1, jstate=2, meci_search="penalty", maxit=100)
job.run()
```

!!! warning "Use MRSF-TDDFTB for S₀/S₁ intersections"
    The optimizer will mechanically accept `meci(S0,S1)` for conventional
    TD-DFTB, but linear-response TDDFT/TD-DFTB has the wrong branching-space
    dimensionality at a crossing with the reference (ground) state — the
    intersection topology is incorrect. Restrict conventional TD-DFTB MECI to
    two *excited* states of the same multiplicity, and use
    [MRSF-TDDFTB](mrsf-tddftb.md#conical-intersections-meci) for S₀/S₁ conical
    intersections, where the topology is correct. `meci` is same-multiplicity
    only; different-multiplicity crossings (`mecp`) are not available for the
    DFTB method.
