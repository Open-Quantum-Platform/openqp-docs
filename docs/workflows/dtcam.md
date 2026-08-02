# DTCAM-TB

**DTCAM-TB** is the tuned MRSF-TDDFTB operator of the OpenQP-DFTB library: a
plain DFTB2 ground-state reference combined with an *independent*
long-range-corrected response kernel, a rescaled spin-magnetization kernel, and
a small response-only one-center exchange term. It restores the relative
ordering of ionic-bright and covalent-dark ππ\* states that the conventional
LC-DFTB protocol inverts, so S₁/S₂ crossings, seams, and excited-state minima
come out at MRSF-TDDFT quality but at tight-binding cost.

You never spell the operator out. It is selected as a named preset with
[`[dftb] model=dtcam`](../keywords/dftb.md), and the parameter vector is
resolved inside `libopenqp_dftb_c` so an input can never drift from the
published values. This page is the DTCAM-TB task manual; the response
formalism itself is documented under [MRSF-TDDFTB](mrsf-tddftb.md) and the
complete key list under [`[dftb]`](../keywords/dftb.md).

!!! warning "External library and development preview"
    The DFTB method is provided by the optional **OpenQP-DFTB** library
    ([`openqp-dftb`](https://github.com/Open-Quantum-Platform/openqp-dftb),
    loaded via `ctypes`); build it from source or build OpenQP with
    `-DENABLE_OPENQP_DFTB=ON` (see the [`[dftb]` reference](../keywords/dftb.md)
    for the full build and library-discovery note). The integration is tracked
    in OpenQP PR [#266](https://github.com/Open-Quantum-Platform/openqp/pull/266)
    and is not part of OpenQP 1.2.0. The one-line `.oqp` format is likewise a
    development-branch input style (see [One-line `.oqp`](../oqp-input.md)).

## Operator presets

`[dftb] model` names a complete, published operator **and** its numerical
protocol (mixer, SCC budget and tolerance, response solver, gradient path).

| `model=` | Legacy aliases (still accepted) | What it is |
| --- | --- | --- |
| `dtcam` | `dtcam-tb`, `dtcam_tb`, `dtcamtb` | The production MRSF-TDDFTB operator (the DTCAM-TB method). Plain DFTB2 reference (no long-range term at all); independent erf response kernel; response-only one-center *pp* exchange that lowers the covalent 2¹A_g⁻. **Default for MRSF.** |
| `dtcam2` / `dtcam-erf` | `dtcam-tb2`, `dtcam_tb2`, `dtcamtb2`, `dtcam-tb-erf`, `dtcam_tb_erf`, `dtcamtberf` | Refit variant: explicit erf response kernel, softened long-range response weight, one-center exchange switched off. Use it only when reproducing that refit. |
| `ob2` | `dftb+`, `dftbplus`, `dftb_plus` | The conventional OB2 / LC-DFTB2 protocol: LC-DFTB2 ground state with the Yukawa–Slater kernel, full long-range exchange, official shell-resolved spin constants, and the DFTB+ program's numerical defaults (SCC tolerance 1e-5, Broyden 0.2, 100 SCC iterations). Use it to compare against the DFTB+ program or against literature LC-DFTB numbers. **Default for SF-TDDFTB and open-shell ground-state runs.** |
| *(opt out)* | `none` | Disables the preset default and returns to the explicit-keys route. |

!!! note "Keyword rename"
    `dtcam` and `ob2` are the canonical names. The former spellings
    `dtcam-tb` and `dftb+` remain **accepted aliases**, so existing inputs
    keep working unchanged. `dftb+` was renamed because DFTB+ is a separate
    program; this preset is a parameter/protocol choice (OB2), not that
    program.

### Defaults when `model=` is omitted

| Route | Effective model |
| --- | --- |
| MRSF-TDDFTB (`[dftb] type=mrsf`) | `dtcam` |
| SF-TDDFTB, open-shell ground state (`reference_multiplicity > 1`) | `ob2` |
| Closed-shell ground state, TD-DFTB, DFTB0 | *(preset-free)* — LC-DFTB2 is not implemented for the restricted reference |

An MRSF run therefore already uses DTCAM-TB; writing `model=dtcam`
explicitly is the recommended, self-documenting form. Tuning **any**
preset-locked key also disables the default, so legacy inputs keep meaning
exactly what they said.

### A preset is all-inclusive

Combining `model=` with an individual operator key is rejected at input time,
because the preset would silently overwrite it:

```text
1. [ERROR] dftb.model: A model preset fixes the complete operator and numerical
   protocol; individual operator keys cannot be combined with it.
   current: 'omega'
   expected: model=dtcam with no tuned operator keys
   fix: Remove the listed [dftb] keys or drop model= to tune manually.
```

The locked keys are `omega`, `cam_alpha`, `cam_beta`, `lc_gamma`,
`lc_ground_state`, `w_scale`, `response_w_scale`, `response_omega`,
`response_cam_alpha`, `response_cam_beta`, `c_mrsf`, `c_mrsf_oo`,
`response_global_hybrid`, `onsite_exchange_scale`, `spc`, `spc_coco`,
`spc_ovov`, `spc_coov`, `onsite_ss`, `onsite_sp`, `onsite_pp`, the four
`mrsf_shift_*`, and the numerical block `scc_mixing`, `scc_history`,
`scc_max_step`, `scc_tolerance`, `max_scc_iterations`, `response_solver`,
`zvector`.

[`scc_mixer`](../keywords/dftb.md) is deliberately **not** locked: choosing the
first-try convergence algorithm is a numerical recovery decision, and an
explicit `scc_mixer` is applied after the preset is loaded. Keys the preset does
not touch — `response_tolerance`, `response_max_iterations`,
`response_max_subspace`, `nstate`, `print_level` — also stay user-tunable.

Presets require [`backend=native`](../keywords/dftb.md#backend); the probe
fallback cannot carry them.

## State numbering

This is the single easiest thing to get wrong.

MRSF relabels its **lowest singlet response root as `S0`**. Every state
selector in the `.inp` format — [`[properties] grad`](../keywords/properties.md),
[`[optimize] istate`](../keywords/optimize.md), `jstate`, `kstate`, and the
`states` list — is **1-based over the physical states**:

| Selector value | Physical state |
| --- | --- |
| `1` | `S0` |
| `2` | `S1` |
| `3` | `S2` |

So `grad=2` is the `S1` gradient, `istate=2` optimizes the `S1` minimum, and
`states=2,3` searches the `S1`/`S2` crossing. The one-line `.oqp` format takes
the physical labels `S0`, `S1`, `S2`, `T0`, … directly and needs no
translation.

`[tdhf] nstate` counts response roots the same way, so `nstate=3` gives you
`S0`, `S1`, `S2`.

## Parameters

Nothing needs configuring with a current `openqp-dftb` install: it ships the
bundled OB2W0PT3 Slater–Koster set (official `spinw.txt` included), which is
resolved automatically when `[dftb] parameter_path` is empty and
`OPENQP_DFTB_PARAMETER_PATH` is unset. Point either at another `.opdftb` file
or SKF directory to override the bundled default. As with every DFTB family,
`basis=` is an ignored placeholder that must nevertheless be present, and
`functional=` is empty.

## Single point and excited-state energies

One MRSF-TDDFTB response gives `S0`, `S1`, `S2`, their oscillator strengths,
and the state-to-state spectrum.

**`.inp`**

```ini
[input]
system=butadiene.xyz
charge=0
runtype=energy
method=dftb

[scf]
type=rohf
multiplicity=3

[dftb]
model=dtcam
type=mrsf
parameter_path=

[tdhf]
type=mrsf
nstate=3
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3)
energy(S0)
dftb(model=dtcam)
geom="butadiene.xyz"
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="dtcam_energy")
job.molecule("butadiene.xyz", charge=0)
job.dftb(response_type="mrsf", nstate=3, model="dtcam")
job.workflow.energy()
job.run()
```

For s-*trans* butadiene this puts the bright ionic 1¹B_u⁺ below the dark
covalent 2¹A_g⁻ at the Franck–Condon point (`S1` carries the oscillator
strength). Swapping to `model=ob2` inverts that ordering — `S1` becomes dark
and `S2` bright — which is exactly the failure DTCAM-TB was fitted to remove.
Run both if you want to see it.

## Analytic excited-state gradient

Gradients are analytic and use the relaxed Z-vector formulation (a single
pair-space solve). `S1` is selector `2`:

**`.inp`**

```ini
[input]
system=butadiene.xyz
charge=0
runtype=grad
method=dftb

[scf]
type=rohf
multiplicity=3

[dftb]
model=dtcam
type=mrsf
parameter_path=

[tdhf]
type=mrsf
nstate=3

[properties]
grad=2
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3)
grad(S1)
dftb(model=dtcam)
geom="butadiene.xyz"
```

**Python**

```python
job.dftb(response_type="mrsf", nstate=3, model="dtcam")
job.workflow.gradient(state=2)
```

Use `grad=1` / `grad(S0)` for the ground-state gradient.

## Geometry optimization

Ground state and excited state use the same deck; only `istate` changes
(`1` = `S0`, `2` = `S1`).

**`.inp`**

```ini
[input]
system=butadiene.xyz
charge=0
runtype=optimize
method=dftb

[scf]
type=rohf
multiplicity=3

[dftb]
model=dtcam
type=mrsf
parameter_path=

[tdhf]
type=mrsf
nstate=3

[optimize]
lib=oqp
istate=2
maxit=50
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3)
opt(S1,maxit=50)
dftb(model=dtcam)
geom="butadiene.xyz"
```

**Python**

```python
job.dftb(response_type="mrsf", nstate=3, model="dtcam")
job.workflow.optimize(istate=2, maxit=50)
```

`istate=1` optimizes the `S0` minimum. `lib=geometric` switches to the external
geomeTRIC optimizer; `lib=oqp` (the default) is the built-in native optimizer
and is the one the recovery behaviour described below applies to.

## MECI search

DFTB supplies MRSF-TDDFTB state energies and analytic gradients, so
minimum-energy conical-intersection searches run through the shared
[`[optimize]`](../keywords/optimize.md) machinery with `runtype=meci` — there is
no separate DFTB entry point. Because MRSF has the correct S₀/S₁ intersection
topology, DTCAM-TB is the DFTB operator to use for conical intersections.

`[optimize] meci_search` accepts `auto` (the default), `auglag`, `penalty`,
`ubp`, `hybrid`, and `baeka`. For two states `auto` runs the augmented
Lagrangian and escalates to BaekA only if that does not meet the convergence
criteria; with three or more states it selects BaekA directly.

### Two-state seam: S₁/S₀ of ethylene

Two-state searches address the roots with `istate`/`jstate`:

```ini
[input]
system=
   6   0.000000   0.000000   0.669500
   6   0.000000   0.000000  -0.669500
   1   0.928900   0.000000   1.232100
   1  -0.928900   0.000000   1.232100
   1   0.000000   0.928900  -1.232100
   1   0.000000  -0.928900  -1.232100
charge=0
runtype=meci
method=dftb

[scf]
type=rohf
multiplicity=3

[dftb]
model=dtcam
type=mrsf
parameter_path=

[tdhf]
type=mrsf
nstate=3

[optimize]
lib=oqp
istate=1
jstate=2
meci_search=baeka
energy_gap=1e-4
maxit=30
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3)
meci(S0,S1,algorithm=baeka,gap=1e-4,maxit=30)
dftb(model=dtcam)
geom="ethylene_twisted.xyz"
```

The S₁/S₀ seam of ethylene lies in the twisted-pyramidalized region, far from
the planar minimum, so start from a ~90° twisted structure. The values above are
deliberately capped for a quick run; for production raise `maxit` (~500) and keep
the default `energy_gap=1e-5`.

### The BaekA algorithm, and why `pen_sigma` matters

BaekA (Baek, Lee, Filatov, Choi, *J. Phys. Chem. A* **2021**, *125*, 1994) is an
adaptive-penalty algorithm over an ordered, consecutive list of same-spin roots.
Its objective over the selected states is

$$
F_N \;=\; \frac{1}{N}\sum_i E_i \;+\; \sigma \sum_i
\frac{(E_{i+1}-E_i)^2}{E_{i+1}-E_i+\alpha}
$$

with $\sigma$ = [`pen_sigma`](../keywords/optimize.md) and $\alpha$ =
`pen_alpha` (a smoothing energy; the schema default `0` is a sentinel that maps
to 0.02 Hartree for BaekA). Only *adjacent* gaps enter. `gap_weight` is fixed at
`1.0` — `pen_sigma` is the penalty multiplier.

Read that objective carefully: **the first term is the mean state energy**.
BaekA is a *minimum*-energy CI search. Once the gap penalty is satisfied it is
free to keep walking downhill *along the seam*, and it will, until it reaches a
lower crossing. That is the desired behaviour when you want the lowest CI of a
pair of surfaces. It is exactly the wrong behaviour when you want one specific,
non-lowest crossing.

`pen_sigma` is the lever that stiffens the penalty and holds the walk near the
seam point you started from.

!!! warning "Set `pen_sigma` when you want a specific, non-lowest crossing"
    With the default `pen_sigma=1` a search started *on* a seam can satisfy the
    gap criterion at step 1 and then slide a full electronvolt downhill along it
    into a different conical intersection. Raise `pen_sigma` to hold the
    intended seam. For the butadiene 1¹B_u⁺/2¹A_g⁻ crossing below, values
    `>= 5` work and `pen_sigma=10` is the recommended setting; `2` is not
    enough.

### Non-lowest seam: the butadiene 1¹B_u⁺/2¹A_g⁻ crossing

This is the worked example. The start structure is the frame of the
bond-length-alternation path where the bright ionic 1¹B_u⁺ and the dark
covalent 2¹A_g⁻ swap character. These are the physical `S1` and `S2`, i.e.
selectors `2,3`:

```ini
[input]
system=
   6   1.916995   0.065369   0.000000
   6   0.554563  -0.434396   0.000000
   6  -1.916995  -0.065369   0.000000
   6  -0.554563   0.434396   0.000000
   1   2.760515  -0.606516   0.000000
   1   2.101350   1.130009   0.000000
   1  -2.760515   0.606516   0.000000
   1   0.382205  -1.502220   0.000000
   1  -2.101350  -1.130009   0.000000
   1  -0.382205   1.502220   0.000000
charge=0
runtype=meci
method=dftb

[scf]
type=rohf
multiplicity=3

[dftb]
model=dtcam
type=mrsf
parameter_path=

[tdhf]
type=mrsf
nstate=3

[optimize]
lib=oqp
states=2,3
meci_search=baeka
energy_gap=1e-5
maxit=50
pen_sigma=10
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3)
meci(S1,S2,algorithm=baeka,gap=1e-5,maxit=50,sigma=10)
dftb(model=dtcam)
geom="butadiene_bla18.xyz"
```

Multi-state BaekA takes the `states` list instead of `istate`/`jstate`. Roots
must be **strictly increasing and consecutive** (`2,3` or `1,2,3`, never
`1,3`). In `.oqp`, `algorithm=` maps to `meci_search`, `gap=` to `energy_gap`,
and `sigma=` to `pen_sigma`.

The difference the stiffness makes, from the same start, same operator, same
budget:

| | `pen_sigma=10` | `pen_sigma=1` (default) |
| --- | --- | --- |
| Mean `S1`/`S2` excitation energy | ≈ 5.27 eV | ≈ 4.46 eV — slid ~0.8 eV downhill |
| True `S1`/`S2` gap at the end point | ≈ 5 × 10⁻⁴ eV | ≈ 1 × 10⁻² eV, still widening |
| Where it ends up | the intended 1¹B_u⁺/2¹A_g⁻ seam, a few hundredths of an Å from the start | walking away toward a different, lower crossing |

The internal `sigma` is ramped up by the additive schedule (`pen_delta`,
`pen_jump`) as the search proceeds, but starting at `1` lets it drift before the
schedule catches up. Starting at `10` prevents the drift.

### `maxit` is not a hard cap

The native optimizer (`lib=oqp`) **auto-restarts from its best geometry** when a
run ends unconverged, adding up to two further rounds of
[`[oqp] recovery_maxit`](../keywords/oqp.md) (default 30) steps. A `maxit=50`
MECI therefore runs up to 110 steps, and `maxit=30` up to 90.

For a genuine cap, disable the recovery:

```ini
[oqp]
auto_recovery=false
```

## Verifying a MECI

Always re-single-point the optimized geometry and read the gap yourself. The
optimizer's own reported gap is computed inside the penalty objective and can
false-converge.

Two files are written into the run directory, and they are **not**
interchangeable:

| File | Contents |
| --- | --- |
| `opt.xyz` | The single latest/retained geometry — rewritten each step. **This is the result.** |
| `opt_geom.xyz` | The full multi-frame trajectory, appended each step. Its **first frame is the STARTING structure**, not the answer. |

`opt_status.txt` carries the per-step table (objective, outer gap, active sigma,
step norms).

So the verification loop is:

1. Take `<rundir>/opt.xyz`.
2. Run the [single-point deck](#single-point-and-excited-state-energies) on it
   with the same `model=` and `nstate=`.
3. Read the true `S1`/`S2` (or `S0`/`S1`) separation from the summary table —
   and check the oscillator strengths, which tell you *which* crossing you
   landed on.

A crossing between a bright and a dark state shows up as two roots that share
the oscillator strength between them at the seam; if both roots come out dark,
you have slid onto a different intersection.

## Troubleshooting

### Discontinuous curves — raise `nstate`

The default `nstate` is often too small. The Davidson solver returns only the
requested number of roots, and with too few of them it can converge onto a
*wrong upper root*, which shows up as kinks, jumps, or state swaps along a scan
or an optimization path. If a potential-energy curve looks discontinuous, or an
excited-state optimization oscillates without converging, raise `nstate` (for
example `3` → `5`) and rerun. Extra roots are cheap in DFTB.

Keep genuinely degenerate multiplets *inside* the requested window — truncating
a multiplet halfway is another source of erratic behaviour.

### SCC will not converge

Preset numerics are already tuned, and `scc_mixer` is the one override a preset
does not lock. Try `scc_mixer=trust` (charge/spin trust-region) or
`scc_mixer=broyden`.

### `model=` was rejected

`Unknown OpenQP-DFTB operator model preset` means the spelling is not in the
accepted set — check the table at the top of this page. Note that a given PyOQP
build may accept fewer spellings than the native library implements; the
`expected:` line of the error message lists exactly what *your* build takes.

### Which run types work

`method=dftb` is wired only through energy/gradient-driven workflows. Accepted:

```text
energy, grad, data, optimize, meci, mep
```

plus `nac`, `nacme`, `namd`, and `soc` when the route is MRSF
(`[tdhf] type=mrsf` with `[dftb] type` `auto` or `mrsf`).

Rejected for `method=dftb`, with a clear input-time error: `hess`, `ts`, `irc`,
`neb`, `tci`, `mecp`, `bp`, `prop`, `ekt`. Analytic/numerical Hessians,
transition-state searches, IRC, and NEB are therefore not available for the DFTB
method today, and the legacy three-state `tci` deck is superseded by
multi-state `runtype=meci` with `meci_search=baeka`.

### Things that cannot be set from an input

The response long-range kernel selector (`response_lc_gamma_code` in the
library) is **not reachable from any `[dftb]` key or C ABI argument**. It is
fixed by the chosen preset (`dtcam` inherits the reference kernel;
`dtcam2`/`dtcam-erf` force erf) and can otherwise only be overridden with
the developer environment variable `OPENQP_DFTB_FIT_RESP_LCGAMMA`, part of the
opt-in `OPENQP_DFTB_FIT_*` fitting-scan family. Those variables are a
parameter-fitting facility, not a supported user interface.

The per-channel `spc_coco` / `spc_ovov` / `spc_coov` splits are reachable from
`[dftb]`, but only on the explicit-keys route (no `model=`), and only with
`backend=native`.

## See also

- [MRSF-TDDFTB](mrsf-tddftb.md) — the response formalism, NACME, SOC, QM/MM
- [BaekA Multistate MECI](baeka-multistate-meci.md) — the algorithm in full
- [`[dftb]`](../keywords/dftb.md) — every DFTB keyword
- [`[optimize]`](../keywords/optimize.md) — every optimizer keyword
- [Optimization](optimization.md) — the shared optimizer workflows
