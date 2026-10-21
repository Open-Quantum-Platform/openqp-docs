# Troubleshooting

## OpenQP Cannot Find Runtime Files

For normal installs, run:

```bash
pip install .
```

from the repository root, or install the package from PyPI. The installed
package should locate its native library and data files without `OPENQP_ROOT`.
Only set `OPENQP_ROOT` for custom layouts where Python is separated from the
OpenQP runtime tree.

## BLAS/LAPACK Integer ABI

OpenQP is ILP64-only: one 8-byte BLAS/LAPACK integer model on every platform.
LP64 support was removed, and `-DLINALG_LIB_INT64=OFF` now fails the configure
deliberately, so a stale CMake cache or an old script cannot produce a
mixed-width build. Clear the cache and drop the flag.

Use ILP64 OpenBLAS or MKL on Linux, MKL ILP64 on Windows, and Accelerate's
`$NEWLAPACK$ILP64` interface on macOS 13.3 or newer.

## SCF Does Not Converge

Try, in increasing order of intervention:

```ini
[scf]
diis_type=vdiis
```

```ini
[scf]
converger_type=soscf
```

```ini
[scf]
converger_type=trah
```

For difficult cases, use `alternative_scf=trah`, `escalation=soscf,trah`, MOM,
or pFON as appropriate. TRAH cannot be used with `mom=true` or `rstctmo=true`:
for those calculations use `diis` or `soscf`, and TRAH is left out of the
escalation ladder.

## Too Many Threads

Use either:

```bash
openqp input.inp --omp 16
```

or:

```ini
[input]
omp_threads=16
```

This controls OpenMP threads per process or MPI rank. MPI rank count remains
controlled by the launcher, for example `mpirun -np 4`.

## PCM Input Runs as Vacuum

PCM-enabled runs should fail clearly if the ddX runtime path is unavailable.
Use:

```ini
[pcm]
enabled=true
backend=ddx
mode=reference_scf
model=ddpcm
```

and keep the run type at `energy` for the current production PCM path.

## MP2 Stops at the Build Guard

The default `[mp2] transform=auto` selects a packed AO-to-MO transformation
when the direct pair-build count exceeds [`[mp2] max_jbuilds`](keywords/mp2.md#max_jbuilds). If the packed
transformation fails, the direct fallback is still subject to that guard.
Explicit `transform=direct` stops when the pair-build count exceeds the guard;
use `auto` or `n5` to select a packed transformation instead. Explicit `n5`
requires a packed form and stops if neither full nor occupied-virtual storage
can fit or allocate. Reduce the basis/problem size when packed storage is
unavailable; raise the direct-build guard only after checking runtime and
memory cost. See [MP2 transformation selection](keywords/mp2.md#transform).

## Documentation Looks Stale

The keyword reference should be checked against the OpenQP source schema:

- [`pyoqp/oqp/molecule/oqpdata.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/molecule/oqpdata.py)
- [`pyoqp/oqp/utils/input_checker.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/utils/input_checker.py)

If the code changes a default, allowed value, or runtime scope, update the
matching keyword and workflow page in the documentation repository before the
next release.
