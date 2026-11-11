# `[guess]`

The `[guess]` section controls initial orbitals, JSON restart files, and manual
MO swaps. Omit it to let OpenQP choose the initial guess automatically.

## Minimal Example

```text
rhf/def2-svp
geom="water.xyz"
```

## Keywords

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Values | `auto`, `huckel`, `modhuckel`, `hcore`, `json`, `previous`, `sap`, `minao`, `sad` |
| Used by | initial density/orbital construction |

Selects the initial guess mode.

| Value | Meaning |
| --- | --- |
| `huckel` | Native extended-Huckel style guess. |
| `modhuckel` | Modified Huckel guess. |
| `hcore` | Core-Hamiltonian guess. |
| `json` | Read orbitals and molecular data from a JSON restart file. |
| `auto` | Use compatible supplied orbitals when available. For a fresh guess, use SAD for open-shell lanthanide systems, MINAO for elements covered by its table, and SAP otherwise. |
| `sap` | Superposition-of-atomic-potentials guess. |
| `minao` | Projected minimal-basis density guess. |
| `sad` | Superposition of atomic densities. |
| `previous` | Reuse the previous orbitals when available. |

Use `json` for exact restarts and `auto` for workflows that may or may not have
a previous restart file.

### `occupation_trials`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |

Use `guess(occupation_trials=true)` to compare candidate occupations when an
initial guess has a degenerate orbital level at an occupation boundary that
splits into different symmetry components. Each candidate gets up to five SCF
iterations. The main SCF starts from the orbitals and density of the candidate
with the lowest trial energy. This short comparison does not establish the
lowest fully converged SCF state.

OpenQP skips the trials when the occupation is selected by MO swaps, MOM, or
restricted orbital rotation, when the candidate count exceeds the internal
limit, or when the calculation uses QM/MM embedding. By default the orbital
symmetry adaptation uses the symmetry table order without running trials.

### `file`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | `type=json`, `type=auto` |

Path to a JSON restart file. With `type=json`, the file must exist. With
`type=auto`, OpenQP uses it when present and otherwise computes a fresh guess.

### `file2`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | NACME and previous-step workflows |

Path to a second JSON restart file. NACME can use `file2` for previous-step
information. If it is omitted, NACME can instead use `[input] system2`.

### `save_mol`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | restart, orbital export, and inspection workflows |

Requests saving molecular data for later restart or inspection. Supported
bases also add portable AO basis, molecular-orbital, vibrational, and
state-specific Dyson data for visualization. See
[Orbital and Vibrational Output](../workflows/orbital-vibrational-output.md).

For a full restart bundle, keep the current same-stem `.json` and `.npz` files
together. Repeated saves update that one `.npz` file and the checksum in the
JSON. A copy of only the JSON is not a preserved snapshot: after a later save,
its old checksum may no longer match the current NPZ. Pause saves, then copy
both files to a new location when a historical restart is needed. Existing
JSON files that reference hash-suffixed NPZ files remain readable; OpenQP does
not automatically delete those older sidecars.

Current writable result pairs also use an adjacent `<stem>.json.lock` file to
coordinate readers and writers. A copied `.json`/`.npz` pair without this lock
remains readable as a snapshot. Before overwriting such a copied **same-stem**
pair, stop all readers and writers and have the result-directory owner create
the empty `<stem>.json.lock` file with read access for readers and write access
for writers. OpenQP refuses the first overwrite until that lock exists. Keep
the lock file with any copy that will be updated. Legacy hash-suffixed NPZ
files remain immutable during migration to the same-stem format.

### `continue_geom`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | JSON restart geometry |

When true, reuses geometry from the JSON restart file. The input checker warns
if `continue_geom=true` is set without `type=json`.

### `swapmo`

| Field | Value |
| --- | --- |
| Type | comma-separated integer list |
| Default | empty |
| Used by | manual orbital reordering before SCF |

Swaps molecular orbitals in pairs. The list must contain an even number of
indices:

```ini
[guess]
swapmo=2,7,8,21
```

This swaps `2` with `7` and `8` with `21`. Use it only when you know the target
orbital ordering.

The swap acts on the alpha orbitals. What happens to the guess density
depends on the guess type:

- Computed guesses (`huckel`, `hcore`, ...): the density of the computed guess is
  kept. The swap only names the occupation that
  [`rstctmo`](scf.md#rstctmo) or [`mom`](scf.md#mom) then follow from the first
  iteration. Without one of them, the first Fock diagonalisation refills the
  lowest orbitals and the swap has no effect.
- Supplied guesses (`json`, `auto` with an existing file, `previous`): the
  guess density is rebuilt from the swapped orbitals, because a supplied guess
  can be accepted as converged on the first iteration and its orbitals and
  density must describe the same state. RHF: the doubly occupied density from
  the swapped orbitals. ROHF: both spin densities from the swapped alpha
  orbitals, and the beta orbitals are replaced by them. UHF: each spin density
  from its own orbitals.
