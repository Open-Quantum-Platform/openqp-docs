# NAMD Numerical Continuity

This page describes the four numerical situations identified in the analytic
MRSF-TDDFT nonadiabatic-coupling study as possible causes of premature
trajectory termination. They are not four independent surface-hopping methods,
and satisfying one of their criteria does not by itself terminate a
trajectory. More than one case can occur during the same nuclear step.

The recommended setting is the default:

```text
namd(S1,scheme=TDC_NAC,continuity=on)
md(nstep=400,dt=0.5,velocity="molecule.vel")
```

`continuity=on` applies one internally consistent set of treatments for cases
A--D. Use `continuity=manual` only when reproducing a comparison, assessing a
threshold, or intentionally disabling one treatment. In manual mode every
changed value must be reported with the trajectory because it can change the
surviving ensemble.

## Summary of Cases A--D

| Case | Numerical situation | Criterion or origin | Default action with `continuity=on` | Does the criterion terminate a trajectory? |
| --- | --- | --- | --- | --- |
| A | Rotation within the doubly occupied orbital space | Consecutive occupied orbitals can rotate even though the occupied subspace is unchanged. | Evaluate state overlaps with exact determinant-factorized minors (`state_overlap=exact`). | No. The exact overlap removes the false loss of state overlap caused by a truncated formula. |
| B | Change of the two-SOMO electronic reference | Either matched SOMO overlap is below `0.5`. | Reuse the preceding orbitals; use SOSCF, then the normal SCF escalation and one fresh-guess retry; diagnose the reference change and consider numerical energy correction after finer nuclear integration. | The SOMO criterion does not terminate the trajectory. Termination occurs only if every SCF attempt fails to converge. |
| C | Loss of active-state character from the retained state space | The projection norm of the current active state onto the preceding retained states is below `0.7`. | Record the event and the missing squared norm; retain the specified state count. | No. It is a diagnostic requiring a larger-state convergence study, not a hop or velocity-rescaling condition by itself. |
| D | Finite-step nuclear integration error | The pre-hop total-energy change exceeds `0.002` Ha in magnitude. | Repeat the nuclear interval with progressively finer subdivisions up to 10; if a residual change remains, permit the documented numerical energy correction when its physical positivity conditions are satisfied. | No. The condition requests recalculation. A separate `nve_policy=error` can stop a calculation under its own criteria. |

These responses occur before electronic propagation and stochastic hop
selection for the interval. A numerical energy correction is distinct from
momentum adjustment after a physical surface hop.

## `continuity`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `on` |
| Values | `on`, `manual` |
| Used by | cases A--D below |

`on` fixes the production settings listed on this page. OpenQP rejects an
individual A--D override while `continuity=on`; this prevents a partially
modified calculation from being mistaken for the complete treatment.

`manual` exposes the case-specific settings. For example:

```text
mrsf(nstate=6)/bhhlyp/6-31g*
namd(S1,scheme=TDC_NAC,continuity=manual,
     state_overlap=exact,
     state_check=true,state_tol=0.8,
     disc_tol=0.001,disc_substeps=20)
md(nstep=400,dt=0.5,velocity="molecule.vel")
```

The example tightens the case-C and case-D criteria. It does not imply that
`0.8`, `0.001` Ha, or 20 substeps are generally preferable; they require a
state-count and nuclear-time-step convergence assessment for the molecular
system.

## Case A: Doubly Occupied Orbital Rotation

The orbital-overlap matrix between consecutive geometries is

\[
S_{pq}^{\mathrm{MO}}=\langle\phi_p(t)|\phi_q(t+\Delta t)\rangle.
\]

Nearly degenerate doubly occupied orbitals may undergo a unitary rotation.
Their individual diagonal overlaps can then be much smaller than one although
the occupied subspace and electronic reference are continuous. A truncated
Leibniz expansion that assumes nearly diagonal molecular-orbital overlaps can
therefore yield an artificially small many-electron state overlap. This can
produce an artificially large overlap time-derivative coupling or apparent
loss of state identity.

The automatic treatment is `state_overlap=exact`, which evaluates the required
minor determinants exactly. It is the default and normally should be omitted
from the input. With `continuity=manual`, `state_overlap=tlf1` and
`state_overlap=tlf2` select first- and second-order truncated formulas for
controlled method comparisons. They are not recommended as general NAMD
settings.

The legacy internal representation is `[tdhf] tlf=0`, `1`, or `2`. It remains
accepted for old sectioned inputs because the determinant-minor evaluation was
historically implemented in the TDHF/MRSF response code. New inputs should not
place this NAMD choice in `tdhf(...)`; use the public `state_overlap` keyword.

Case A is not detected by a scalar threshold and then repaired. Exact overlap
evaluation is used at every step, including steps without a large occupied-
orbital rotation.

## Case B: Electronic-Reference Change

MRSF-TDDFT uses a high-spin two-SOMO reference. Along a trajectory, orbital
character can exchange between the doubly occupied and singly occupied spaces,
or an SCF calculation can converge to a different solution. The resulting
change of reference can cause an abrupt change in MRSF energies even when the
nuclear displacement is small.

OpenQP first continues the preceding solution. With the automatic settings it
reuses the preceding orbitals (`mo_reuse=True`), follows them with SOSCF
(`ref_follow=soscf`), retains the normal robust SCF escalation
(`scf_fail=escalate`), and permits one fresh-guess attempt after failed
continuation (`scf_guess_retry=True`). If all SCF attempts fail, the required
reference is unavailable and the trajectory terminates; numerical energy
correction never substitutes for a converged SCF calculation.

