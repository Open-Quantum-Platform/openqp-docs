# Wavefunction methods

OpenQP provides native determinant-space FCI, CASCI, CASSCF, state-averaged
CASSCF, and second-order multireference perturbation methods. These workflows
require an RHF reference: leave `[input] functional` empty and use
`[scf] type=rhf` with `multiplicity=1`.

The method selects which sections are read:

| `[input] method` | Required controls | Optional controls |
| --- | --- | --- |
| `fci` | `[fci]` | — |
| `casci` | `[cas]`, `[ci]` | `[state_average]` |
| `casscf`, `sa-casscf` | `[cas]`, `[ci]`, `[casscf]` | `[state_average]` |
| `caspt2`, `ms-caspt2`, `xms-caspt2` | `[cas]`, `[ci]`, `[pt2]` | `[casscf]`, `[state_average]` |
| `mrmp2`, `mcqdpt2`, `xmcqdpt2` | `[cas]`, `[ci]`, `[pt2]` | `[casscf]`, `[state_average]` |

## Minimal inputs

FCI uses its self-contained section:

```ini
[input]
system=
  H  0.0  0.0  0.0
  H  0.0  0.0  0.74
method=fci
runtype=energy
basis=sto-3g
functional=

[scf]
type=rhf
multiplicity=1

[fci]
nroot=1
solver=auto
```

CASCI and CASSCF separate the active-space, CI, and orbital-optimization
controls:

```ini
[input]
method=casscf
runtype=energy
basis=sto-3g
functional=

[cas]
active_electrons=2
active_orbitals=2
frozen_core=0

[ci]
nroot=2
solver=auto
target_spin=singlet

[casscf]
root=0
converger=trah
hessian=fd
```

For equal-weight two-state SA-CASSCF, add:

```ini
[state_average]
enabled=true
nstate=2
equal_weights=true
target_roots=0,1
```

For CASPT2 on the converged reference, add `[pt2]` and set
`[input] method=caspt2`:

```ini
[pt2]
reference=casscf
h0=fock
contraction=uncontracted
ipea_shift=0.0
```

