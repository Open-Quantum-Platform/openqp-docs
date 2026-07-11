# One-line `.oqp` Input

The `.oqp` format describes one calculation in one readable line. It has no
leading `#` and no `[input]` or `[scf]` blocks.

!!! warning "Development / next-release input style"

    One-line `.oqp` input is implemented on the current development branch and
    is not part of the published OpenQP 1.2.0 release. Existing 1.2.0 users
    should continue to use sectioned `.inp` files until a release explicitly
    includes this parser.

## Quick Start

Put `h2o.xyz` beside a file named, for example, `h2o-opt.oqp`, and write:

```text
mrsf/bhhlyp/6-31g* h2o.xyz opt
```

For a keyword with no arguments, empty parentheses are optional: `opt` and
`opt()` mean the same thing. The examples use the shorter form when possible.
An `.xyz` or `.pdb` geometry may immediately follow the route in this short
form. OpenQP normalizes it to the stable, explicit form:

```text
mrsf/bhhlyp/6-31g* geom="h2o.xyz" opt
```

Use quotes for a path containing spaces, for example
`geom="structures/water molecule.xyz"`.

Read the line from left to right:

| Text | Meaning |
| --- | --- |
| `mrsf` | Use MRSF-TDDFT. |
| `bhhlyp` | Use the BHHLYP functional. |
| `6-31g*` | Use the 6-31G* basis. |
| `h2o.xyz` | Read the molecular geometry from `h2o.xyz`. |
| `opt` | Optimize the geometry. With MRSF, an omitted state means `S0`. |

Run it as usual:

```bash
openqp h2o-opt.oqp
```

Useful command-line variations are:

```bash
openqp h2o-opt.oqp --nompi
openqp h2o-opt.oqp --silent
openqp h2o-opt.oqp --omp 8
```

`--nompi` is required for ground-state OpenMM QM/MM molecular dynamics.

To optimize a particular excited state with tighter controls, add details only
where they are needed:

```text
mrsf(nstate=3)/bhhlyp/6-31g* geom="h2o.xyz" charge=0 opt(S1,maxit=100) scf(conv=1e-8)
```

This explicitly requests three states, the physical `S1` surface, at most 100
optimization steps, and an SCF convergence threshold of `1e-8`.

### Common MRSF calculations

```text
mrsf(nstate=3)/bhhlyp/6-31g* geom="h2o.xyz" energy
mrsf(nstate=3)/bhhlyp/6-31g* geom="h2o.xyz" grad(S1)
mrsf(nstate=3)/bhhlyp/6-31g* geom="h2o.xyz" opt(T0)
mrsf(nstate=3)/bhhlyp/6-31g* geom="guess.xyz" meci(S1,S2)
```

### Four rules to remember

1. **Write one main task (primary driver) per file.** Choose one of `energy`,
   `grad`, `opt`, `meci`, `soc`, and the other main tasks. For example,
   `grad(S1) opt(S1)` is an error. Modifiers such as `pcm(water)` and exact
   section controls such as `scf(conv=1e-8)` do not count as another task.
2. **MRSF state labels start at zero in each spin group (manifold).** `S0`,
   `T0`, and `Q0` are the lowest singlet, triplet, and quintet states,
   respectively. `S1`, `T1`, and `Q1` are the next states. These labels
   describe ordering *within each spin group*, not a combined energy ordering
   between singlets and triplets.
3. **Do not specify the internal reference for MRSF.** Write `opt(S0)` or
   `opt(T0)`, not `mult=...`, `spin=...`, or a ROHF multiplicity. OpenQP selects
   the required high-spin working reference automatically.
4. **Existing `.inp` files still work unchanged.** Use the one-line syntax in
   a new `.oqp` file. Keep the traditional sectioned syntax in `.inp`; do not
   mix the two formats in one file.

### SOC state counts

One count requests the same number of singlets and triplets:

```text
mrsf(nstate=3)/bhhlyp/6-31g* geom="h2o.xyz" soc
```

This calculates `S0`--`S2` and `T0`--`T2`. To use different counts, put both
counts in `soc(...)`:

