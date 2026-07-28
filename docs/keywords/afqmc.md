# `[afqmc]`

The `[afqmc]` section controls Hamiltonian export and auxiliary-field quantum
Monte Carlo propagation through the optional OpenQP–AFQMC integration. OpenQP
provides the geometry, SCF reference, molecular orbitals, and integrals; the
installed `openqp-afqmc` command prepares the interchange files and starts the
native OpenMP AFQMC executable.

Concise `.oqp` input uses `afqmc(...)`:

```text
rohf/sto-3g geom="ch2.xyz" charge=0 mult=3 energy guess(type=huckel)
afqmc(output=ch2_afqmc,trial=mean_field,walkers=16,steps=20,dt=0.005,seed=161803,threads=2,chol=1e-10,accumulate_after=5)
```

The concise aliases `output`, `walkers`, `steps`, `dt`, `threads`, and `chol`
map to the corresponding long-form keyword names below. Unknown and duplicate
options are rejected.

## Keywords

| Keyword | `.oqp` alias | Type | Default | Meaning |
| --- | --- | --- | --- | --- |
| `output_dir` | `output` | string | input stem plus `_afqmc` | Prepared calculation directory. |
| `chol_tol` | `chol` | float | `1.0e-10` | Eigenvalue cutoff for the ERI Cholesky factorization. |
| `trial` | — | string | `mean_field` | Trial type: `mean_field`, `mrsf`, `sf`, or `none`. |
| `trial_file` | — | path | empty | External CI determinant expansion required by `mrsf` and `sf`. |
| `nwalkers` | `walkers` | integer | `640` | Walker population. |
| `nsteps` | `steps` | integer | `1000` | Imaginary-time propagation steps. |
| `timestep` | `dt` | float | `0.005` | Imaginary-time step in Hartree inverse. |
| `seed` | — | integer | `1` | Reproducible random-number seed. |
| `omp_threads` | `threads` | integer | `1` | OpenMP threads used by the native runner. |
| `stabilize_every` | — | integer | `5` | Walker orthonormalization interval. |
| `population_control_every` | — | integer | `5` | Population-control interval. |
| `estimate_every` | — | integer | `25` | Energy-estimator sampling interval. |
| `accumulate_after` | — | integer | `100` | Equilibration steps discarded before accumulation; smaller than `nsteps`. |
| `force_bias_bound` | — | float | `1.0` | Component-wise force-bias bound. |

## Python API

The schema exposes this section through the compact Python API:

```python
from oqp.openqp import OpenQP

job = OpenQP("ch2_afqmc")
job.molecule("ch2.xyz", basis="sto-3g", charge=0, multiplicity=3)
job.theory("hf", reference="rohf")
job.settings.afqmc(
    output_dir="ch2_afqmc",
    trial="mean_field",
    nwalkers=640,
    nsteps=1000,
    timestep=0.005,
    omp_threads=4,
)
```

The installed command remains the execution entry point for the complete
OpenQP-to-AFQMC workflow. See [Auxiliary-Field Quantum Monte
Carlo](../workflows/afqmc.md).
