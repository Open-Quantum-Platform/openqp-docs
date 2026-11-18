# `[scf]`

The `[scf]` section controls the reference wavefunction and SCF convergence
strategy. It is required for HF, DFT, MP2, TDHF/TDDFT, SF-TDDFT, MRSF-TDDFT,
SOC, NACME, and EKT workflows.

## Minimal Examples

Closed-shell singlet:

```ini
[scf]
type=rhf
multiplicity=1
```

Triplet ROHF reference for MRSF-TDDFT:

```ini
[scf]
type=rohf
multiplicity=3
```

## Keywords

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `rhf` |
| Values | `rhf`, `rohf`, `uhf` |
| Used by | reference selection |

Selects the SCF reference. Use `rhf` for closed-shell singlets, `rohf` for the
high-spin reference commonly used by SF/MRSF workflows, and `uhf` for
unrestricted references including UMRSF-TDDFT and UHF-referenced SF-TDDFT. Standalone MP2 supports RHF,
UHF, and ROHF references.

The input checker rejects `type=rhf` with `multiplicity>1`.

### `multiplicity`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | spin state and electron occupation |

Sets the spin multiplicity, `2S+1`. SF/MRSF examples usually use a triplet ROHF
reference with `multiplicity=3`.
In the high-level Python API, `job.theory.mrsf(...)` supplies this
usual MRSF reference multiplicity implicitly; set `multiplicity` in
`job.molecule(...)` for ordinary HF/DFT references or when overriding the
default deliberately.

### `maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `30` |
| Used by | SCF iteration loop |

Maximum number of SCF iterations before failure or fallback handling.

### `conv`

| Field | Value |
| --- | --- |
| Type | float or `auto` |
| Default | `auto` |
| Used by | SCF convergence test |

Convergence threshold for the SCF cycle, applied to the largest element of the
orbital gradient `FDS - SDF`. A number is used as given. `auto` (the default)
selects the threshold from the job:

| Job | `auto` resolves to |
| --- | --- |
| HF or DFT (`method=hf`) with `runtype` `energy`, `grad` or `optimize` | `1.0e-6` |
| Every other job: TDDFT/MRSF (`method=tdhf`) energies and gradients, NACs, MP2, CC, CASSCF and other correlated methods; Hessians and frequencies (`hess`, `thermo`, analytic or finite difference); dynamics (`md`, `namd`); path and saddle searches (`ts`, `irc`, `mep`, `neb`); `prop` and `data` | `1.0e-8` |

The energy error of a variational SCF is second order in the density error and
its nuclear gradient is first order, so `1.0e-6` keeps the HF/DFT gradient error
near `1e-6` Hartree/Bohr. This is far below the optimizer's `max_grad` of
`3e-4`. For thymine/cc-pVTZ the largest gradient change against `conv=1e-10` was
`5.2e-7` (RHF) and `8.9e-7` (B3LYP), with 20-25 % fewer SCF iterations.

Response, correlated and finite-difference jobs use the SCF solution beyond its
first derivative and keep `1.0e-8`. The log reports the resolved value as
`PyOQP scf convergence:`.

Set the value explicitly to override `auto`. For example, `scf(conv=1e-8)` in
`.oqp`, or `conv = 1e-8` under `[scf]`, restores the tighter threshold for an
HF/DFT gradient or optimization. Do this when gradients must agree beyond
`1e-6`, for example as the reference for your own finite differences.

### `maxdiis`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `7` |
| Used by | DIIS subspace |

Maximum number of vectors kept in the DIIS extrapolation space. Set
`maxdiis <= 13` whenever an active DIIS stage uses `ediis`, `adiis`, `vdiis`,
or any nonzero `vshift`; those paths use the deterministic simplex solver,
whose exact supported history limit is 13 states. The rule applies to the
primary DIIS/`auto`/`ml` converger, to an enabled `init_scf` stage when its
effective `init_converger` is DIIS, and to any DIIS stage selected through
`escalation` or `alternative_scf`. A calculation using only `soscf` or `trah`,
or unshifted `cdiis`, may use a larger history.

### `diis_type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `cdiis` |
| Values | `none`, `cdiis`, `ediis`, `adiis`, `vdiis` |
| Used by | DIIS convergence accelerator |