```text
mrsf/bhhlyp/6-31g* geom="h2o.xyz" soc(ns=3,nt=5)
```

This calculates `S0`--`S2` and `T0`--`T4`. Do not combine route `nstate` with
`soc(ns=...,nt=...)`; choose one form or the other.

## General Form

The complete pattern is:

```text
ROUTE GLOBAL... PRIMARY_DRIVER MODIFIER... SECTION_CALL...
```

The route comes first and spaces separate the remaining parts. OpenQP converts
the line to its established configuration and applies the same schema
validation used for traditional input.

## Route and Model Reference

Use one of the following route forms. `N` is a positive number of response
roots.

| Calculation model | Canonical route |
| --- | --- |
| Hartree--Fock with automatic restricted/unrestricted reference | `hf/BASIS` |
| Explicit HF reference | `rhf/BASIS`, `uhf/BASIS`, or `rohf/BASIS` |
| Kohn--Sham DFT with automatic restricted/unrestricted reference | `dft/FUNCTIONAL/BASIS` |
| Explicit KS reference | `rks/FUNCTIONAL/BASIS`, `uks/FUNCTIONAL/BASIS`, or `roks/FUNCTIONAL/BASIS` |
| MP2 | `mp2(variant=...,same_spin_scale=...,opposite_spin_scale=...)/BASIS` |
| TDHF | `tdhf(nstate=N)/BASIS` |
| TDDFT | `tddft(nstate=N)/FUNCTIONAL/BASIS` |
| TDA-TDDFT | `tda(nstate=N)/FUNCTIONAL/BASIS` |
| CIS / TDA-TDHF | `tda-tdhf(nstate=N)/BASIS`; `cis(...)` is an accepted input alias |
| SF-TDDFT | `sf(nstate=N)/FUNCTIONAL/BASIS` |
| MRSF-TDDFT | `mrsf(nstate=N)/FUNCTIONAL/BASIS` |
| UMRSF-TDDFT | `umrsf(nstate=N)/FUNCTIONAL/BASIS` |
| SF-TDHF | `sf-tdhf(nstate=N)/BASIS` |
| MRSF-TDHF | `mrsf-tdhf(nstate=N)/BASIS` |
| UMRSF-TDHF | `umrsf-tdhf(nstate=N)/BASIS` |
| Ground-state SCC-DFTB | `dftb` |
| Ground-state non-SCC DFTB0 | `dftb0`; `dftb-noscc` and `dftb-nonscc` are accepted input aliases |
| TD-DFTB | `tddftb(nstate=N)` |
| TDA-TDDFTB | `tda-tddftb(nstate=N)`; `tda-dftb` and `tddftb-tda` are accepted input aliases |
| SF-TDDFTB | `sf-tddftb(nstate=N)`; `sf-dftb` and `sftddftb` are accepted input aliases |
| MRSF-TDDFTB | `mrsf-tddftb(nstate=N)` |

The parenthesized route options are optional; omit the parentheses when none
are needed.

The table shows the canonical spellings. The parser also accepts these
compatibility aliases: `mrsf-tddft`, `mrsftddft`, `umrsf-tddft`,
`umrsftddft`, `sf-tddft`, `sftddft`, `td-dft`, `ks-dft`, `td-dftb`, and
`mrsf-dftb`. Canonical rendering normalizes them to the routes in the table.

The explicit-reference routes never silently change the requested reference.
`rhf` and `rks` require `mult=1`; `rohf` and `roks` require an open-shell
`mult` of at least 2. `uhf` and `uks` may also be used deliberately at
`mult=1`. The TDHF-family routes contain no functional component, whereas the
corresponding TDDFT-family routes do.

DFTB-family routes contain no functional or basis component. `dftb0` selects
the non-SCC ground-state model. Conventional `tddftb` and `tda-tddftb` accept
physical singlet and triplet labels; `T0` is their first triplet response root.
The character of an SF state is not known before diagonalization, so
`sf-tddftb` uses `root=N`, for example `grad(root=2)`, rather than `S`/`T`
labels. MRSF-TDDFTB uses zero-based `S0`/`T0` labels and does not support
quintets.

