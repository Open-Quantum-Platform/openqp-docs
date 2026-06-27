# Results and Molecule Data

After `runner.run()`, the `Runner` keeps the active calculation object at
`runner.mol`. This `Molecule` object stores the parsed configuration, native
OpenQP data handle, scalar results, and NumPy-accessible arrays.

```python
runner.run()

mol = runner.mol
print(mol.config["input"]["runtype"])
print(mol.get_scf_energy())
print(mol.get_system())
```

## Runner Summary

`runner.results()` returns a compact dictionary for Python-to-Python
communication:

| Key | Meaning |
| --- | --- |
| `atoms` | Atomic numbers. |
| `system` | Cartesian coordinates in Bohr. |
| `energy` | Energy array or scalar data accumulated by the workflow. |
| `grad` | Gradient data when available. |
| `dcm` | Derivative-coupling matrix data when available. |
| `nac` | Nonadiabatic coupling data when available. |
| `soc` | Spin-orbit coupling data when available. |
| `data` | Raw OpenQP data tags serialized into Python lists. |

For file-style result export, use `runner.mol.get_results()`. It returns a JSON
friendly dictionary with atoms, coordinates, total energy, symmetry metadata,
TDDFT energies, gradients, NAC, SOC, Hessian data, and MRSF-EKT records when
present.

When the corresponding property is requested via `[properties] scf_prop`,
`get_results()` also includes the following (identically for file-based and
`input_dict`/scripting-API runs):

| Key | Requested by | Meaning |
| --- | --- | --- |
| `dipole` | `el_mom` | Electric dipole vector (a.u.). |
| `mulliken_charges` | `mulliken` | Mulliken atomic partial charges (e). |
| `lowdin_charges` | `lowdin` | Löwdin atomic partial charges (e). |
| `resp_charges` | `resp` | RESP/ESP-fitted atomic charges (e). |
| `nmr_shielding` | `nmr` | Isotropic NMR shielding (ppm), shape `(natom, 5)`: columns are `dia`, `para_uncoupled`, `para_coupled`, `total_uncoupled`, `total_coupled`. |

`nac` is populated with the NACME derivative-coupling matrix for `runtype=nacme`
and is empty otherwise.

## Common Molecule Methods

| Method | Returns |
| --- | --- |
| `get_atoms()` | Atomic numbers as a copied NumPy array. |
| `get_mass()` | Atomic masses as a copied NumPy array. |
| `get_system()` | Cartesian coordinates in Bohr as a copied NumPy array. |
| `get_scf_energy()` | Total SCF energy. |
| `get_scf_energy("all")` | Dictionary of available SCF energy components. |
| `get_grad()` | Gradient in Hartree/Bohr. |
| `get_hess()` | Cartesian Hessian matrix when available. |
| `get_soc()` | SOC eigenvalues in cm-1 when available. |
| `get_data()` | Raw registered OpenQP data tags converted to lists. |
| `get_results()` | JSON-friendly calculation summary. |
| `write_molden(filename)` | Writes Molden orbital data. |

## Dynamic Tag Accessors

OpenQP registers several native data tags and creates matching Python getter
and setter methods. The method names are lower-case versions of the tag names.

| Tag | Getter | Typical content |
| --- | --- | --- |
| `OQP::DM_A` | `get_dm_a()` | Alpha density matrix. |
| `OQP::DM_B` | `get_dm_b()` | Beta density matrix. |
| `OQP::FOCK_A` | `get_fock_a()` | Alpha Fock matrix. |
| `OQP::FOCK_B` | `get_fock_b()` | Beta Fock matrix. |
| `OQP::E_MO_A` | `get_e_mo_a()` | Alpha orbital energies. |
| `OQP::E_MO_B` | `get_e_mo_b()` | Beta orbital energies. |
| `OQP::VEC_MO_A` | `get_vec_mo_a()` | Alpha MO coefficients. |
| `OQP::VEC_MO_B` | `get_vec_mo_b()` | Beta MO coefficients. |
| `OQP::Hcore` | `get_hcore()` | Core Hamiltonian. |
| `OQP::SM` | `get_sm()` | AO overlap matrix. |
| `OQP::TM` | `get_tm()` | Kinetic-energy matrix. |
| `OQP::td_energies` | `get_td_energies()` | TDHF/TDDFT excitation energies. |
| `OQP::td_mrsf_density` | `get_td_mrsf_density()` | MRSF density data. |
| `OQP::td_states_overlap` | `get_td_states_overlap()` | State-overlap matrix. |
| `OQP::soc_eval` | `get_soc_eval()` | SOC eigenvalues. |

Each dynamic tag also has a setter named `set_<tag>()`, for example
`set_dm_a(array)`. Setters mutate the native data store and are intended for
advanced workflows such as custom SCF experiments or internal coupling between
OpenQP modules.

## Units and Shapes

- Coordinates returned by `get_system()` are in Bohr.
- Gradients returned by `get_grad()` are in Hartree/Bohr.
- `get_soc()` reports SOC eigenvalues in cm-1.
- Many raw tag arrays are stored in flattened native order. Convert or reshape
  them using the current basis size, atom count, or state count before analysis.

When possible, prefer `runner.results()` or `mol.get_results()` for automated
post-processing because those summaries are less tied to native storage layout.
