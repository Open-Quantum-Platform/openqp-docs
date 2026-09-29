# Ensembles and SOC-NAMD

## Nuclear Ensemble

### `ensemble`

| Value | Current support |
| --- | --- |
| `nve` | Default; no thermostat after the initial velocity is prepared. |
| `nvt` | Langevin thermostat at `temperature` with damping `friction`. |
| `npt` | Reserved but currently rejected. |

NPT requires a QM/MM energy evaluation for every barostat trial box. The
current ESPF-QM/MM driver does not provide that trial-box energy, so OpenQP
rejects `ensemble=npt` rather than performing an invalid NPT simulation.

`friction` is in ps⁻¹ and defaults to `1.0`; it must be positive for NVT. The
legacy `thermostat` keyword accepts `off` or `langevin` and maps to
`ensemble=nve` or `ensemble=nvt`. In legacy `[md]` input, the corresponding
scalar names are `init_temp`, `thermostat_temperature`, and
`thermostat_friction` (default `1.0` ps⁻¹).

The NVE energy criteria are documented separately under
[NAMD Diagnostics](md-diagnostics.md). They do not apply to thermostat energy
exchange in NVT.

## Adaptive Nuclear Timestep

| Keyword | Default | Meaning |
| --- | --- | --- |
| `dt_adaptive` | `False` | Reduce the timestep when the displacement criterion requires it. |
| `dt_min` | `0.05` fs | Smallest allowed adaptive timestep. |
| `dx_max` | `0.02` bohr | Largest accepted per-step atomic displacement. |

Adaptive stepping is a separate integration option. Case-D energy-triggered
substepping repeats one nominal interval from the same phase point and is
documented under [NAMD Numerical Continuity](md-continuity.md).

## SOC-NAMD

### `soc`

Default: `False`. `soc=True` enables surface hopping with spin--orbit coupling
among `ns` singlets and `nt` triplets. Each triplet contributes three
\(M_S\) sublevels, giving `ns + 3*nt` MCH basis functions before
spin-adiabatic transformation.

### `soc_basis`

| Value | Meaning |
| --- | --- |
| `adiabatic` | Propagate spin-adiabatic SOC eigenstates; the force uses the weighted-MCH approximation. |
| `mch` | Propagate the spin-pure MCH basis with the active-root MCH gradient. |

Default: `adiabatic`. The `mch` form is recommended for current production
calculations because it avoids the approximate weighted force of the
spin-adiabatic implementation.

### `init_state`

Optional zero-based MCH character label such as `S0`, `S1`, `T0`, or `T1`.
It selects the initial spin-adiabatic state with the largest matching MCH
character and overrides `active` in an SOC calculation.

### Spin-adiabatic force diagnostics

| Keyword | Default | Meaning |
| --- | --- | --- |
| `grad_wthr` | `0.001` | Minimum MCH weight included in the weighted diagonal gradient. |
| `soc_du_dt_corr` | `False` | Add a finite-difference eigenvector-change correction. |
| `soc_tdc_grad_corr` | `False` | Add an approximate TDC-projected gradient correction. |
| `econs` | `False` | Rescale every step as a temporary energy-drift stabilizer. |

These controls examine the approximate spin-adiabatic force and are not needed
for `soc_basis=mch`. `econs` is not a substitute for a physically consistent
force and should remain off unless a documented diagnostic requires it.

## QM/MM SOC-NAMD

Adding `qmmm(...)` selects the corresponding SOC-QM/MM driver. See
[SOC-NAMD-QMMM](../workflows/soc-namd-qmmm.md) for the dispatch table and the
current force and coupling approximations.