When `mult` is omitted from `dftb`, `dftb0`, `tddftb`, or `tda-tddftb`, the
canonical lowering does not invent `dftb.reference_multiplicity`. This lets a
probe backend apply its own default. An explicitly written `mult=N` is
preserved. SF- and MRSF-TDDFTB instead construct their required high-spin
reference automatically.

```text
dftb0 geom="h2o.xyz" energy dftb(backend=probe,parameter_path="minimal.opdftb")
tda-tddftb(nstate=3) geom="h2o.xyz" grad(T0) dftb(parameter_path="minimal.opdftb")
sf-tddftb(nstate=3) geom="h2o.xyz" grad(root=2) dftb(parameter_path="minimal.opdftb")
```

All response-route parentheses accept only `nstate`. Select a physical spin
manifold with the primary-driver state, not with a route option. Thus
`mrsf(nstate=3)/... energy(T0)` requests the three triplet states `T0`--`T2`.
Numeric route `mult=...`, `multiplicity=...`, and `spin=...` are not public
spellings. Put advanced response controls in their exact section call, for
example:

```text
mrsf(nstate=5)/bhhlyp/6-31g* geom="h2o.xyz" energy(S0) tdhf(nvdav=30)
```

MP2 route parentheses likewise accept only `variant`, `same_spin_scale`, and
`opposite_spin_scale`; other MP2 settings use `mp2(...)` as an exact section
call. Use physical state labels in the driver for state-specific work.
`mrsf(...) energy` defaults to the singlet target manifold. `energy(T0)`
selects the triplet manifold, and `energy(Q0)` selects the quintet manifold for
all-electron MRSF. MRSF-TDDFTB supports singlet and triplet manifolds only. The
high-spin working reference is supplied internally in every case.

## Top-Level Globals

These common values follow the route without a section name:

| Keyword | Meaning |
| --- | --- |
| `geom="FILE"` | Required primary geometry. Relative paths are resolved from the `.oqp` file directory. |
| `geom2="FILE"` | Previous or second geometry for workflows that require one. |
| `charge=N` | Molecular charge; default `0`. |
| `mult=N` | Ordinary SCF-reference multiplicity for non-mixed-reference models. It is forbidden for MRSF, UMRSF, SF, and MRSF-TDDFTB routes. |
| `library=VALUE` | Basis-library mapping used by the established input schema. |
| `ispher=VALUE` | Spherical/Cartesian AO convention. |
| `perf=N` | OpenQP performance preset. |
| `omp_threads=N` | OpenMP threads per MPI rank. `threads=N` is an alias. |

`geometry`/`system` are accepted aliases for `geom`, and
`geometry2`/`system2` for `geom2`. `basis=...` and `functional=...` are accepted
only when they agree with the route; the slash route is the canonical spelling.
Top-level `multiplicity=N` remains an accepted input alias for canonical
`mult=N`.

For MRSF-family calculations, select the target with a physical driver label
such as `S0`, `S1`, `T0`, or `Q0`; never expose the automatic high-spin
reference through a top-level `mult`.

## Exactly One Primary Driver

Every `.oqp` calculation has exactly one primary driver. If it is omitted,
OpenQP inserts `energy`. Square brackets below mean an optional argument;
`STATE` is a physical label such as `S0`, `S1`, `T0`, or `Q0`.

In the signatures, `OPT` means only `maxit`, `lib`, `optimizer`, `step_size`,
`step_tol`, `rmsd_grad`, `rmsd_step`, `max_grad`, `max_step`, `energy_shift`,
`energy_gap`, `meci_search`, `pen_sigma`, `pen_alpha`, `pen_incre`,
`gap_weight`, and `init_scf`. `NAMD` means the current `[md]` controls `nstep`,
`dt`, `active`, `substep`, `decoherence`, `edc_c`, `thrshe`, `tdc`, `trivial`,
`trivial_thresh`, `init_temp`, `velocity`, `seed`, `restart`, `soc`,
`soc_basis`, `soc_du_dt_corr`, `soc_tdc_grad_corr`, `grad_wthr`, `init_state`,
`econs`, `dt_adaptive`, `dt_min`, and `dx_max`.
For NEB, `product`, `images`/`nimage`, and `climb` are understood by both
backends and routed to the selected backend. `NEB_OQP` means the remaining
native options `spring`, `fmax`, `climb_fmax`, `neb_dt`, `maxmove`, `opt_ends`,
and `end_fmax`. `NEB_GEOMETRIC` means the remaining geomeTRIC options `k`,
`maxg`, `avgg`, `align`, and `optep`.

