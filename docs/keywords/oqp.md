# `[oqp]`

The `[oqp]` section stores controls for the native OpenQP optimizer in
traditional sectioned `.inp` input and the internal configuration assembled by
the concise parser. In a concise `.oqp` file, write native geometry controls in
the primary driver, for example `opt(coordsys=dlc,trust=0.1)`, never as a
separate `oqp(...)` call. Traditional sectioned `.inp` files may still select
the native engine explicitly with `[optimize] lib=oqp`.

## Keywords

### `coordsys`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Used by | native optimizer coordinates |

Coordinate system for the native optimizer. `auto` selects delocalized internal
coordinates (DLC) for minimum, TS, MECI, MECP, and TCI calculations. MEP and IRC
use their mass-weighted path coordinates, and NEB uses its Cartesian FIRE band;
these three path drivers do not read `coordsys`. The DLC basis must span the
complete molecular vibrational space (`3N-6` for a non-linear isolated system);
otherwise OpenQP uses its safer coordinate-recovery sequence. Molecular
complexes are supplemented with interfragment distances when their primitive
internal-coordinate metric is poorly conditioned. Explicit `tric`, `ric`, and
Cartesian selections remain available as expert overrides.

For QST2/QST3, distinct Cartesian endpoints may coincide in the selected
internal coordinates, as in NH3 inversion. The engine then switches to Cartesian
coordinates before initializing the model Hessian and reports the fallback in
its coordinate label, for example `DLC->CART(fallback)`. This check applies to
`auto` and explicit internal-coordinate selections. See
[QST coordinate selection](../workflows/transition-state-search.md#coordinate-selection-and-inversion-endpoints).

### `trust`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.2` |
| Used by | optimizer trust radius |

Initial trust radius.

### `trust_max`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | optimizer trust radius |

Maximum trust radius.

### `auto_recovery`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | native minimum, crossing-point, and TS optimizers |

Enables the native optimizer's coordinate and trust-radius recovery attempts
after an initial optimization attempt does not converge. In concise input,
place it in the primary driver, for example `opt(auto_recovery=false)`.

### `recovery_maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `30` |
| Used by | native optimizer recovery |

Minimum iteration allowance for a recovery attempt. The value must be
positive. In concise input, write it in `opt`, `meci`, `mecp`, `tci`, or `ts`.

### `recovery_trust`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.02` |
| Used by | native optimizer recovery |

Initial trust radius for a recovery attempt. The value must be finite and
positive; the optimizer limits it against `trust_max`. In concise input, write
it in `opt`, `meci`, `mecp`, `tci`, or `ts`.

### `freeze`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | native constrained minimum optimization |

Freezes each listed atom-pair distance at its value in the input geometry.
Indices are one-based. Use `distance(i,j)` or the short `r(i,j)` spelling, and
separate multiple pairs with semicolons:

```ini
[oqp]
freeze=distance(1,2);distance(2,3)
```

In concise input, place the same expression directly in `opt(...)`, for example
`opt(S0,freeze="distance(1,2)")`. Current native constraints are limited to
frozen distances and minimum searches.

### `follow`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | mode following |

Mode-following selector for transition-state style steps.

### `init_hessian`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `model` |
| Values | `model`, `numerical`, `analytical` |
| Used by | native transition-state optimization |

Initial Hessian policy for native P-RFO transition-state searches. `model`
uses the inexpensive internal-coordinate model Hessian. `numerical` and
`analytical` calculate a real Cartesian Hessian for the selected state before
the first TS step. In concise input, use
`ts(S0,hessian=model|numerical|analytical)`.

### `spring`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.05` |
| Used by | NEB |

NEB spring constant.

### `climb`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | NEB |

Enables climbing-image NEB behavior.

### `fmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `2.0e-3` |
| Used by | NEB convergence |

NEB force threshold.

### `frms`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `2.0e-3` |
| Used by | NEB convergence |

RMS force threshold over all movable NEB images. A native band converges only
when both `fmax` and `frms` are satisfied.

### `climb_fmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.05` |
| Used by | climbing-image NEB activation |

Relax-then-climb threshold. Native NEB enables its climbing image after the
ordinary band maximum force falls below this value. When `climb=True`, it must
be greater than or equal to `fmax`; otherwise the ordinary band could satisfy
the final threshold before climbing-image activation.

### `neb_dt`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | NEB propagation |

NEB FIRE integration step. Concise `.oqp` accepts `dt` as the preferred public
spelling and lowers it to `neb_dt`.

### `maxmove`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.2` |
| Used by | NEB image updates |

Maximum NEB image displacement per step.

### `align`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | NEB endpoint preparation |

Rigidly aligns the product endpoint to the reactant with a proper Kabsch
rotation before interpolation, removing overall translation and rotation.

### `opt_ends`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | NEB endpoints |

Optimizes NEB endpoints when true.

### `end_fmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-3` |
| Used by | NEB endpoint convergence |

Endpoint force threshold.

### `neb_output`

| Field | Value |
| --- | --- |
| Type | string (path) |
| Default | empty |
| Used by | NEB final-path output |

Path for the final multi-frame NEB XYZ file. Each frame includes the image
energy in Hartree. If empty, OpenQP writes `<project>_neb.xyz` in the log
directory. Concise `.oqp` input uses the public spelling `output="path.xyz"`.

### `irc_step`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Used by | IRC |

IRC step size.

### `irc_direction`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `forward` |
| Used by | IRC |

IRC direction.

### `mep_step`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Used by | MEP |

MEP step size.

### `path_gtol`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-4` |
| Used by | native IRC and MEP convergence |

Euclidean-norm threshold on the mass-weighted gradient used to stop native IRC
and MEP path tracing. Concise `.oqp` exposes this value as `gtol`, for example
`irc(S0,gtol=1e-4)` or `mep(S0,gtol=1e-4)`.

### `ts_search`, `ts_product`, `ts_guess`

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `ts_search` | string | `prfo` | Native TS search: `prfo`, `qst2`, or `qst3` |
| `ts_product` | string | empty | Product XYZ for QST2/QST3; same atoms and order as reactant |
| `ts_guess` | string | empty | Approximate TS XYZ required by QST3 |

QST2/QST3 require `runtype=ts`, `lib=oqp`, and `init_hessian=model`.
They use only electronic energies and gradients. The reactant is the input
geometry. XYZ coordinates are Å; relative paths resolve from the input file.
In concise input write `ts(search="qst3",product="p.xyz",guess="g.xyz")`.
The default `coordsys=auto` handles inversion endpoints through automatic
Cartesian fallback when necessary; an explicit Cartesian override is not required.
See [transition-state searches](../workflows/transition-state-search.md).

### `neb_interpolation`

String, default `linear`. Selects `linear` or `idpp` initialization for native NEB.
In concise input write `neb(interpolation="idpp",...)`. IDPP uses interpolated
pair distances to prepare the band without electronic calculations. It supports
nonperiodic molecules only. Failed surrogate convergence prevents electronic NEB.
See [transition-state searches](../workflows/transition-state-search.md).
