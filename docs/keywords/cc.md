# `[cc]`

!!! warning "Development preview"
    `[cc]` targets OpenQP PR
    [#302](https://github.com/Open-Quantum-Platform/openqp/pull/302) and is not
    part of OpenQP 1.2.0.

The `[cc]` section controls the frozen core and the coupled-cluster solver for
`[input] method=ccsd` and `[input] method=ccsd(t)`. The defaults are usable as
they stand; the section is only needed to freeze core orbitals or to change the
convergence behaviour.

Coupled cluster is a post-SCF energy workflow. It requires an HF reference, so
`[input] functional` must be empty and `[input] runtype` must be `energy`. In
concise input, select the reference with
`ccsd_t(reference=rhf|rohf|uhf)/BASIS`; the value lowers to `[scf] type` and is
not a keyword in this section.

## Minimal Examples

CCSD(T) in `.oqp`:

```text
ccsd_t/6-31g
energy
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_ccsd_t")
job.molecule(geometry="water")
job.theory.ccsd_t(basis="6-31g")
mol = job.run()
```

Legacy `.inp`:

```ini
[input]
method=ccsd(t)
runtype=energy
functional=
```

To freeze core orbitals, add an exact `.oqp` section call:

```text
ccsd_t/6-31g
energy
cc(nfzc=1)
geom="h2o.xyz"
```

The legacy section is:

```ini
[cc]
nfzc=1
```

## Keywords

### `nfzc`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | CCSD and CCSD(T) |

Number of lowest orbitals excluded from the correlation treatment. Must be
non-negative and smaller than the number of occupied orbitals; the module
aborts otherwise.

For an ROHF reference the core is removed before semicanonicalisation, so the
correlated space is the span of the reference orbitals that were kept. See the
[coupled-cluster workflow](../workflows/coupled-cluster.md#frozen-core).

### `conv`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1e-7` |
| Used by | CCSD and CCSD(T) |

Convergence threshold. The iteration stops when both the amplitude RMS change
and the change in the correlation energy fall below this value.

### `maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50` |
| Used by | CCSD and CCSD(T) |

Maximum number of CCSD iterations. A run that does not converge within this
many iterations aborts rather than reporting an unconverged energy.

### `ndiis`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `8` |
| Used by | CCSD and CCSD(T) |

DIIS subspace size for the amplitude iteration. Set `0` to disable DIIS; the
same tolerance then typically needs two to three times as many iterations.

## Notes

- `method=ccsd` and `method=ccsd(t)` accept `runtype=energy` only.
- Both reject non-empty `[input] functional` values.
- The reference is selected through `[scf] type`; RHF, UHF, and ROHF are
  supported. Open-shell references run through a spin-orbital solver whose
  storage grows as `(2*nmo)^4`, so keep those systems small.
- The integrals are held in memory on both paths. The module prints the
  storage it needs and refuses above 64 GB (closed shell) or 32 GB (open
  shell).

See the [coupled-cluster workflow](../workflows/coupled-cluster.md) for
complete input and Python examples.