Selects the DIIS variant. `cdiis` is the default. `vdiis` can be useful for
difficult cases with level shifting. Active `ediis`, `adiis`, and `vdiis`
stages require `maxdiis <= 13`.

### `diis_reset_mod`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `10` |
| Used by | DIIS reset logic |

Controls periodic DIIS reset behavior.

### `diis_reset_conv`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.005` |
| Used by | DIIS reset logic |

Convergence threshold used by the DIIS reset heuristic.

### `cdiis_switch`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.3` |
| Used by | CDIIS switching heuristic |

Threshold for switching into CDIIS-style extrapolation.

### `vdiis_vshift_switch`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.003` |
| Used by | VDIIS level-shift behavior |

Threshold for VDIIS/level-shift switching.

### `vshift`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.0` |
| Used by | virtual-orbital level shift |

Applies a level shift during SCF. Larger values can stabilize convergence but
may slow final convergence. For an active DIIS stage, any nonzero value selects
the C-DIIS/E-DIIS/C-DIIS cascade regardless of `diis_type`, so `maxdiis` must
not exceed 13.

### `incremental`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | incremental Fock build |

Enables incremental Fock builds where supported.

### `incremental_reset`

| Field | Value |
| --- | --- |
| Type | string |
| Values | `error`, `period` |
| Default | `error` |
| Used by | incremental two-electron Fock construction |

Each SCF stage begins with a full Fock build. With `error`, DIIS and SOSCF
rebuild when the estimated accumulated integral-screening error exceeds
0.1 times the preceding SCF residual. The SOSCF residual is the RMS orbital
gradient. The estimate adds 1600 times the difference-density screening
threshold used in each incremental build since the last full build. Both
coefficients are empirical. The estimate supplies a rebuild criterion.

`period` retains the previous schedule: rebuild every tenth iteration and at
entry to the convergence tail (residual below 1e-4). In that tail SOSCF and
TRAH use full builds under `period`. TRAH uses this schedule under both
values. For `error` the DIIS or SOSCF convergence decision is confirmed
with a full build. When progressive screening pins its final thresholds
or grid, the next build is full.

Set `incremental=false` to build the full two-electron Fock matrix at every
iteration. The `incremental_reset` choice only applies to incremental Fock
builds.

```text
rks/bhhlyp/cc-pvdz grad scf(conv=1e-8,incremental_reset=error)
geom="molecule.xyz"
```

### `fock_reproducible`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | every two-electron Fock build (SCF, TDHF/TDDFT/MRSF response, z-vector) |

By default the two-electron Fock build hands shell pairs to OpenMP threads
dynamically, so the order in which contributions are summed, and hence the
last bits of the Fock matrix, changes from run to run. Two calculations of the
same input then stop at SCF points that differ slightly (orbitals by about
1e-9 at `conv=1e-8`). Energies are unaffected at any meaningful precision,
but quantities that are not stationary in the orbitals, and nearly degenerate
SCF solutions, can differ in the last digits between runs.

With `fock_reproducible=true` each shell pair is assigned to a fixed thread,
every thread accumulates its own Fock copy, and the copies are summed in
thread order. Repeated runs with the same `OMP_NUM_THREADS` and the same MPI
rank count then give bitwise identical energies and orbitals; the XC build is
always reproducible in this sense. Different thread counts still differ in
the last bits. The option costs about 2-4 % of the two-electron Fock time and
always keeps one Fock copy per thread (the low-memory shared atomic Fock is
not used).

```text
rks/b3lypv5/6-31g* scf(fock_reproducible=true)
```

### `mom`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | maximum-overlap method |