| Driver signature | Lowered option family |
| --- | --- |
| `energy([S0|T0|Q0])` | Single-point energy. On a response route, the optional zero-state label selects a spin manifold; no other state or options are accepted. MRSF defaults to singlet. |
| `grad([STATE],td_prop=...,export=...,title=...)` | Gradient target plus concise `[properties]` controls. Default target is `S0`, except that SF routes require `root=N`. |
| `opt([STATE],OPT...)` | Minimum optimization. Default target is `S0`, except that SF routes require `root=N`. |
| `meci(STATE1,STATE2,OPT...)` | Two distinct states of the same multiplicity. State order is normalized. |
| `mecp(STATE1,STATE2,OPT...)` | Two states of different multiplicity. |
| `tci(STATE1,STATE2,STATE3,OPT...)` | Three distinct states of the same multiplicity. |
| `mep([STATE],OPT...,points=...,step=...)` | Minimum-energy path; `points` and `step` map to the selected backend. `mep_maxit` is SciPy-only. |
| `ts([STATE],OPT...,hessian=...)` | Transition-state search; the concise `hessian` option is geomeTRIC-only. |
| `irc([STATE],OPT...,direction=...,step=...,hessian=...)` | IRC controls are routed according to `lib=oqp` or `lib=geometric`. |
| `neb([STATE],product="FILE",images=N,climb=...,OPT...,NEB_OQP...)` | Native NEB with `lib=oqp`, which is the default; `product` is required. |
| `neb([STATE],product="FILE",images=N,climb=...,OPT...,NEB_GEOMETRIC...)` | geomeTRIC NEB with `lib=geometric`; `product` is required. |
| `hess([STATE],type=numerical|analytical,dx=...,nproc=...,read=...,restart=...,temperature=...,clean=...)` | Hessian/frequency calculation. |
| `nac(STATE1,STATE2,type=numerical,dx=...,nproc=...,restart=...,clean=...,align=...)` | Numerical nonadiabatic-coupling vector between two states in the same spin manifold. |
| `bp(STATE1,STATE2,type=numerical,dx=...,nproc=...,restart=...,clean=...,align=...)` | Numerical branching-plane calculation between two states in the same spin manifold. |
| `nacme(STATE1,STATE2,dt=...,align=...)` | Coupling matrix element; requires `geom2` or `guess(file2=...)`. |
| `soc(soc_2e=...,ns=...,nt=...)` | Spin-orbit coupling; accepts no single target state. `ns` and `nt` must be supplied together. |
| `md([S0]) qmmm(...)` | Ground-state QM/MM molecular dynamics. `qmmm(...)` is mandatory and owns the OpenMM controls. |
| `namd([STATE],NAMD...)` | MRSF nonadiabatic molecular dynamics using the `[md]` controls listed above; defaults to `S1`. |
| `ekt([STATE],ip=true|false,ea=true|false)` | MRSF extended Koopmans IP/EA options; the parent state defaults to `S0`. |
| `thermo([STATE],type=numerical|analytical,dx=...,nproc=...,read=...,restart=...,temperature=...,clean=...)` | Alias that lowers to the supported Hessian path; the state defaults to `S0`. |
| `prop([STATE],scf_prop=...,nmr_gauge=...,td_prop=...,export=...,title=...)` | MRSF-TDDFT/MRSF-TDHF property driver; defaults to `S0`. |
| `data([STATE],scf_prop=...,nmr_gauge=...,td_prop=...,export=...,title=...)` | Multi-state data/gradient export. A response route defaults to `S1`; an SF route defaults to `root=1`. |

