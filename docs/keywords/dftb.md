# `[dftb]`

The `[dftb]` section configures the optional OpenQP-DFTB adapter. In one-line
`.oqp` input, prefer the routes `dftb`, `dftb0`, `tddftb(...)`,
`tda-tddftb(...)`, `sf-tddftb(...)`, and `mrsf-tddftb(...)`, then put only
backend-specific controls in `dftb(...)`.

```text
mrsf-tddftb(nstate=3) geom="h2o.xyz" grad(S1) dftb(parameter_path="params.opdftb")
```

The route owns `type`, `reference_multiplicity`, and `target_multiplicity` in
`.oqp`. Those keys remain available to traditional `.inp` files.

## Backend and Parameter Source

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `backend` | string | `native` | Adapter backend: `auto`, `native`, or the developer fallback `probe`. |
| `type` | string | `auto` | Ground/response family. Accepted legacy values include `ground`, `ground_noscc`, `tddftb`, `tda`, `sf`, and `mrsf`. |
| `parameter_path` | path | empty | `.opdftb` file or SKF parameter directory. `OPENQP_DFTB_PARAMETER_PATH` is the environment fallback. |
| `library_path` | path | empty | Explicit native OpenQP-DFTB shared-library path. |
| `executable` | path | empty | Explicit probe executable when `backend=probe`. |
| `timeout` | integer | `300` | Probe/backend timeout in seconds; must be positive. |

The native backend is required for state overlap, NAC/NACME, NAMD, SOC, and
controls that the probe executable cannot forward.

## SCC Controls

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `scc_tolerance` | float | `1.0e-8` | SCC convergence threshold; must be positive. |
| `scc_mixer` | string | `auto` | `auto`, `linear`, `anderson`, `pulay`, `broyden`, `diis`, `trust`, or `trah`. |
| `scc_mixing` | float | `0.35` | Population-vector mixing fraction in `(0,1]`. |
| `scc_history` | integer | `12` | Mixer history length; must be positive. |
| `scc_max_step` | float | `0.5` | Maximum SCC update; zero disables the cap. |
| `max_scc_iterations` | integer | `1200` | Maximum SCC iterations; must be positive. |

## Response Controls

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `response_tolerance` | float | `1.0e-6` | Response-solver convergence threshold. |
| `response_max_iterations` | integer | `50` | Maximum response iterations. |
| `response_max_subspace` | integer | `100` | Maximum iterative-solver subspace. |
| `response_solver` | string | `auto` | `auto`, `dense`, or `davidson`. |
| `zvector` | boolean | `True` | Enable the relaxed Z-vector response where supported. |

## Spin, Range Separation, and MRSF Controls

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `spc` | float | `0.5` | MRSF spin-pair coupling. `-1` inherits the CAM exchange fraction. |
| `spc_coco` | float | `-999.0` | Closed-open/closed-open channel override; sentinel uses the backend default. |
| `spc_ovov` | float | `-999.0` | Occupied-virtual channel override. |
| `spc_coov` | float | `-999.0` | Mixed channel override. |
| `omega` | float | `0.3` | Range-separation parameter; must be non-negative. |
| `cam_alpha` | float | `0.0` | Short-range CAM exchange coefficient. |
| `cam_beta` | float | `1.0` | Long-range CAM increment. |
| `lc_gamma` | string | `yukawa` | Long-range gamma kernel: `yukawa` or `erf`. |
| `lc_ground_state` | boolean | `False` | Apply the long-range correction to the ground-state SCC problem. |
| `spin_complete` | boolean | `True` | Use the spin-complete response construction where supported. |
| `reference_multiplicity` | integer | `0` | Legacy DFTB reference multiplicity; the `.oqp` route owns it. |
| `target_multiplicity` | integer | `1` | Legacy response multiplicity, currently singlet `1` or triplet `3`; the `.oqp` state label owns it. |
| `mrsf_shift_oo` | float | `0.0` | MRSF occupied-occupied block shift. |
| `mrsf_shift_co` | float | `0.0` | MRSF closed-open block shift. |
| `mrsf_shift_ov` | float | `0.0` | MRSF occupied-virtual block shift. |
| `mrsf_shift_cv` | float | `0.0` | MRSF closed-virtual block shift. |

DFTB does not consume Gaussian-basis SCF property analyses or PCM. Available
workflow combinations also depend on the DFTB response type and backend; rely
on input validation rather than assuming every all-electron workflow is wired.
