# Molecular Dynamics

OpenQP uses three explicit input calls for dynamics:

- `md(...)` contains nuclear propagation, initial-condition, ensemble, and
  output settings.
- `namd(...)` adds excited-state propagation and surface hopping.
- `qmmm(...)` selects a QM/MM model. It does not replace either dynamics call.

Thus `md(...)` alone requests ground-state Born--Oppenheimer molecular
dynamics, while `namd(...) md(...)` requests nonadiabatic molecular dynamics
(NAMD). Add `qmmm(...)` to either form when a QM/MM calculation is intended.

## Dynamics Backend Selection

OpenMM is used for periodic systems and for nonperiodic QM/MM dynamics. The
native OpenQP molecular-dynamics integrator is used for gas-phase calculations
and for the explicitly selected spherical-boundary model.

| Calculation | Input form | Dynamics backend |
| --- | --- | --- |
| Gas-phase ground-state dynamics | `md(...)` | native OpenQP |
| Periodic ground-state dynamics | `md(...) qmmm(periodic=true,...)` | OpenMM |
| Nonperiodic QM/MM ground-state dynamics | `md(...) qmmm(...)` | OpenMM |
| Gas-phase NAMD | `namd(...) md(...)` | native OpenQP |
| QM/MM NAMD | `namd(...) md(...) qmmm(...)` | OpenMM environment with OpenQP QM forces |

## Minimal Inputs

Ground-state gas-phase dynamics:

```text
bhhlyp/6-31g* geom="molecule.xyz"
md(nstep=400,dt=0.5,velocity="molecule.vel",ensemble=nve)
```

Recommended MRSF-TDDFT NAMD:

```text
mrsf(nstate=4)/bhhlyp/6-31g* geom="molecule.xyz"
namd(S1,scheme=TDC_NAC)
md(nstep=400,dt=0.5,velocity="molecule.vel",ensemble=nve)
```

The default `continuity=on` activates the complete numerical-continuity
treatment described in [NAMD Numerical Continuity](md-continuity.md). It does
not need to be repeated in a standard input.

QM/MM NAMD:

```text
mrsf(nstate=4)/bhhlyp/6-31g* geom="system.xyz"
namd(S1,scheme=TDC_NAC)
md(nstep=400,dt=0.5,velocity="system.vel",ensemble=nve)
qmmm(pdb_file="system.pdb",forcefield_files="forcefield.xml",
     qm_atoms="0-12")
```

`TDC_NAC` and `NAC` are available for QM/MM NAMD under the documented
frozen-embedding-field QM-region NAC approximation and without link atoms.
See [NAC](nac.md) for its exact scope.

## Choose One NAMD `scheme`

Every concise `namd(...)` input requires one complete surface-hopping scheme.
The choice determines electronic-amplitude propagation, momentum-adjustment
direction, hop-gap ceiling, and the treatment of a frustrated directional hop.

| `scheme` | Electronic propagation | Successful-hop velocity adjustment | Hop-gap ceiling | Frustrated directional hop |
| --- | --- | --- | --- | --- |
| `BaeckAn` | lagged time-dependent Baeck--An coupling | isotropic | 10 kcal mol⁻¹ | unchanged |
| `Overlap` | overlap NPI TDC | isotropic | 10 kcal mol⁻¹ | unchanged |
| `TDC_NAC` | overlap NPI TDC | analytic NAC for the selected hop | 10 eV | reflect NAC-direction component |
| `NAC` | analytic NAC contracted with velocity | analytic NAC | 10 eV | reflect NAC-direction component |

`TDC_NAC` is the principal general setting: overlaps propagate the electronic
amplitudes, while the analytic derivative-coupling vector is evaluated for a
selected hop. `NAC` evaluates analytic couplings for electronic propagation as
well. Full definitions and `scheme=custom` are on
[NAMD Coupling Schemes](md-schemes.md).

## Essential Options