Aliases such as `sp`, `gradient`, `optimize`, `optimization`, and `hessian` are
accepted, but the spellings in the table are the canonical generated forms.
Backend availability and option values remain subject to the existing OpenQP
validator.

SF state character is not known before diagonalization. Therefore every
state-specific SF request must write `root=N`; do not omit the state and do not
write `S0`, `S1`, or `T0` on an SF route.

The NAC family currently requires an MRSF route and two distinct states in the
same spin manifold. `nac` and `bp` support numerical finite differences only;
analytical NAC is rejected. `nacme` accepts only its time-step/alignment
controls and additionally requires a previous geometry through `geom2` or
`guess(file2=...)`. Branching-plane analysis is not available for
MRSF-TDDFTB. The `prop` driver is currently limited to all-electron
MRSF-TDDFT/MRSF-TDHF; use `prop(S1)` or omit the state for its `S0` default.

For MRSF SOC, the route count is applied equally to singlets and triplets:

```text
mrsf(nstate=3)/bhhlyp/6-31g* geom="h2o.xyz" soc
```

This requests `S0`--`S2` and `T0`--`T2`. Use explicit counts when the two
manifolds need different sizes:

```text
mrsf/bhhlyp/6-31g* geom="h2o.xyz" soc(ns=3,nt=5)
```

`ns` and `nt` are inseparable, and `soc(ns=...,nt=...)` cannot be combined with
route `nstate`. For a crossing between different multiplicities, use physical
labels directly, for example `mecp(S0,T0,maxit=100)`.

Two primary drivers never imply a sequence. This is an error:

```text
mrsf(nstate=5)/bhhlyp/6-31g* geom="h2o.xyz" grad(S1) opt(S1)
```

Use separate `.oqp` files for separate calculation steps.

Optimizer libraries are driver-specific:

| Driver | Supported `lib` values |
| --- | --- |
| `opt`, `meci`, `mecp` | `oqp`, `scipy`, `geometric` |
| `tci` | `oqp` |
| `mep` | `oqp`, `scipy` |
| `ts`, `irc`, `neb` | `oqp`, `geometric` |

The default is `lib=oqp`. The concise `optimizer`, `step_size`, and `step_tol`
options belong only to `lib=scipy`. For MEP, `points`/`step` map to
`mep_maxit`/`step_size` with SciPy and to native `maxit`/`mep_step` with OQP;
do not specify both an alias and its backend-specific equivalent.

For native IRC (`lib=oqp`), `hessian=analytical` becomes `[hess]
type=analytical`, while `direction` and `step` become native `irc_direction`
and `irc_step`. Native `hessian` accepts only `numerical` or `analytical`, and
`step` is native-only. For geomeTRIC IRC (`lib=geometric`), `hessian` and
`direction` are geomeTRIC backend options. Thus the same concise driver does
not place a geomeTRIC Hessian choice into the native Hessian section.

NEB backend options are also strict and cannot be mixed:

```text
dft/pbe0/def2-svp geom="reactant.xyz" neb(S0,product="product.xyz",images=7,lib=oqp,spring=0.08,climb=true)
dft/pbe0/def2-svp geom="reactant.xyz" neb(S0,product="product.xyz",images=7,lib=geometric,k=0.8,maxg=0.2,climb=0.5,align=true)
```

For example, `spring` is rejected with `lib=geometric`, and `k` is rejected
with `lib=oqp`.

## Modifiers

Modifiers may accompany the one primary driver:

| Modifier | Meaning |
| --- | --- |
| `d4` | Enable DFT-D4. `d4()` is also accepted. |
| `pcm([SOLVENT], pcm...)` | Enable PCM and optionally name a solvent, for example `pcm(water)`. The current production path is an RHF/ROHF, ddX, reference-SCF single-point energy. |
| `nmr([gauge=cgo|giao])` | Request NMR shielding. Bare `nmr` defaults to GIAO. |
| `ir` | Record that IR intensities are requested; valid only with `hess(...)` or `thermo()`. |
| `raman` | Record that Raman activities are requested; valid only with `hess(...)` or `thermo()`. |
| `qmmm(qmmm...)` | Supply QM/MM options and enable `qmmm_flag` automatically. It may accompany `energy`, `md`, or `namd`; `md` requires it. |

