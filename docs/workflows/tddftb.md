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

**`.oqp`** (route `tddftb(nstate=N)`; `tda-tddftb(nstate=N)` for TDA)

```text
tddftb(nstate=3)
energy
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb")
job.molecule("h2o.xyz")
job.dftb(response_type="tddftb", nstate=3)
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

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb
```

## Gradient

Gradient of the first excited singlet `S1` (response root 1 → `grad=1`):

**`.oqp`**

```text
tddftb(nstate=3)
grad(S1)
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb_grad")
job.molecule("h2o.xyz")
job.dftb(response_type="tddftb", nstate=3)
job.workflow.gradient(state=1)
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

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb

[properties]
grad=1
```

Conventional TD-DFTB currently supports singlet targets. Use
[`sf-tddftb`](../oqp-input.md#route-and-model-reference) or
[`mrsf-tddftb`](mrsf-tddftb.md) for triplet-state calculations. The equivalent
TDA singlet gradient is:

```text
tda-tddftb(nstate=3)
grad(S1)
geom="h2o.xyz"
```

## Geometry optimization

Optimize the `S1` excited-state minimum (`istate=1`):

**`.oqp`**

```text
tddftb(nstate=3)
opt(S1)
geom="h2o.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb_opt")
job.molecule("h2o.xyz")
job.dftb(response_type="tddftb", nstate=3)
job.workflow.optimize(istate=1)
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

[tdhf]
type=rpa
nstate=3

[dftb]
backend=native
type=tddftb

[optimize]
lib=oqp
istate=1
```

## MECI

A minimum-energy conical intersection between two excited singlets of the same
multiplicity — here `S1`/`S2` (`istate=1`, `jstate=2`) — using the penalty
optimizer:

**`.oqp`**

```text
tddftb(nstate=3)
meci(S1,S2)
geom="guess.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="tddftb_meci")
job.molecule("guess.xyz")
job.dftb(response_type="tddftb", nstate=3)
job.workflow.meci(istate=1, jstate=2, meci_search="penalty")
job.run()
```

**Legacy `.inp`**

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

[optimize]
lib=oqp
istate=1
jstate=2
meci_search=penalty
pen_sigma=1.0
pen_incre=1.2
energy_gap=1.0e-4
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