| Keyword | Default | Meaning |
| --- | --- | --- |
| `nstep` | `100` | Number of nuclear steps. |
| `dt` | `0.5` fs | Nuclear timestep. Total time is `nstep * dt`. |
| `velocity` | `maxwell` | `maxwell`, `zero`, or a velocity-file path. |
| `temperature` | `300.0` K | Maxwell--Boltzmann sampling temperature and NVT target. |
| `seed` | `0` → local `YYYYMMDD` | Random seed; set explicitly for a reproducible ensemble. |
| `rng_stream` | `1` | Independent counter-RNG stream or trajectory identifier. |
| `ensemble` | `nve` | Choose `nve` or `nvt`; `npt` is reserved but currently rejected. |
| `scheme` | required by `namd()` | One of the four schemes above or `custom`. |
| `active` | `1` | Initial active response state if no state label is supplied. |
| `continuity` | `on` | Complete A--D numerical-continuity treatment; use `manual` only for individual controls. |
| `decoherence` | `edc` | Energy-based decoherence; `off` disables it. |
| `nve_policy` | `warn` | Report NVE energy deviations without terminating the trajectory. |

## Core Keyword Definitions

### `nstep`

Positive integer number of nuclear steps. The requested propagation time is
`nstep * dt`; there is no separate `total_time` keyword.

### `dt`

Positive nuclear timestep in femtoseconds. Establish nuclear-time-step
convergence for the system and observable of interest.

### `active`

Initial active state, using the 1-based internal response-state index. A state
label in `namd(S1,...)` is clearer and takes precedence in concise input.

### `substep`

Number of electronic-amplitude integration substeps per nuclear step. Default:
`50000`. This does not change the nuclear timestep or total propagation time.

### `decoherence`

`edc` (default) applies the Granucci--Persico energy-based decoherence
correction. `off` disables decoherence for a controlled comparison.

### `edc_c`

Energy-based decoherence constant in Hartree. Default: `0.1` Ha. It is used
only with `decoherence=edc`.

## Grouped Reference Pages

The remaining options are separated by scientific purpose:

| Page | Contents |
| --- | --- |
| [NAMD Coupling Schemes](md-schemes.md) | `scheme`, `tdc`, `rescale`, `thrshe`, `frustrated`, Baeck--An controls, and optional trivial-crossing following |
| [NAMD Numerical Continuity](md-continuity.md) | Analytic-NAC cases A--D, `continuity=on|manual`, SCF/reference controls, retained-state criterion, substepping, and numerical energy correction |
| [NAMD Diagnostics](md-diagnostics.md) | NACME comparison and NVE energy criteria, including which `error` policies can terminate a run |
| [Initial Conditions and Restart](md-initial-restart.md) | velocity files and units, temperature, random streams, trajectory output, checkpoint restart, and local continuation |
| [Ensembles and SOC-NAMD](md-ensemble-soc.md) | NVE/NVT/NPT, OpenMM restrictions, adaptive timestep, SOC basis, initialization, and SOC force diagnostics |
| [NAMD Advanced Controls](md-advanced.md) | compact index of rarely changed settings and links to the detailed group pages |

## Sectioned `.inp` Compatibility

The concise input above is recommended. Legacy sectioned input places the same
runtime settings in `[md]`; `temperature` and `friction` correspond to
`init_temp`/`thermostat_temperature` and `thermostat_friction` where required
by the legacy spelling. The scientific meaning and defaults are the same.

Legacy `nacme_gate*` and `nve_gate*` names are accepted as aliases for
`nacme_policy*` and `nve_policy*`. New inputs should use `policy`. Do not specify
both spellings for the same setting.

## Python API

The Python API uses the same concise calls and keyword names as `.oqp` input.
For reproducible trajectory ensembles, set `seed` and give each trajectory a
different `rng_stream`. Restart files bind all trajectory-changing controls,
including `scheme`, `continuity`, and the manual A--D settings.