The compatibility spellings `d4=true` and `qmmm=true` remain accepted, but
`d4` and `qmmm(...)` are preferred in canonical files.

In canonical `.oqp` input, `nmr` explicitly lowers to the GIAO gauge; use
`nmr(gauge=cgo)` to request CGO. This canonical default does not alter the
unchanged defaults of a traditional sectioned `.inp` file.

Use `qmmm(n_steps=N,...)` for the QM/MM MD step count. `qmmm.n_steps` is a
first-class schema key used by the OpenMM MD engine. The older `qmmm.nsteps`
key remains accepted for compatibility with the legacy static QM/MM driver,
but it is not the canonical spelling for `md()`.

`energy qmmm(...)` selects the active QM/MM single-point path. `md` is the
ground-state QM/MM molecular-dynamics driver and therefore requires
`qmmm(...)`. MRSF `namd(...)` may run gas phase or with `qmmm(...)`. Attaching
`qmmm(...)` to `grad`, `opt`, or another driver is rejected because those
generic backends do not yet provide a verified QM/MM gradient assembly.
QM/MM/OpenMM controls belong in `qmmm(...)`; nonadiabatic-dynamics controls
belong in `namd(...)` and lower to the legacy `[md]` section.

## Advanced Section Calls

Non-owned legacy keywords keep their section and option names. A section becomes
a keyword-only call:

```text
scf(conv=1e-8,maxit=100)
oqp(coordsys=tric,trust=0.2)
properties(scf_prop=mulliken)
tdhf(nvdav=30,zvconv=1e-7)
```

The available section families are `input`, `guess`, `scf`, `mp2`, `dftgrid`,
`tdhf`, `properties`, `optimize`, `oqp`, `geometric`, `pcm`, `symmetry`, `hess`,
`nac`, `ekt`, `neb`, `md`, `qmmm`, `dftb`, `json`, and `tests`. The established
schema remains authoritative for keyword spelling, type, allowed values, and
cross-section constraints.

This is not a promise that bookkeeping keys can be repeated verbatim. Method,
state, spin, and workflow selectors are owned by the route and primary driver;
the reserved-key table below is authoritative. In particular, use
`soc(ns=...,nt=...)`, not `tdhf(nstate_s=...,nstate_t=...)`, in `.oqp`, and do
not combine those two spellings. Likewise, put `soc_2e` in `soc(...)` rather
than repeating it through `input(soc_2e=...)`.

When a section name is also a primary driver, put its options in that driver.
For example, write `opt(S0,maxit=100,lib=oqp)`, not
`opt(S0) optimize(maxit=100)`. Backend-specific controls remain separate calls,
as in `opt(S0,lib=oqp) oqp(coordsys=tric)`.

## Physical States and Reserved Internal Keys

State labels always describe the physical target:

| Model and label | Physical meaning | Internal lowering |
| --- | --- | --- |
| HF/DFT `S0` | Ground-state SCF surface | State index 0 |
| DFTB/DFTB0 `S0` | Ground-state DFTB surface | State index 0 |
| Conventional TDDFT/TDHF `S0` | Ground-state DFT/HF surface for a state-specific derivative driver | State index 0 |
| Conventional TDDFT/TDHF `Sn`, `n >= 1` | Singlet excited state `n` | Response root `n` |
| Conventional TDDFT/TDHF `Tn`, `n >= 0` | Triplet response state `n` | Response root `n + 1`, target multiplicity 3 |
| TD-DFTB/TDA-TDDFTB `Sn`, `n >= 1` | Singlet excited state `n` | Response root `n` |
| TD-DFTB/TDA-TDDFTB `Tn`, `n >= 0` | Triplet response state `n` | Response root `n + 1`, target multiplicity 3 |
| SF family `root=N` | Response root whose spin character is assigned after diagonalization | Response root `N` |
| All-electron MRSF `Sn`, `Tn`, or `Qn`, `n >= 0` | State `n` within the selected singlet, triplet, or quintet manifold | Response root `n + 1`, target multiplicity 1, 3, or 5 |
| MRSF-TDDFTB `Sn` or `Tn`, `n >= 0` | State `n` within the singlet or triplet manifold | Response root `n + 1`; quintet is rejected |