Runnable examples are in
[`examples/WF_methods`](https://github.com/Open-Quantum-Platform/openqp/tree/main/examples/WF_methods).

## `[fci]`

`[fci]` is used only by `method=fci`. It combines the active-space and solver
controls that CAS methods keep in separate sections.

| Keyword | Default | Meaning |
| --- | --- | --- |
| `nroot` | `1` | Number of CI roots returned. |
| `active_electrons`, `active_orbitals` | `0`, `0` | Optional restricted active space; zeros mean full CI. |
| `frozen_core` | `0` | Number of doubly occupied orbitals folded into the core. |
| `solver` | `auto` | `auto`, `dense`, or `davidson`. |
| `max_det` | `5000` | Determinant-count safety limit. |
| `max_memory` | `2048` | Combined working-memory ceiling in MiB. |
| `eig_tol` | `1.0e-10` | Eigenpair residual tolerance. |
| `davidson_maxiter`, `davidson_subspace` | `100`, `0` | Davidson iteration and subspace limits; zero subspace selects the automatic size. |
| `target_spin` | `any` | `any`, a multiplicity name such as `singlet`, or an integer multiplicity. |
| `print_ci_vectors`, `save_ci_vectors`, `save_rdm` | `false` | Optional CI diagnostics and artifacts. |

The only integral backend is `integral_backend=native`. Use
`integral_cutoff` to screen small determinant-Hamiltonian contributions.

## `[cas]`

`[cas]` defines the orbital partition shared by CASCI, CASSCF, and PT2.

| Keyword | Default | Meaning |
| --- | --- | --- |
| `active_electrons` | `0` | Total active electrons; required by the compact helpers. |
| `active_orbitals` | `0` | Number of active spatial orbitals. |
| `frozen_core` | `0` | Number of frozen doubly occupied orbitals. |
| `active_orbital_indices`, `core_orbital_indices` | empty | Explicit 1-based orbital selections. |
| `orbital_source` | `rhf` | `rhf`, `json`, or another supported orbital source. |
| `orbital_file` | empty | File used by a non-RHF orbital source. |
| `sort_orbitals` | `energy` | Ordering used before the active partition is formed. |
| `localize` | `none` | Optional orbital localization. |
| `max_det`, `max_memory` | `5000`, `2048` | Determinant and combined memory safety limits. |

Explicit scattered orbital selections are supported by CASCI. CASSCF and PT2
currently require a contiguous core/active partition.

## `[ci]`

`[ci]` controls the active-space eigensolver for CAS methods.

| Keyword | Default | Meaning |
| --- | --- | --- |
| `nroot` | `1` | Number of reference roots to solve. |
| `solver` | `auto` | `auto`, `dense`, or `davidson`. |
| `eig_tol` | `1.0e-10` | Eigenpair residual tolerance. |
| `davidson_maxiter`, `davidson_subspace` | `100`, `0` | Davidson limits. |
| `target_spin` | `any` | Requested spin multiplicity. |
| `root_tracking` | `energy` | Root ordering/tracking policy. |
| `print_ci_vectors`, `save_ci_vectors`, `save_rdm` | `false` | Optional diagnostics and artifacts. |

`nroot` must cover every CASSCF root, state-average target, and PT2 target.

## `[casscf]`

| Keyword | Default | Meaning |
| --- | --- | --- |
| `max_macro_iterations` | `20` | Orbital-optimization iteration limit. |
| `root` | `0` | Zero-based state-specific objective root. |
| `converger` | `trah` | `trah`, `ah`, `twophase`, `diis`, or `auto`. |
| `hessian` | `fd` | Finite-difference (`fd`) or analytic orbital Hessian. |
| `gradient_norm_tol` | `1.0e-6` | Orbital-gradient convergence threshold. |
| `energy_decrease_tol` | `1.0e-10` | Energy-change threshold. |
| `step_norm_tol` | `1.0e-8` | Orbital-step threshold. |
| `max_rotation_norm` | `0.2` | Maximum orbital-rotation norm. |
| `canonicalize` | `true` | Canonicalize the converged orbitals. |

The `ah_*`, `diis_*`, and diagnostic keywords provide detailed control of the
selected converger. `max_macro_iterations=0` runs the fixed-orbital CASCI
scaffold and performs no orbital optimization.

## `[state_average]`

| Keyword | Default | Meaning |
| --- | --- | --- |
| `enabled` | `false` | Enable a state-averaged CAS objective. |
| `nstate` | `0` | Number of averaged states. |
| `target_roots` | empty | Zero-based CI roots included in the average. |
| `equal_weights` | `true` | Assign equal normalized weights. |
| `weights` | `1.0` | Explicit weights when `equal_weights=false`. |
| `root_tracking` | `overlap` | Track roots between orbital iterations. |

The number of weights must equal the number of target roots. Weights are
normalized internally and must contain a positive total.

## `[pt2]`

| Keyword | Default | Meaning |
| --- | --- | --- |
| `reference` | `casscf` | `casscf` or fixed-orbital `casci` reference. |
| `variant` | `auto` | Single-state, multistate, or extended-multistate variant inferred from the method by default. |
| `h0` | `fock` | `fock` for CASPT2/QDPT or `dyall` for NEVPT2. |
| `contraction` | `uncontracted` | `uncontracted` or `strong` (SC-NEVPT2). |
| `target_roots`, `nroot` | empty, `0` | PT2 target model space; zero inherits `[ci] nroot`. |
| `ipea_shift`, `level_shift`, `imaginary_shift`, `edshft` | `0.0` | Denominator regularization controls. |
| `engine` | `auto` | Automatic, direct/Fortran, or dense QDPT engine. |
| `nproc` | `0` | Worker count; zero selects the automatic value. |
| `max_terms` | `30000000` | Direct-engine streamed-term limit. |
| `max_memory` | `2048` | PT2 memory ceiling in MiB, combined with the tighter `[cas]` ceiling. |
| `semi_canonical` | `true` | Semicanonicalize the reference orbitals. |

Use `h0=dyall, contraction=strong` for strongly contracted NEVPT2. The
QDPT family (`mrmp2`, `mcqdpt2`, and `xmcqdpt2`) uses the diagonal-Fock direct
engine and accepts `edshft`; `edshft` is mutually exclusive with real or
imaginary level shifts.

## Python helpers

The fluent API writes the same sections and validates the required active
space:

```python
from oqp.openqp import OpenQP

job = OpenQP("h4_xms")
job.molecule(geometry="h4.xyz", charge=0)
job.caspt2(
    active_electrons=2,
    active_orbitals=2,
    variant="xms-caspt2",
    nroot=2,
    basis="sto-3g",
)
mol = job.run()
print(mol.get_results()["energies"])
```

Available helpers include `fci`, `casci`, `casscf`, `sa_casscf`, `caspt2`,
`nevpt2`, and `qdpt2`. A helper call resets method-owned state from an earlier
call on the same builder unless that state is explicitly supplied again.
