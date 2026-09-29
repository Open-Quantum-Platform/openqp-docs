# NAMD Advanced Controls

This page collects controls that are not needed in a standard NAMD input.
Start with the four named [`scheme`](md.md#scheme-oqp-and-python-api) values in
the main [`[md]` manual](md.md). Add an option from this page only when the
chosen physical treatment, diagnostic comparison, or restart procedure
requires it.

## Custom Surface-Hopping Scheme

Use `scheme=custom` only when none of the four named schemes represents the
intended calculation. All four low-level choices are then required:

| Keyword | Meaning | Allowed values |
| --- | --- | --- |
| `tdc` | time-derivative coupling used to propagate electronic amplitudes | `fd`, `npi`, `analytic`, `baeck_an` |
| `rescale` | direction used to adjust nuclear velocity after an allowed hop | `auto`, `isotropic`, `analytic_nac`, `hop_analytic_nac` |
| `thrshe` | maximum energy gap for a hop attempt, in Hartree | positive number |
| `frustrated` | treatment of a directional hop with insufficient kinetic energy | `none`, `reflect` |

The four named schemes expand as follows:

| `scheme` | `tdc` | `rescale` | `thrshe` | `frustrated` |
| --- | --- | --- | --- | --- |
| `BaeckAn` | `baeck_an` | `isotropic` | `0.015936` | `none` |
| `Overlap` | `npi` | `isotropic` | `0.015936` | `none` |
| `TDC_NAC` | `npi` | `hop_analytic_nac` | `0.367493` | `reflect` |
| `NAC` | `analytic` | `analytic_nac` | `0.367493` | `reflect` |

Do not combine a named scheme with any of the four low-level keywords. A
custom scheme must state all four explicitly:

```text
namd(S1,scheme=custom,tdc=npi,rescale=isotropic,
     thrshe=0.367493,frustrated=reflect)
md(nstep=400,dt=0.5,velocity="molecule.vel")
```

SOC-NAMD and QM/MM NAMD do not support the analytic-NAC rescaling required by
`TDC_NAC` or `NAC`. A defined overlap/isotropic custom scheme is therefore
written explicitly, for example:

```text
namd(scheme=custom,tdc=npi,rescale=isotropic,
     thrshe=0.367493,frustrated=reflect,
     soc=true,soc_basis=mch,init_state=S1)
md(nstep=400,dt=0.5)
```

## Diagnostic and Numerical Controls

| Purpose | Keywords and defaults |
| --- | --- |
| Decoherence parameter | `decoherence=edc`, `edc_c=0.1` Ha |
| Baeck--An or analytic-NACME comparison | `nacme_check=off`, `ba_gap_max=0.0734986443513` Ha, `nacme_policy=off` |
| NACME comparison criteria | `nacme_policy_invariant_tol=1.0e-10`, `nacme_policy_abs_tol=1.0e-4` au⁻¹, `nacme_policy_rel_tol=1.0`, `nacme_policy_consecutive=3` |
| NVE energy criteria | `nve_policy_abs_tol=5.0e-3` Ha, `nve_policy_step_tol=1.0e-3` Ha, `nve_policy_transition_tol=1.0e-6` Ha, `nve_policy_consecutive=3` |
| Delayed hopping or trivial-crossing following | `first_hop_step=1`, `trivial=False`, `trivial_thresh=0.5` |
| Electronic propagation resolution | `substep=50000` |

Use `nacme_policy=warn` or `nve_policy=warn` to print the corresponding
diagnostic result without terminating the trajectory. Use `error` only after
the relevant numerical thresholds have been established for the molecular
system and timestep.

## Electronic-Structure Continuity

| Purpose | Keywords and defaults |
| --- | --- |
| Reuse the preceding SCF solution | `mo_reuse=True`, `scf_guess_retry=True` |
| Failed continuation SCF calculation | `scf_fail=escalate` |
| Follow the two-SOMO reference | `ref_follow=soscf`, `somo_tol=0.5` |
| Energy treatment at a reference change | `ref_switch_rescale=True` |
| Non-hop energy discontinuity | `disc_rescale=True`, `disc_tol=0.002` Ha, `disc_substeps=10`, `econs=False` |

These settings control numerical continuity of the electronic-structure
calculation. They do not define a different surface-hopping scheme.

## Output, Restart, and Continuation

| Purpose | Keywords and defaults |
| --- | --- |
| Packed trajectory output | `trajectory_interval=1`; `trajectory_file` derived from the project name |
| Atomic checkpoint | `restart_interval=10`; `restart_file` derived from the project name |
| Restart the same calculation | `restart=False`; normally run the generated `.namd.restart.oqp` file |
| Continue into new output files | `continuation_checkpoint`, `continuation_trajectory` empty by default |

Local continuation with a changed timestep is restricted to fixed-step,
same-spin `NAC` dynamics. The new timestep cannot exceed the timestep stored in
the source checkpoint.

## NVT and SOC-Specific Controls

| Purpose | Keywords and defaults |
| --- | --- |
| Langevin NVT | `md(ensemble=nvt,temperature=300.0,friction=1.0)` |
| SOC initial MCH character | `init_state` empty by default |
| SOC force diagnostics | `soc_du_dt_corr=False`, `soc_tdc_grad_corr=False`, `grad_wthr=0.001` |
| Adaptive SOC timestep | `dt_adaptive=False`, `dt_min=0.05` fs, `dx_max=0.02` bohr |

With the default `velocity=maxwell`, OpenQP samples initial velocities at
`temperature=300.0` K even for NVE dynamics. `temperature` does not alter a
velocity read from a file or set to zero; with `ensemble=nvt`, the same
value is the NVT target. The sectioned `.inp` compatibility names are
`init_temp`, `thermostat_temperature`, and `thermostat_friction`.

## Detailed Definitions

The complete type, range, and physical meaning of each keyword remain in the
[`[md]` keyword reference](md.md#standard-keyword-reference). This page is the
short index for deciding whether an advanced control is needed.