Every available MRSF spin manifold is therefore zero-based. In all-electron
MRSF, `S0`, `T0`, and `Q0` all lower to internal response root 1, while `S1`,
`T1`, and `Q1` lower to root 2. MRSF-TDDFTB follows the same rule for its
supported singlet and triplet manifolds.
`opt(S0)` therefore lowers to internal `istate=1`. On non-SF routes, omitted
states for `grad`, `opt`, `hess`, and similar state-specific drivers normally
default to `S0`. SF routes are the exception and require an explicit `root=N`.
OpenQP also supplies the triplet ROHF reference for MRSF and the triplet UHF
reference for UMRSF. These are implementation references, not requested
triplet surfaces.
MRSF NAMD uses exactly the same zero-based physical labels. For example,
`namd(T0,soc=true)` lowers to legacy `[md] init_state=T0`; the first triplet is
`T0`, not `T1`. A non-SOC `namd(T0)` selects internal active root 1, while an
omitted NAMD state defaults to `S1`. Do not write the internal `active` or
`init_state` selector alongside a physical driver state.

SF-family state character cannot be assigned safely before diagonalization, so
SF-TDDFT, SF-TDHF, and SF-TDDFTB state-specific drivers require `root=N`
instead of an `S` or `T` label.
Conventional TD calculations accept `S` and `T` labels but reject `Q` labels;
all DFTB routes also reject quintet targets.

The following bookkeeping keys are reserved and cannot contradict the route or
physical state syntax:

| Legacy/internal keys | Canonical source of truth |
| --- | --- |
| `input.method`, `input.runtype`, `input.system`, `input.system2`, `input.basis`, `input.functional`, `input.charge` | Route, globals, and primary driver |
| `scf.type`, `scf.multiplicity` | Route-selected reference for every model; MRSF/SF/UMRSF choose their high-spin reference automatically |
| `tdhf.type`, `tdhf.multiplicity`, `tdhf.nstate`, `tdhf.target` | Response route `nstate` and physical state labels |
| `properties.grad` | `grad(STATE)`, `prop(STATE)`, or `data(STATE)` |
| `optimize.istate/jstate/kstate`, `optimize.imult/jmult` | `opt`, `meci`, `mecp`, `tci`, and reaction-path state labels |
| `hess.state`, `nac.states`, `md.active/init_state` | Corresponding state-aware driver |
| `qmmm.istate` | No canonical equivalent; obsolete disconnected-path selector |
| `tdhf.nstate_s/nstate_t`, `input.soc_2e` | `soc(ns=...,nt=...,soc_2e=...)`; do not combine the two sources |
| DFTB `type`, `target_multiplicity`, `reference_multiplicity` | DFTB route and physical state label |

An attempt such as `mrsf/... opt(S0) scf(multiplicity=1)` is rejected instead
of allowing the last spelling to win.

`qmmm.istate` remains in the legacy schema for compatibility, but it is
an obsolete selector from the disconnected legacy `libopenmm` path. It is
reserved in `.oqp`. Ground-state `md` uses `S0`; use physical driver labels
where a state-aware canonical workflow supports them.

## Canonical Examples

1. HF energy with a tighter SCF threshold:

    ```text
    hf/6-31g* geom="h2o.xyz" charge=0 mult=1 energy scf(conv=1e-8)
    ```

2. DFT-D4/PCM single point:

    ```text
    dft/pbe0/def2-svp geom="h2o.xyz" charge=0 energy d4 pcm(water)
    ```

3. MRSF gradient on the physical first singlet excited state:

    ```text
    mrsf(nstate=5)/bhhlyp/6-31g* geom="h2o.xyz" charge=0 grad(S1)
    ```

4. MRSF optimization on the physical singlet ground state:

    ```text
    mrsf(nstate=5)/bhhlyp/6-31g* geom="h2o.xyz" charge=0 opt(S0,maxit=100)
    ```

