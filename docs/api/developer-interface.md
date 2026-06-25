# Developer Interface

The C/Fortran interface is OpenQP's native bridge. It is exposed through
`include/oqp.h` and is used by the Python package through CFFI. This layer is
useful for OpenQP developers and native extension authors, but it is not the
recommended API for ordinary user scripts.

!!! warning "Internal interface"
    The native handle layer can change when OpenQP data structures or kernels
    change. Use `oqp.pyoqp.Runner` for stable Python automation.

## Handle Model

The central object is `oqp_handle_t`. It stores pointers to molecular data,
runtime controls, DFT and TDDFT parameters, MPI metadata, shell data, and result
records.

```c
typedef struct oqp_handle_t {
    void *inf;
    xyz_t *xyz;
    double *qn;
    double *mass;
    xyz_t *grad;
    struct molecule *mol_prop;
    struct energy_results *mol_energy;
    struct dft_parameters *dft;
    struct tddft_parameters *tddft;
    struct control_parameters *control;
    struct mpi_communicator *mpiinfo;
    struct electron_shell *elshell;
    struct trah_control *trah;
} oqp_handle_t;
```

The handle is shared across C, Fortran, and Python. The Python `Molecule` object
owns an OpenQP data wrapper that points into this handle and provides higher
level accessors.

## Lifecycle

| Function | Purpose |
| --- | --- |
| `oqp_init()` | Allocate and initialize an OpenQP handle. |
| `oqp_clean(handle)` | Release handle-owned native resources. |
| `oqp_set_atoms(handle, natoms, x, y, z, q, mass)` | Set atom coordinates, charges, and optional masses. |
| `oqp_get(handle, code, type_id, ndims, dims, value)` | Retrieve registered tag data by code. |
| `oqp_alloc(handle, code, type_id, ndims, dims, value)` | Allocate registered tag data. |
| `oqp_del(handle, code)` | Delete registered tag data. |
| `oqp_get_nbf(handle)` | Return the number of basis functions. |
| `oqp_get_basis(handle, ...)` | Retrieve basis metadata arrays. |

At this level, callers must manage pointer validity, array dimensions, and
lifetime explicitly.

## Kernel Families

`include/oqp.h` exposes native procedures for the main kernel families:

| Family | Examples |
| --- | --- |
| Basis and shells | `apply_basis`, `append_shell`, `append_ecp` |
| Integrals | `int1e`, `int2e` |
| Initial guesses | `guess_hcore`, `guess_huckel`, `guess_modhuckel`, `guess_json`, `guess_sap`, `guess_minao` |
| HF/DFT | `hf_energy`, `hf_gradient`, `hf_hessian` |
| TDHF/SF/MRSF | `tdhf_energy`, `tdhf_gradient`, `tdhf_sf_energy`, `tdhf_mrsf_energy`, `tdhf_mrsf_gradient` |
| MRSF-EKT | `tdhf_mrsf_ekt_ip`, `tdhf_mrsf_ekt_ea` |
| Properties | `electric_moments`, `mulliken`, `lowdin`, `nmr_shielding` |
| Spin-orbit coupling | `soc_mrsf` |

Python wraps callable native functions automatically during `import oqp`. Most
native functions become Python callables that accept a `Molecule` object and pass
its underlying handle to the compiled function.

## Python CFFI Bridge

The installed `oqp` package resolves the native runtime, reads `include/oqp.h`,
loads `liboqp`, and exposes native functions through CFFI. A typical internal
call path is:

1. `Runner` creates a `Molecule`.
2. `Molecule` allocates the native OpenQP data handle.
3. The input parser applies schema defaults and user options.
4. `Runner.run()` dispatches to the Python workflow function for the selected
   `[input] runtype`.
5. The workflow function calls native kernels through the wrapped `oqp`
   functions.
6. Results are stored back on the handle and exposed through `Molecule` getters.

This design lets Python control workflow orchestration while Fortran and native
libraries handle the expensive electronic-structure kernels.

## Extension Guidance

- Add user-facing input first to the schema and keyword documentation.
- Validate new input combinations in the input checker before dispatch.
- Store reusable arrays as registered OpenQP data tags when they need to cross
  Python/native boundaries.
- Prefer adding a Python workflow wrapper before exposing low-level native
  procedures directly to users.
- Update this API chapter when a new user-facing entry point becomes stable.
