# Installation

## Recommended Install

Use the Python package when possible:

```bash
pip install openqp
```

For a local source checkout:

```bash
git clone https://github.com/Open-Quantum-Platform/openqp.git
cd openqp
pip install .
```

The top-level package build installs the Python package, native library, header
files, and data files together. Normal command-line use does not require
`OPENQP_ROOT` after installation.

## Requirements

- Python 3.9 or newer
- GCC, G++, and Gfortran on Linux and macOS; Intel oneAPI (`ifx`, `icx`) on
  Windows, which has no GNU Fortran toolchain
- CMake 3.25 or newer
- BLAS/LAPACK
- `cffi`, NumPy, and SciPy
- Ninja, recommended for source builds
- OpenMPI or another MPI implementation, only when building with MPI

geomeTRIC is optional. Concise `.oqp` geometry drivers use the native OpenQP
optimizer and do not require it. Install the extra only for traditional `.inp`
or Python workflows that explicitly select the legacy geomeTRIC backend, such
as advanced constraint types beyond native frozen distances:

```bash
pip install "openqp[geometric]"
```

OpenQP 1.3.0 provides the optional `geometric` extra introduced by
[OpenQP #273](https://github.com/Open-Quantum-Platform/openqp/pull/273).
Plain `pip install openqp` does not install this compatibility backend.

See the [Build Options](build-options.md) reference for the full CMake option
table, defaults, BLAS/LAPACK choices, external dependency cache behavior, and
package-build overrides.

## Windows

`pip install openqp` works the same as elsewhere:

```bat
pip install openqp
```

pip installs Intel MKL alongside the wheel, so nothing else is needed. The
wheels are built with Intel oneAPI (`ifx`/`icx`) against MKL ILP64, and are
published for CPython 3.9 through 3.14.

MKL is linked but deliberately not carried inside the wheel: a single MKL
library exceeds PyPI's per-file size limit, so it is declared as a runtime
dependency instead. This is why installation pulls in `mkl` and
`intel-openmp`, and why the `mkl` requirement is pinned to the oneAPI series
the wheels are compiled against.

### Building from source on Windows

A source build needs the Intel oneAPI compilers; the GNU toolchain used on
Linux and macOS has no Windows equivalent here. Load the oneAPI environment
first (`setvars.bat`), then:

```bat
pip install . --config-settings=cmake.define.LINALG_LIB=Intel10_64ilp
```

Three configurations are rejected during CMake configuration rather than
failing later:

- **Static builds** (`-DBUILD_SHARED_LIBS=OFF`). The bundled DFT-D4 sources
  export their API with `DLLEXPORT`, which a static link cannot satisfy, and
  static library discovery here looks for Unix `.a` names. Windows is built
  shared.
- **Multi-configuration generators** (Visual Studio). The DFT-D4 DLLs are
  resolved from the top of each subproject build directory, without a
  per-configuration subdirectory. Configure with `-G Ninja`.
- **`-DENABLE_DDX=ON`.** The ddX build models a single library artifact, while
  Windows needs the import library and the DLL modelled separately.

`LINALG_LIB=auto` resolves to MKL ILP64 on Windows. OpenQP is ILP64-only — one
8-byte integer model everywhere — so a build that cannot obtain an ILP64
interface fails rather than silently linking a 4-byte one.

## Source Build

The default source install is:

```bash
pip install .
```

For development builds where you want to inspect the native build directory:

```bash
cmake -B build -G Ninja \
  -DCMAKE_C_COMPILER=gcc \
  -DCMAKE_CXX_COMPILER=g++ \
  -DCMAKE_Fortran_COMPILER=gfortran \
  -DCMAKE_INSTALL_PREFIX=. \
  -DENABLE_OPENMP=ON
ninja -C build install
cd pyoqp
pip install .
```

On macOS, prefer Homebrew GCC and the native Accelerate BLAS/LAPACK stack:

```bash
cmake -B build -G Ninja \
  -DCMAKE_C_COMPILER=/opt/homebrew/bin/gcc-15 \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/bin/g++-15 \
  -DCMAKE_Fortran_COMPILER=/opt/homebrew/bin/gfortran-15 \
  -DCMAKE_INSTALL_PREFIX=. \
  -DENABLE_OPENMP=ON \
  -DLINALG_LIB=auto \
  -DLINALG_LIB_INT64=OFF
ninja -C build install
cd pyoqp
pip install .
```

Adjust the compiler suffix to match the Homebrew GCC version installed on the
machine.

## Common CMake Options

| Option | Default | Meaning |
| --- | --- | --- |
| `-DENABLE_MPI=ON` | `OFF` | Enable MPI support. Use an MPI Fortran compiler wrapper such as `mpif90`. |
| `-DENABLE_OPENMP=ON` | `OFF` in CMake, `ON` for Python package builds | Enable OpenMP parallel sections. |
| `-DUSE_LIBINT=ON` | `ON` in CMake, `OFF` for Python package builds | Use Libint for ERIs instead of the native Rys path. |
| `-DLINALG_LIB=<vendor>` | `auto` | Select BLAS/LAPACK provider. |
| `-DLINALG_LIB_INT64=ON` | `ON` | Use ILP64 BLAS/LAPACK. |
| `-DENABLE_OPENTRAH=OFF` | `ON` in CMake, `OFF` for Python package builds | Skip the external OpenTrustRegion library and use native TRAH. |
| `-DOQP_REUSE_EXTERNALS=OFF` | `ON` | Disable reusable bundled-external build caches. |

For the complete list, including `ENABLE_DDX`, `BUILD_SHARED_LIBS`,
`ENABLE_PYTHON`, sanitizer flags, and external dependency cache paths, see
[Build Options](build-options.md).

ILP64 BLAS/LAPACK is the normal build mode. LP64
(`-DLINALG_LIB_INT64=OFF`) is supported only on macOS, mainly for a consistent
native Accelerate build.

## Runtime Files

Installed packages resolve runtime files package-locally first. Source-tree
development layouts are also detected when the native library has been installed
into the checkout. Keep `OPENQP_ROOT` only as a compatibility fallback for
custom layouts where Python and the OpenQP runtime tree are separated.

## OpenMP Threads

OpenQP accepts the OpenMP thread count from the command line:

```bash
openqp h2o.oqp --omp 16
```

or from a top-level option in `.oqp`:

```text
hf/6-31g* omp_threads=16
geom="h2o.xyz"
```

The legacy sectioned spelling is:

```ini
[input]
omp_threads=16
```

Precedence is `--omp`, then `input.omp_threads`, then `OMP_NUM_THREADS`, then
the built-in default.

## Test

```bash
openqp --run_tests all
```

This uses the default mixed regression set. Add `--input-format inp` or
`--input-format oqp` to select one syntax within that test scope, or
`--input-format both` to include both. See [Examples](examples/index.md) for the
standard `all` exclusions and explicit-directory policy.

For a smaller first check:

```bash
openqp examples/HF/H2O_RHF-HF_ENERGY.oqp
```
