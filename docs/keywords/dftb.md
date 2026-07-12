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

### `backend`, `type`, `parameter_path`, `library_path`, `executable`, `timeout`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `backend` | string | `native` | Adapter backend: `native`; `auto` currently selects the same native path, while `probe` is an explicit developer fallback. |
| `type` | string | `auto` | Ground/response family. Accepted legacy values include `ground`, `ground_noscc`, `tddftb`, `tda`, `sf`, and `mrsf`. |
| `parameter_path` | path | empty | `.opdftb` file or SKF parameter directory. `OPENQP_DFTB_PARAMETER_PATH` is the environment fallback. |
| `library_path` | path | empty | Explicit native shared-library path. `OPENQP_DFTB_LIBRARY` is the environment fallback; otherwise OpenQP checks the installed locator package and staged runtime library. |
| `executable` | path | empty | Probe executable when `backend=probe`. `OPENQP_DFTB_STATE_GRADIENT_PROBE` and then `PATH` provide fallbacks. |
| `timeout` | integer | `300` | Probe-subprocess timeout in seconds; must be positive. |

The native backend is required for state overlap, NAC/NACME, NAMD, SOC, and
controls that the probe executable cannot forward. The probe also rejects
nondefault target/reference multiplicities, per-channel `spc_*`, MRSF shifts,
LC ground-state handling, spin-completeness changes, and response/Z-vector
controls that its command line cannot represent.

## SCC Controls

### `scc_tolerance`, `scc_mixer`, `scc_mixing`, `scc_history`, `scc_max_step`, `max_scc_iterations`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `scc_tolerance` | float | `1.0e-8` | SCC convergence threshold; must be positive. |
| `scc_mixer` | string | `auto` | `auto`, `linear`, `anderson`, `pulay`, `broyden`, `diis`, `trust`, or `trah`. |
| `scc_mixing` | float | `0.35` | Population-vector mixing fraction in `(0,1]`. |
| `scc_history` | integer | `12` | Mixer history length; must be positive. |
| `scc_max_step` | float | `0.5` | Maximum SCC update; zero disables the cap. |
| `max_scc_iterations` | integer | `1200` | Maximum SCC iterations; must be positive. |

## Response Controls

### `response_tolerance`, `response_max_iterations`, `response_max_subspace`, `response_solver`, `zvector`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `response_tolerance` | float | `1.0e-6` | Response-solver convergence threshold. |
| `response_max_iterations` | integer | `50` | Maximum response iterations. |
| `response_max_subspace` | integer | `100` | Maximum iterative-solver subspace. |
| `response_solver` | string | `auto` | `auto`, `dense`, or `davidson`. |
| `zvector` | boolean | `True` | Enable the relaxed Z-vector response where supported. |

## Spin, Range Separation, and MRSF Controls

### `spc`, `spc_coco`, `spc_ovov`, `spc_coov`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `spc` | float | `0.5` | MRSF spin-pair coupling. `-1` inherits the CAM exchange fraction. |
| `spc_coco` | float | `-999.0` | Closed-open/closed-open channel override; the sentinel inherits global `spc`. |
| `spc_ovov` | float | `-999.0` | Occupied-virtual channel override; the sentinel inherits global `spc`. |
| `spc_coov` | float | `-999.0` | Mixed channel override; the sentinel inherits global `spc`. |

### `omega`, `cam_alpha`, `cam_beta`, `lc_gamma`, `lc_ground_state`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `omega` | float | `0.3` | Range-separation parameter; must be non-negative. |
| `cam_alpha` | float | `0.0` | Short-range CAM exchange coefficient. |
| `cam_beta` | float | `1.0` | Long-range CAM increment. |
| `lc_gamma` | string | `yukawa` | Long-range gamma kernel: `yukawa` or `erf`. |
| `lc_ground_state` | boolean | `False` | Apply the long-range correction to the ground-state SCC problem. |

### `spin_complete`, `reference_multiplicity`, `target_multiplicity`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `spin_complete` | boolean | `True` | Use the spin-complete response construction where supported. |
| `reference_multiplicity` | integer | `0` | Auto reference multiplicity: `3` for SF/MRSF and `1` otherwise. The `.oqp` route owns it. |
| `target_multiplicity` | integer | `1` | Legacy response multiplicity, currently singlet `1` or triplet `3`; the `.oqp` state label owns it. |

### `mrsf_shift_oo`, `mrsf_shift_co`, `mrsf_shift_ov`, `mrsf_shift_cv`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `mrsf_shift_oo` | float | `0.0` | MRSF occupied-occupied block shift. |
| `mrsf_shift_co` | float | `0.0` | MRSF closed-open block shift. |
| `mrsf_shift_ov` | float | `0.0` | MRSF occupied-virtual block shift. |
| `mrsf_shift_cv` | float | `0.0` | MRSF closed-virtual block shift. |

DFTB does not consume Gaussian-basis SCF property analyses or PCM. Available
workflow combinations also depend on the DFTB response type and backend; rely
on input validation rather than assuming every all-electron workflow is wired.