5. MRSF conical-intersection search:

    ```text
    mrsf(nstate=5)/bhhlyp/6-31g* geom="guess.xyz" charge=0 meci(S2,S1,maxit=100)
    ```

6. Ground-state QM/MM molecular dynamics:

    ```text
    dft/pbe0/def2-svp geom="qm.xyz" charge=0 md qmmm(pdb_file="system.pdb",forcefield_files="amber14-all.xml",qm_atoms="0-2",n_steps=100)
    ```

7. QM/MM single-point energy with the QM atom selection in the PDB geometry:

    ```text
    dft/pbe0/def2-svp geom="ala.pdb 9 10 17 18 19" energy qmmm(embedding=electrostatic)
    ```

8. Ground-state NEB calculation:

    ```text
    dft/pbe0/def2-svp geom="reactant.xyz" charge=0 neb(S0,product="product.xyz",images=7)
    ```

9. NMR shielding with the canonical GIAO default:

    ```text
    dft/pbe0/def2-svp geom="h2o.xyz" charge=0 energy nmr
    ```

10. Analytic Hessian with IR and Raman intent:

    ```text
    dft/pbe0/def2-svp geom="h2o.xyz" charge=0 hess(S0,type=analytical) ir raman
    ```

11. Forward native IRC:

    ```text
    dft/pbe0/def2-svp geom="ts.xyz" charge=0 irc(S0,direction=forward,step=0.1,maxit=30,hessian=analytical,lib=oqp)
    ```

Run any canonical file normally:

```bash
openqp calculation.oqp
```

## Errors and Corrections

OpenQP reports canonical-looking mistakes as errors; it does not reinterpret
them as prose. Common corrections are:

| Error | Correction |
| --- | --- |
| `# mrsf/...` | Remove the leading `#`. It is not a route marker in `.oqp`. |
| `[input]` or `[scf]` in an `.oqp` file | Keep sectioned input in a `.inp` file, or rewrite it as one line. |
| `grad(S1) opt(S1)` | Put the two primary calculations in separate `.oqp` files. |
| `mrsf/... mult=3` | Remove `mult`; choose the physical target in the driver, such as `opt(T0)`. |
| `sf/... grad(S1)` | Use an unlabeled response root, for example `grad(root=1)`. |
| route `nstate` together with `soc(ns=...,nt=...)` | Choose equal counts with route `nstate`, or unequal counts with `ns` and `nt`. |
| `qmmm(istate=...)` | The key belongs to an obsolete disconnected path; use the physical-state driver contract instead. |

### Optional correction assistant

Canonical syntax is the authoritative runnable input. As a secondary aid,
OpenQP can translate a short Korean or English request into canonical syntax.
It never executes the prose directly: `request.oqp` produces
`request.resolved.oqp`, then that generated file is reparsed and validated
before execution. The original is not overwritten, and ambiguous requests are
rejected. Canonical-looking text with a syntax error is reported as a syntax
error rather than reinterpreted as prose.

For reproducible production work, inspect and retain the resolved canonical
line or write the canonical form directly.

## MRSF Log Presentation

MRSF logs present the physical request first and implementation bookkeeping
second. For example, an MRSF ground-state optimization begins with a summary
equivalent to:

```text
Method:                       MRSF-TDDFT
Calculation:                  Geometry optimization
Physical target state(s):     S0
Target spin:                  singlet
Reference:                    triplet ROHF (internal working reference)
State labels:                 physical labels shown; engine root numbers are internal
```

The SCF detail block likewise says `reference type (internal)` and `reference
multiplicity (internal)` instead of presenting the ROHF triplet as the target
state. Gradient, optimization, intersection, and dynamics progress headings
use `S0`, `S1`, `T0`, or `Q0`; an engine root number is shown only as internal
bookkeeping when needed. SOC summaries show both requested ranges, such as
`S0-S2 and T0-T2`.

The same presentation is used for existing `.inp` calculations; their input
syntax is not changed. In a traditional MRSF input, `[scf] multiplicity=3`
still describes the internal high-spin reference, while `[tdhf]
multiplicity=1|3|5` selects the physical response manifold.
