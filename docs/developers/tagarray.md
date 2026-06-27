# Data Tags and Tagarray

OpenQP uses a tagarray container to move arrays and scalar records across
Fortran, C, and Python. It is the shared storage for matrices, orbital data,
response vectors, SOC arrays, Hessians, and other intermediate or result data
that must survive across language boundaries.

## Naming

Tag names use the `OQP::` prefix. Fortran code usually imports named constants
from `source/tagarray_driver.F90`, such as:

| Tag | Typical content |
| --- | --- |
| `OQP::DM_A`, `OQP::DM_B` | Alpha and beta density matrices. |
| `OQP::FOCK_A`, `OQP::FOCK_B` | Alpha and beta Fock matrices. |
| `OQP::E_MO_A`, `OQP::E_MO_B` | Molecular-orbital energies. |
| `OQP::VEC_MO_A`, `OQP::VEC_MO_B` | Molecular-orbital coefficient matrices. |
| `OQP::Hcore`, `OQP::SM`, `OQP::TM` | Core Hamiltonian, overlap, and kinetic-energy matrices. |
| `OQP::td_energies`, `OQP::td_bvec_mo` | TDHF/TDDFT/MRSF response data. |
| `OQP::soc_eval`, `OQP::soc_hsoc_re`, `OQP::soc_hsoc_im` | SOC eigenvalues and Hamiltonian components. |
| `OQP::hf_hessian` | Native analytical HF/DFT Hessian matrix. |

## Fortran Pattern

Fortran modules normally reserve data before writing and then recover a typed
pointer with `tagarray_get_data`:

```fortran
use oqp_tagarray_driver, only: OQP_hf_hessian, TA_TYPE_REAL64, tagarray_get_data

call infos%dat%reserve_data(OQP_hf_hessian, TA_TYPE_REAL64, &
                            ncart*ncart, (/ ncart, ncart /))
call tagarray_get_data(infos%dat, OQP_hf_hessian, hess_store)
```

Use `data_has_tags(...)` when a kernel depends on records produced by an earlier
stage. Use the typed constants and comments in `tagarray_driver.F90` instead of
hard-coded strings when adding stable records.

## C Bridge

The native C interface exposes generic tag access through:

| Function | Purpose |
| --- | --- |
| `oqp_get(handle, code, type_id, ndims, dims, value)` | Return a pointer, type, dimensions, and data length for an existing tag. |
| `oqp_alloc(handle, code, type_id, ndims, dims, value)` | Allocate storage for a tag and return a writable pointer. |
| `oqp_del(handle, code)` | Delete a tag record. |

These are low-level functions. Callers must respect the returned type and
dimensions.

## Python Access

Python accesses tagarray records through `Molecule.data`:

```python
td_energies = mol.data["OQP::td_energies"]
soc_eval = mol.data["OQP::soc_eval"]
```

`Molecule` also creates convenience getters for common tags. For example,
`OQP::DM_A` becomes `mol.get_dm_a()`, and `OQP::td_energies` becomes
`mol.get_td_energies()`.

## Contributor Checklist

When adding a new shared data record:

1. Add a stable `OQP::...` constant and comment in `source/tagarray_driver.F90`.
2. Reserve the tag with the correct `TA_TYPE_*`, total data length, and shape.
3. Retrieve it with the matching typed pointer rank.
4. Add it to Python result handling only if users or workflows need it.
5. Add tests that check the tag is populated with the expected shape and data
   type.
6. Document user-facing result tags in [Results and Molecule Data](../api/results.md).