After convergence, OpenQP matches the two SOMOs between consecutive steps. A
matched overlap below `somo_tol=0.5` records a reference-change event. This is
a diagnosis of the converged solution; it does not constrain the SOMOs during
SCF optimization.

With `ref_switch_rescale=True`, a detected reference change makes numerical
energy correction eligible, but only after the finer-step recalculation in
case D has been attempted and a residual change remains. The target kinetic
energy and current kinetic energy must both be positive. Otherwise the
velocities remain unchanged and the unsuccessful correction is recorded.

Manual controls for case B are:

| Keyword | Default | Meaning |
| --- | --- | --- |
| `mo_reuse` | `True` | Use the preceding orbitals as the next SCF guess. |
| `ref_follow` | `soscf` | Select `off`, `soscf`, or `diis_vshift` for reference continuation. |
| `scf_fail` | `escalate` | Use the robust converger sequence; `restart` creates a fresh-reference boundary. |
| `scf_guess_retry` | `True` | Permit one fresh-guess calculation after failed continuation. |
| `somo_tol` | `0.5` | Record case B if either matched SOMO overlap is below this value. |
| `ref_switch_rescale` | `True` | Permit the post-substepping numerical energy correction for case B. |

## Case C: Loss from the Retained State Space

Let the retained states at the preceding step define

\[
\hat P_{\mathrm{ret}}^n=\sum_{I\in\mathrm{ret}}
|\Psi_I^n\rangle\langle\Psi_I^n|.
\]

For the current active state \(a\), OpenQP evaluates

\[
q_a^2=\langle\Psi_a^{n+1}|\hat P_{\mathrm{ret}}^n|
\Psi_a^{n+1}\rangle
=\sum_{I\in\mathrm{ret}}|S_{Ia}|^2.
\]

The automatic criterion is `state_tol=0.7`. Therefore `q_a<0.7` means that
more than \(1-0.7^2=0.51\) of the squared norm lies outside the preceding
retained state space. The event is printed when `state_check=True`.

This criterion does not identify its cause uniquely. A reference change can
also reduce `q_a`, so the case-B SOMO overlaps must be examined first. If the
reference remains continuous, calculate additional states at both geometries,
reevaluate the exact projection, and repeat the dynamics with larger retained
state spaces to determine the required `nstate`.

Case C alone does not increase `nstate`, select a surface hop, or authorize
velocity rescaling. Numerical energy correction cannot restore omitted
electronic-state character.

| Keyword | Default | Meaning |
| --- | --- | --- |
| `state_check` | `True` | Evaluate and report the retained-space projection criterion. |
| `state_tol` | `0.7` | Record case C when \(q_a\) is below this value; allowed range `(0,1]`. |

With `continuity=manual`, set `state_check=False` to suppress this diagnosis
or change `state_tol` for a defined convergence study.

## Case D: Finite-Step Nuclear Integration Error

A nuclear interval can cross a region in which the active-state force varies
rapidly. A large pre-hop total-energy change can then arise from finite-step
integration even when the potential-energy surface is continuous. OpenQP
compares the current pre-hop total energy with the preceding-step value. If
the magnitude of the change exceeds `disc_tol=0.002` Ha, it restores the
initial phase point and repeats the same interval with finer nuclear steps.
The electronic structure and active-state force are recomputed at every
substep.

With `disc_substeps=10`, the current implementation tries 2, 4, 8, and finally
10 equal subdivisions, stopping when the criterion is satisfied. The analytic-
NAC paper's reported uracil comparison used one repetition with ten 0.05-fs
substeps for a 0.5-fs interval; the progressive sequence is an implementation
extension that can avoid unnecessary electronic-structure calculations.

After the configured subdivisions are exhausted, `disc_rescale=True` permits
an isotropic numerical velocity adjustment for a residual energy change. It
is applied only with a converged SCF reference and positive current and target
kinetic energies. It conserves the corrected step's total energy but does not
establish force continuity, restore missing state character, or represent a
physical hop.

Manual controls for case D are:

| Keyword | Default | Meaning |
| --- | --- | --- |
| `disc_tol` | `0.002` Ha | Energy-change criterion for finer nuclear integration and residual correction. |
| `disc_substeps` | `10` | Maximum number of equal subdivisions; `0` disables the explicit setting, although a correction enabled for case B or D requires at least two subdivisions. |
| `disc_rescale` | `True` | Permit last-resort numerical correction after the finer-step attempts. |

Cases B and D are coupled by a physical restriction: a numerical correction
must not be applied before a finer-step integration has been attempted. Thus
`ref_switch_rescale=True` or `disc_rescale=True` requires at least two nuclear
substeps even in manual mode.

## What Can Actually Stop the Calculation?

The A--D criteria should not be interpreted as four automatic termination
conditions:

- Case A is treated continuously by exact overlap evaluation.
- The case-B overlap criterion records a changed reference; only failure of
  every SCF attempt terminates the calculation.
- Case C is a warning that the retained state space may be incomplete.
- Case D requests finer integration and, when allowed, a numerical correction.

Independent strict diagnostic settings can still stop a run. In particular,
`nve_policy=error` and `nacme_policy=error` apply the criteria documented under
[NAMD Diagnostics](md-diagnostics.md). They are not part of cases A--D and are
not enabled as termination policies by `continuity=on`.