Enables MOM occupation tracking for challenging electronic states. In every
iteration, after the new Fock matrix is diagonalised, MOM occupies the orbitals
with the largest overlap with the previous orbitals instead of the lowest ones.
The first reference is the guess orbitals, so a non-aufbau guess (for example
one prepared with [`swapmo`](guess.md#swapmo)) is kept from the first
iteration, as long as MOM is already active there (see `mom_switch`):

```ini
[scf]
mom=true
mom_switch=100
```

MOM cannot be combined with TRAH. TRAH minimises the energy and never
rediagonalises the Fock matrix, so it would leave the targeted state.
`converger_type=trah` or `init_converger=trah` together with `mom=true` is an
input error. The escalation ladder, the `stability` pass and `converger_type=ml`
never use TRAH for a MOM calculation.

### `mom_switch`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.003` |
| Used by | MOM activation heuristic |

MOM becomes active once the DIIS error drops below this value. Before that,
each iteration fills the lowest orbitals. To keep a non-aufbau guess, set it above
the first DIIS error, for example `mom_switch=100`.

### `pfon`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | pseudo-fractional occupation number method |

Enables pFON smoothing for difficult SCF cases.

### `pfon_start_temp`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `2000.0` |
| Used by | pFON schedule |

Initial pFON electronic temperature.

### `pfon_cooling_rate`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `50.0` |
| Used by | pFON schedule |

Cooling rate used as pFON occupations are annealed.

### `pfon_nsmear`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `5.0` |
| Used by | pFON occupation smoothing |

Controls the smearing width/count used by the pFON method.

### `converger_type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `diis` |
| Values | `diis`, `soscf`, `trah`, `arh`, `auto`, `ml` |
| Used by | SCF convergence manager |

Selects the main SCF convergence strategy. `auto` and `ml` are Python-side
manager modes that choose a concrete native converger before dispatch.

`arh` runs the augmented Roothaan-Hall (ARH) trust-region method alone: every
macro-iteration uses the ARH model Hessian (see [`trh_arh`](#trh_arh)), so no
exact response Fock matrix is built. Each step costs about two Fock builds,
and convergence near the solution is linear, so a tight `conv` needs more
iterations than `trah`. Like DIIS, `arh` does no stability check of its own;
add `stability=true` for the TRAH stability pass after convergence.

`trah` and `arh` are rejected together with `mom=true` or `rstctmo=true`. When
`ml` would choose TRAH for such a calculation, DIIS is used instead.

### `init_converger`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `None` |
| Values | empty, `none`, `diis`, `soscf`, `trah`, `auto`, `ml` |
| Used by | initial SCF phase |

Overrides the converger used during an optional initial SCF stage. As with
`converger_type`, `trah` is rejected together with `mom=true` or
`rstctmo=true`.

### `alternative_scf`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `trah` |
| Values | `diis`, `soscf`, `trah`, `auto`, `ml` |
| Used by | fallback SCF attempts |

Fallback converger after repeated SCF difficulty.

### `escalation`

| Field | Value |
| --- | --- |
| Type | comma-separated string |
| Default | empty |
| Values | `diis`, `soscf`, `arh`, `trah` stages |
| Used by | custom fallback ladder |

When the primary converger does not converge, OpenQP tries further convergers
in turn, each starting from the orbitals of the previous one. The default
ladder is SOSCF, then ARH, then `alternative_scf` (TRAH). The primary converger
is removed from the ladder.

- The ARH stage runs at least 100 iterations, even when `maxit` is smaller,
  because ARH converges linearly; `maxit` is restored afterwards.
- A TRAH stage that follows ARH (as a ladder stage or as the primary
  converger) uses the exact Hessian, unless `trh_arh` is set explicitly.

`escalation` replaces this ladder. With `mom=true` or `rstctmo=true`
the TRAH and ARH stages are dropped from any ladder, because they cannot keep
the selected occupation. In an `.oqp` input, a list value must be quoted:

```ini
[scf]
escalation=soscf,trah
```

```text
scf(escalation="soscf,trah")
```

### `forced_attempt`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `2` |
| Used by | repeated SCF attempts |

Controls how many attempts the SCF manager can force before declaring failure
or escalating.

### `init_scf`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `no` |
| Values | `no`, `rhf`, `uhf`, `rohf`, `rks`, `uks`, `roks` |
| Used by | initial low-cost SCF stage |

Requests an initial SCF calculation before the main SCF. KS-style initial SCF
values (`rks`, `uks`, `roks`) require `[input] functional`.

### `init_basis`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `none` |
| Used by | initial SCF basis selection |

Basis used for the initial SCF stage. `library` can be used with
`init_library`.

### `init_library`

| Field | Value |
| --- | --- |
| Type | multiline string |
| Default | empty |
| Used by | tagged basis mapping for `init_basis=library` |

Maps atom tags to basis names for the initial SCF basis.

### `init_it`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `15` |
| Used by | initial SCF stage |

Maximum number of iterations in the initial SCF stage.

### `init_conv`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.001` |
| Used by | initial SCF stage |

Convergence threshold for the initial SCF stage.

### `save_molden`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | Molden output |

Set `scf(save_molden=true)` to write Molden files. Hessian calculations combine SCF
orbitals and normal modes in the frequency Molden file. MRSF-EKT calculations
also write a state-labeled Dyson Molden file after the EKT kernel completes.
See [Orbital and Vibrational Output](../workflows/orbital-vibrational-output.md).

### `rstctmo`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | MO ordering |

Restricts molecular-orbital ordering in workflows that need stable state or
orbital labels. The occupation chosen in the guess (for example with
[`swapmo`](guess.md#swapmo)) is kept through the iterations. This is the
delta-CHP core-hole route.

Like `mom`, `rstctmo` cannot be combined with TRAH (`converger_type=trah` or
`init_converger=trah` is an input error), and TRAH is never used for
escalation or stability.

### `scal_rel`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Values | `0`, `1`, `2` |
| Used by | scalar-relativistic one-electron Hamiltonian |

Selects the scalar relativistic Douglas-Kroll-Hess correction applied to the
spin-free one-electron core Hamiltonian:

| Value | Meaning |
| --- | --- |
| `0` | Disabled. |
| `1` | First-order Douglas-Kroll-Hess correction. |
| `2` | First- and second-order Douglas-Kroll-Hess correction. |

This is not the SOC switch. `scal_rel` changes the scalar, spin-free
Hamiltonian; SOC is selected separately with `[input] runtype=soc` and
`[input] soc_2e`. See [References](../references.md#scalar-relativistic-correction)
for the DKH background.

The input-file default is `scal_rel=0`. In the high-level Python API,
`job.workflow.soc(...)` sets `scal_rel=2` by default for the SOC workflow
because the documented SOC path uses a DKH2 spin-free Hamiltonian before the
SOC matrix is formed. Pass `scal_rel=0`, `1`, or `2` to override that helper
default.

### `scal_rel_decontract`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Values | `0`, `1` |
| Used by | scalar-relativistic one-electron Hamiltonian (`scal_rel=1` or `2`) |

Selects the basis in which the Douglas-Kroll-Hess decoupling is carried out:

| Value | Meaning |
| --- | --- |
| `1` | The basis is decontracted (one shell per unique primitive exponent per atom, angular momentum and angular type), the decoupling is carried out there, and the relativistic correction to the core Hamiltonian is projected back onto the contracted basis with the contraction matrix. |
| `0` | The decoupling is carried out directly in the contracted basis (the behaviour before this keyword existed). |

Use the default. The contracted basis truncates the kinetic-balance space of the
decoupling, and with contracted relativistic basis sets the resulting
Hamiltonian is not variational: the DKH2 energy of the mercury atom in a
contracted Sapporo-DKH3-DZP basis is about 2300 Hartree below the energy
obtained with the same basis fully uncontracted, and about 2300 Hartree below
the Dirac-Coulomb Hartree-Fock limit. With `scal_rel_decontract=1` the
contracted-basis energy lies within the usual contraction error above the
uncontracted-basis value (0.56 Hartree for that case; 0.1 Hartree for krypton
in x2c-TZVPall). For an already uncontracted basis both values give the same
result.

The decontraction applies only to the construction of the relativistic core
Hamiltonian; the SCF itself still uses the contracted basis. `0` is kept to
reproduce earlier results and for comparison.

### `stability`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | SCF stability analysis |

Requests stability analysis where wired. The analysis uses TRAH with the exact
Hessian and is skipped for `mom=true` and `rstctmo=true` calculations. It runs
after a DIIS, SOSCF or `arh` primary converger; a `trah` primary converger
checks stability itself, so the extra pass is skipped there.

### `soscf_lvl_shift`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0` |
| Used by | SOSCF convergence |

Level shift used by the SOSCF converger.

### `verbose`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` (`0` for [`runtype = md`](input.md#runtype) and `namd`) |
| Values | `0`, `1`, `2`, `3` |
| Used by | the text log of the whole run |

Older spelling of [`[input] verbose`](input.md#verbose), which sets the log level
for the whole run. It is still read: when both are given, the one that differs
from the default `1` wins, `[input]` first. Its effect on the molecular-orbital
table after each SCF is:

| Value | Effect |
| --- | --- |
| `0` | No molecular-orbital table. |
| `1` | Orbital energies, without coefficients, after a converged SCF (the default). |
| `2` and above | Orbital energies and coefficients, also when the SCF did not converge. |

The orbital table is written after every SCF, and a dynamics run calls the SCF
at least once per step, so at the default it is repeated for every step of the
trajectory: a 100-step QM/MM surface-hopping run of an 18-atom QM region wrote
405 tables and 83 MB of log, in which the 101 lines that report the dynamics
are impossible to find. [`runtype = md`](input.md#runtype) and `namd`
therefore default this keyword to `0` unless `[input] verbose` or
`[scf] verbose` is set to a value other than `1`; write `verbose = 2` in the
deck to get the tables back for a trajectory.

Only the log is affected. The orbitals of any frame remain available from the
Molden file, the restart record and the
[trajectory file](../workflows/soc-namd-qmmm.md), and the setting does not change
any computed quantity.

## TRAH Keywords

TRAH is the trust-region augmented Hessian SCF converger. It is implemented
natively; the external OpenTrustRegion (OpenTRAH) backend was removed.

### `trh_impl`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Accepted | `auto`, `native` |
| Used by | TRAH implementation selection |

Selects the TRAH implementation. Both accepted values resolve to the native
trust-region augmented-Hessian solver, which is the only implementation.

`otr`, which selected the external OpenTrustRegion backend, is **no longer
accepted**: the backend was removed and an input requesting it now fails with a
`ValueError` naming the accepted values, rather than silently running the native
solver instead.

### `trh_arh`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `-1` |
| Values | `-1`, `0`, positive integer |
| Used by | TRAH and ARH Hessian |

Selects the Hessian of the TRAH micro-iterations.

- `0` uses the exact response Hessian.
- A positive `n` uses the augmented Roothaan-Hall (ARH) model, built from the
  last `n` density and Fock matrices (Host et al., J. Chem. Phys. 129, 124106
  (2008)). TRAH then uses the model while the RMS orbital gradient is
  above `1e-4` and the exact Hessian from there on, including the stability check
  at convergence.
- `-1` (default) depends on the reference: `20` for ROHF/ROKS and UHF/UKS, and
  `0` for RHF/RKS. On closed-shell systems the model saved no Fock builds.

The model changes only the path to the solution: the orbital gradient is
exact, so the converged energy is the same as with the exact Hessian. Set
`trh_arh=0` to reproduce the exact-Hessian TRAH of earlier versions.

With `converger_type=arh`, the model is used in every step, and a positive
`trh_arh` sets its memory (default `20`).

```text
rohf/6-31g* mult=2 scf(converger_type=trah,trh_arh=0)
```

### `trh_stab`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | TRAH stability mode |

Enables TRAH stability behavior.

### `trh_ls`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | TRAH line search |

Enables line search inside TRAH.

### `trh_sub_solver`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `davidson` |
| Used by | TRAH micro-iteration solver |

Selects the subsystem solver used by TRAH.

### `trh_nrtv`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | TRAH random trial vectors |

Number of random trial vectors used in the TRAH subsystem.

### `trh_r0`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.4` |
| Used by | TRAH trust radius |

Initial TRAH trust radius.

### `trh_jd_start`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `30` |
| Used by | TRAH Jacobi-Davidson switch |

Iteration threshold for the Jacobi-Davidson path in TRAH.

### `trh_nmic`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50` |
| Used by | TRAH micro-iterations |

Maximum number of TRAH micro-iterations.

### `trh_gred`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.001` |
| Used by | TRAH global reduction |

Global reduction factor for the TRAH microproblem.

### `trh_lred`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.0001` |
| Used by | TRAH local reduction |

Local reduction factor for the TRAH microproblem.

### `xc_c2f`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` (follows `perf`) |
| Values | `on`, `off`, `auto` |
| Used by | DFT SCF — coarse-to-fine XC grid during descent |

Use a coarse XC grid during the SCF descent and the full grid in the convergence
tail. Exact at convergence. See [Performance](../performance.md).

### `xc_phi_cache`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` (follows `perf`; no preset enables it) |
| Values | `on`, `off`, `auto` |
| Used by | DFT SCF — collocation-Φ cache |

Cache the collocation Φ across SCF iterations (exact). Opt-in; on the CPU
benchmark it was net-negative, so no preset enables it.

### `xc_incdft`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` (follows `perf`; no preset enables it) |
| Values | `on`, `off`, `auto` |
| Used by | DFT SCF — incremental DFT (experimental) |

Incremental XC from density differences. Experimental; typically slows SCF
convergence. Opt-in only.

### `grad_cutoff`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `auto` (follows `perf`; `1.0d-10` baseline) |
| Used by | gradients — 2e-derivative Schwarz cutoff |

Schwarz block cutoff for the 2e-derivative gradient build. Looser values trade a
small gradient error for speed (`1.0d-8` ≈ 5×10⁻⁷ a.u.).

## Progressive Screening Keywords

Progressive screening is an opt-in SCF acceleration path. During the early
descent it may use looser integral and XC-grid thresholds; once the DIIS error
falls below `pscreen_tight`, it returns to the normal converged thresholds. No
performance preset enables it automatically.

Set the screening controls in the calculation input. If a legacy screening
environment variable is set, OpenQP stops and reports its corresponding input
keyword. For an existing shell script, move the old value to the keyword shown
below and unset the environment variable before starting OpenQP.

| Legacy environment variable | `[scf]` keyword |
| --- | --- |
| `OQP_PSCREEN` | `pscreen` |
| `OQP_PSCREEN_K` | `pscreen_k` |
| `OQP_PSCREEN_CAP` | `pscreen_cap` |
| `OQP_PSCREEN_TIGHT` | `pscreen_tight` |
| `OQP_PSCREEN_XC_DCUT` | `pscreen_xc_dcut` |
| `OQP_PSCREEN_XC_AOCUT` | `pscreen_xc_aocut` |
| `OQP_PSCREEN_GRID_RAD` | `pscreen_grid_rad` |
| `OQP_PSCREEN_GRID_ANG` | `pscreen_grid_ang` |

### `pscreen`, `pscreen_k`, `pscreen_cap`, `pscreen_tight`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `pscreen` | boolean | `False` | Enable progressive integral/grid screening. |
| `pscreen_k` | float | `1.0e-2` | Safety factor in the iteration-dependent cutoff, approximately `pscreen_k * DIIS error`. |
| `pscreen_cap` | float | `1.0e-8` | Loosest permitted integral cutoff. Values looser than `1e-8` can risk changing the SCF state. |
| `pscreen_tight` | float | `1.0e-4` | DIIS-error threshold for returning to tight cutoffs; the effective value is at least `10 * scf.conv`. |

### `pscreen_xc_dcut`, `pscreen_xc_aocut`, `pscreen_grid_rad`, `pscreen_grid_ang`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `pscreen_xc_dcut` | float | `0.0` | Loose XC density cutoff during descent; zero disables this ramp. |
| `pscreen_xc_aocut` | float | `0.0` | Loose XC AO-pruning threshold during descent; zero disables it. |
| `pscreen_grid_rad` | integer | `0` | Coarse radial-grid size during descent; both grid sizes must be positive to enable this progressive-screening override. |
| `pscreen_grid_ang` | integer | `0` | Coarse angular-grid size during descent; zero disables this override, independent of the separate `xc_c2f` schedule. |

Keep `pscreen_tight` safely above the final SCF convergence threshold so the
calculation reaches the normal integral and grid accuracy before convergence.
When an error-budget adaptive grid builds its descent grid, that grid supplies
the coarse sizes. To specify the descent sizes with
`pscreen_grid_rad` and `pscreen_grid_ang`, choose a fixed production grid
with `dftgrid(rad_npts=50,ang_npts=230)` or another supported fixed size.
