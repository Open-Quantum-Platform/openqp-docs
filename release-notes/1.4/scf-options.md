# SCF options

## `orbital_hessian_check`

**Separate development candidate.** This option is under validation and is
unavailable on the current 1.4 release branch.

| Field | Value |
| --- | --- |
| Type | Boolean |
| Default | `false` |
| Applied at | SOSCF in the SCF escalation sequence |

Set `orbital_hessian_check=true` to request a lowest-curvature check of the orbital
Hessian when the SCF escalation reaches an eligible SOSCF stage. The check
uses additional orbital Hessian products and increases the cost of that
stage. With the default `false`, the calculation follows the standard SCF
convergence criteria. A near-stalled RHF or UHF SOSCF escalation can also
probe for a downhill orbital rotation. If such a rotation is accepted, SOSCF
resumes and checks the relaxed solution after it converges.

The option is incompatible with fractional occupations (`pfon`), maximum
overlap (`mom`), restricted orbital rotations (`rstctmo`), and C₃-constrained
ROHF. The log reports `SOSCF orbital-Hessian probe calls=N`. A count of zero
means that no eligible SOSCF stage was reached, as when the primary
converger succeeds.

```text
roks/bhhlyp/cc-pvdz mult=3 energy
geom="triplet.xyz"
scf(escalation=soscf,orbital_hessian_check=true)
```

For legacy input, use `orbital_hessian_check=true` in the `[scf]` section. In the
Python SDK, set `job.scf.orbital_hessian_check = True`.

The `orbital_hessian_check` option applies to the SOSCF escalation stage.
[`stability`](keywords/scf.md#stability)
requests a separate stability analysis of the converged SCF reference.
