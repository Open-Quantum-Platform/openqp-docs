# NAMD Diagnostics

These options compare numerical quantities and report deviations. They are
separate from the four numerical-continuity cases described in
[NAMD Numerical Continuity](md-continuity.md).

## Coupling Comparisons

| Keyword | Default | Meaning |
| --- | --- | --- |
| `nacme_check` | `off` | Compare the propagation coupling with `baeck_an` or `analytic`; `off` performs no comparison. |
| `ba_gap_max` | `0.0734986443513` Ha (2 eV) | Largest state gap included in a Baeck--An comparison. |
| `nacme_policy` | `off` | `off`, `warn`, or `error` response to the comparison criteria. |
| `nacme_policy_invariant_tol` | `1.0e-10` | Antisymmetry and diagonal-invariant tolerance. |
| `nacme_policy_abs_tol` | `1.0e-4` au⁻¹ | Absolute comparison tolerance. |
| `nacme_policy_rel_tol` | `1.0` | Relative comparison tolerance. |
| `nacme_policy_consecutive` | `3` | Consecutive reference-comparison failures required by `error`. |

Use `warn` while establishing appropriate thresholds for a molecular system.
`error` can terminate a trajectory and should be used only after that
assessment.

## NVE Energy Diagnostics

| Keyword | Default | Meaning |
| --- | --- | --- |
| `nve_policy` | `warn` | `off`, `warn`, or `error` response to NVE energy criteria. |
| `nve_policy_abs_tol` | `5.0e-3` Ha | Total drift from the initial NVE energy. |
| `nve_policy_step_tol` | `1.0e-3` Ha | Change between adjacent recorded steps. |
| `nve_policy_transition_tol` | `1.0e-6` Ha | Residual across a hop or trivial crossing after its energy-conserving adjustment. |
| `nve_policy_consecutive` | `3` | Consecutive drift or step failures required by `error`. |

`nve_policy=warn` is the default and does not terminate the trajectory.
`nve_policy=error` terminates immediately for a failed transition-energy
criterion or after the configured number of consecutive drift/step failures.
This policy is independent of case-D substepping.

## Additional Diagnostics

| Keyword | Default | Meaning |
| --- | --- | --- |
| `first_hop_step` | `1` | First interval in which a stochastic hop can be accepted. |
| `trivial` | `False` | Enable overlap-triggered trivial-crossing following. |
| `trivial_thresh` | `0.5` | State-overlap criterion for that optional treatment. |

Trivial-crossing following is a separate approximation and is not enabled by
the four continuity treatments.

