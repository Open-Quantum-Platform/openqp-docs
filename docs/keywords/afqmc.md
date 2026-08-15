# `[afqmc]`

!!! warning "Companion development build required"
    The `[afqmc]` section is provided by the
    [`openqp-afqmc` development branch](https://github.com/Open-Quantum-Platform/openqp-afqmc/pull/1),
    not by the OpenQP 1.2.0 package from PyPI.

The `[afqmc]` section controls phaseless auxiliary-field quantum Monte Carlo
calculations selected with `[input] method=afqmc`. OpenQP can use a mean-field
trial, read an SF/MRSF-CSF trial from a file, or build a trial directly from an
OpenQP MRSF Davidson root.

## Minimal examples

Mean-field trial in concise `.oqp` input:

```text
afqmc/sto-3g
energy
afqmc(walkers=64,steps=200,dt=0.005)
geom="h2.xyz"
```

An in-memory MRSF singlet root with selected CSF channels:

```text
mrsf(nstate=3)/bhhlyp/cc-pvdz
energy
afqmc(
  trial=mrsf_state,
  state=2,
  channels="oo+ov",
  nvirtual=2,
  walkers=256,
  steps=2000
)
geom="butadiene.xyz"
```

Here `state=2` is the second one-based OpenQP MRSF root, physically `S1` in the
singlet manifold. The concise aliases `channels`, `ncore`, and `nvirtual` lower
to the legacy keywords `csf_channels`, `csf_ncore`, and `csf_nvirtual`.

The corresponding legacy section is:

```ini
[afqmc]
trial=mrsf_state
state=2
csf_channels=oo+ov
csf_ncore=-1
csf_nvirtual=2
nwalkers=256
nsteps=2000
timestep=0.005
```

## Trial selection

### `trial`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `mean_field` |
| Values | `mean_field`, `sf`, `mrsf`, `mrsf_state` |

Selects the trial source. `mean_field` uses the converged SCF determinant.
`sf` and `mrsf` read a trial from `trial_file`. `mrsf_state` first runs the
native OpenQP MRSF Davidson solver and consumes the selected root directly in
CSF space. The current in-memory `mrsf_state` path supports singlet MRSF roots;
other target multiplicities are rejected rather than silently reinterpreted.

### `trial_file`

| Field | Value |
| --- | --- |
| Type | path string |
| Default | empty |
| Used by | `trial=sf`, `trial=mrsf` |

Path to the external trial representation.

This is a legacy raw Slater-component interface. The first record contains
three integers,

```text
NCOMP  NALPHA  NBETA
```

and each of the following `NCOMP` records contains

```text
REAL(C)  IMAG(C)  A1 ... A_NALPHA  B1 ... B_NBETA
```

Orbital indices are one-based canonical-MO indices. Alpha occupations precede
beta occupations, and their column order fixes the component phase. OpenQP
normalizes the complete coefficient vector after reading it. Duplicate or
out-of-range occupations are rejected.

For example, the following two-component file represents one linked open-shell
singlet CSF in a two-orbital, one-alpha/one-beta space:

```text
2 1 1
0.7071067811865475 0.0  1  2
0.7071067811865475 0.0  2  1
```

For `trial=mrsf`, every paired CSF must already appear as its complete linked
set of components with the intended relative phase. The file reader does not
infer or repair a missing partner. Prefer `trial=mrsf_state` when the trial is
an OpenQP MRSF root, because that path starts from the native CSF coefficients
and materializes the partners consistently.

### `state`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | `trial=mrsf_state` |

One-based OpenQP Davidson root used for the trial. For singlet MRSF, root 1 is
physical `S0`, root 2 is `S1`, and so on.

### `trial_threshold`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-8` |
| Used by | MRSF-CSF trials |

Drops a whole CSF when `|X_I|` is at or below the threshold. Thresholding and
normalization occur before the fixed Slater components are materialized, so
the linked components of one CSF cannot be selected independently. The value
must be nonnegative.

## MRSF CSF space

The MRSF orbitals are partitioned into `C`, `O`, and `V`: doubly occupied
closed orbitals, the two singly occupied open-shell orbitals, and virtual
orbitals. The source/destination pair gives four selectable channels.

### `csf_channels`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `oo` |
| Values | any nonempty combination of `oo`, `co`, `ov`, `cv`; or `all` |

Selects the MRSF CSF channels used in the trial. Separate names with `+`, a
comma, or whitespace. Examples include `oo`, `oo+ov`, `oo+co+ov`, and `all`.

`OO` is the small default. `OV` is commonly the first enlargement to test.
`CV` is optional; its present two-component MRSF representation can retain a
known residual spin contamination, which OpenQP reports through the trial
`<S^2>` diagnostic.

### `csf_ncore`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `-1` |
| Used by | `CO` and `CV` channels |

Number of `C` orbitals retained, selected from the highest-energy end nearest
the open-shell pair. `-1` uses every available `C` orbital; `0` uses none.

### `csf_nvirtual`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `-1` |
| Used by | `OV` and `CV` channels |

Number of `V` orbitals retained, selected from the lowest-energy end nearest
the open-shell pair. `-1` uses every available `V` orbital; `0` uses none.

## Propagation and estimator controls

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `chol_tol` | float | `1.0e-10` | Modified-Cholesky residual threshold. |
| `nwalkers` | integer | `640` | Walker population. |
| `nsteps` | integer | `1000` | Number of imaginary-time steps. |
| `timestep` | float | `0.005` | Imaginary-time step in inverse Hartree. |
| `seed` | integer | `1` | Random-number seed. |
| `stabilize_every` | integer | `5` | Walker orbital reorthogonalization interval. |
| `population_control_every` | integer | `5` | Population-control interval. |
| `estimate_every` | integer | `25` | Estimator reporting interval. |
| `accumulate_after` | integer | `100` | First step included in block averages. |
| `force_bias_bound` | float | `1.0` | Force-bias clipping bound. |

OpenQP reports both mixed and hybrid estimators. The block-averaged mixed
estimator is the AFQMC energy returned by the calculation.

## State-specific controls

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `oo_orbitals` | boolean | `False` | Read a state-specific orbital rotation. |
| `oo_file` | path string | empty | Orbital file required by `oo_orbitals=True`. |
| `nlow` | integer | `0` | Number of lower-state constraints. |
| `low_file` | path string | empty | Lower-state data file required when `nlow>0`. |
| `low_max` | float | `0.0` | Lower-state overlap threshold. |
| `low_cap` | float | `10.0` | Cap applied by lower-state control. |
| `low_start` | integer | `0` | Step at which lower-state control begins. |

### `oo_file` format

The first record is `NMO NSPIN_BLOCKS`, where `NSPIN_BLOCKS` is either `1` for
one shared spatial rotation or `2` for separate alpha and beta rotations. It is
followed by `NMO*NMO` complex matrix elements per spin block, one
`REAL(C_PQ) IMAG(C_PQ)` pair per record, with row index `P` varying fastest
inside each column `Q`. The matrix rotates the canonical MO basis and must be
unitary to within `1e-7`.

A two-orbital identity rotation shared by both spins is:

```text
2 1
1.0 0.0
0.0 0.0
0.0 0.0
1.0 0.0
```

### `low_file` format

The first record is `NLOW NCOMP`; both values must match the current AFQMC
input and trial expansion. Each of the next `NLOW` records contains `2*NCOMP`
numbers, written as real/imaginary pairs for every coefficient in exactly the
same component order as the target trial. OpenQP orthonormalizes the supplied
lower-state span before projecting it from the target coefficients.

For one lower state in a two-component trial:

```text
1 2
1.0 0.0  0.0 0.0
```

These file controls are advanced interfaces. They do not by themselves prove
excited-state orthogonality during stochastic propagation; convergence and
state-collapse diagnostics remain required.

See the [AFQMC workflow](../workflows/afqmc.md) for method details, CSF
materialization, exact H2 validation, and production convergence checks.
