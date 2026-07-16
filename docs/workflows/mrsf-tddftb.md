# MRSF-TDDFTB

**MRSF-TDDFTB** transfers the spin-adapted MRSF-TDDFT response — independent
singlet and triplet CSF equations of motion, recovered open-shell spin
complements, and conical-intersection capability — into the atom-resolved
transition-charge framework of long-range corrected DFTB. It is the
excited-state spin-flip family of the [DFTB method](../keywords/dftb.md),
selected with [`[input] method=dftb`](../keywords/input.md#method) plus
[`[tdhf] type=mrsf`](../keywords/tdhf.md#type). The DFTB method also provides
ground-state [DFTB2 and DFTB0](dftb.md), [conventional TD-DFTB](tddftb.md), and
SF-TDDFTB. All DFTB keywords live in the [`[dftb]`](../keywords/dftb.md) section.

!!! warning "External library and development preview"
    The DFTB method is provided by the optional **OpenQP-DFTB** library
    ([`openqp-dftb`](https://github.com/Open-Quantum-Platform/openqp-dftb),
    loaded via `ctypes`); build it from source or build OpenQP with
    `-DENABLE_OPENQP_DFTB=ON` (see the [`[dftb]` reference](../keywords/dftb.md)
    for the full build and library-discovery note). The integration is tracked
    in OpenQP PR [#266](https://github.com/Open-Quantum-Platform/openqp/pull/266)
    and is not part of OpenQP 1.2.0. The one-line `.oqp` format is likewise a
    development-branch input style (see [One-line `.oqp`](../oqp-input.md)).

## Why DFTB

The DFTB electronic problem is minimal-basis and replaces four-center
electron-repulsion integrals by atom-resolved transition charges, so the
complete MRSF response, its analytic gradient, and state couplings are delivered
in seconds for hundreds of atoms. This brings MRSF-level photochemistry —
including nonadiabatic dynamics — to large chromophores, molecular aggregates,
and long trajectories that are out of reach for routine all-electron
MRSF-TDDFT, while keeping the same singlet/triplet spin separation and
multireference character near conical intersections.

## State labels

MRSF-TDDFTB uses a high-spin ROKS DFTB reference, and the root convention
follows MRSF-TDDFT: the lowest singlet response root is relabeled **`S0`**. In
the `[properties] grad` and `[optimize] istate` keys the roots are therefore
**1-based over the MRSF manifold — root 1 = `S0`, root 2 = `S1`**, and so on
(`T0` is the lowest triplet). The one-line `.oqp` form uses the physical
zero-based labels `S0`, `S1`, `T0`, … directly. As with every DFTB family,
`basis=` is an ignored placeholder and `functional=` is empty.

## Energy

Three singlet states (`S0`–`S2`) from one MRSF-TDDFTB response:

**`.inp`**

```ini
[input]
method=dftb
runtype=energy
charge=0
basis=sto-3g
functional=

[tdhf]
type=mrsf
nstate=3

[dftb]
backend=native
type=mrsf
parameter_path=/path/to/params
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3) geom="chromophore.xyz" energy dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="mrsf_energy")
job.molecule("chromophore.xyz", charge=0)
job.dftb(response_type="mrsf", nstate=3, parameter_path="/path/to/params")
job.workflow.energy()
job.run()
```

## Gradient

Gradient of the first excited singlet `S1`. `S1` is response **root 2**, so
`[properties] grad=2` (root 1 is `S0`):

**`.inp`**

```ini
[input]
method=dftb
runtype=grad
charge=0
basis=sto-3g
functional=

[tdhf]
type=mrsf
nstate=3

[dftb]
backend=native
type=mrsf
parameter_path=/path/to/params

[properties]
grad=2
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3) geom="chromophore.xyz" grad(S1) dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="mrsf_grad")
job.molecule("chromophore.xyz", charge=0)
job.dftb(response_type="mrsf", nstate=3, parameter_path="/path/to/params")
job.workflow.gradient(state=2)
job.run()
```

Use `grad=1` / `grad(S0)` / `gradient(state=1)` for the `S0` gradient.

## Geometry optimization

Optimize the `S1` minimum — root 2, so `istate=2` (use `istate=1` for the `S0`
minimum):

**`.inp`**

```ini
[input]
method=dftb
runtype=optimize
charge=0
basis=sto-3g
functional=

[tdhf]
type=mrsf
nstate=3

[dftb]
backend=native
type=mrsf
parameter_path=/path/to/params

[optimize]
lib=oqp
istate=2
maxit=100
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3) geom="chromophore.xyz" opt(S1) dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="mrsf_opt")
job.molecule("chromophore.xyz", charge=0)
job.dftb(response_type="mrsf", nstate=3, parameter_path="/path/to/params")
job.workflow.optimize(istate=2, maxit=100)
job.run()
```

## Long-range kernels and the erf-tuned operator

Two response kernels are available through
[`[dftb] lc_gamma`](../keywords/dftb.md): `yukawa` (LC-DFTB2 Yukawa–Slater) and
`erf` (erf$(\omega R)/R$). The **erf-tuned** combination `lc_gamma=erf`,
`omega=0.25`, `cam_beta=1.2` reproduces the MRSF-TDDFT ordering of
near-degenerate bright/dark states, which the stock kernels can invert. Because
its `cam_beta>1` LC ground-state SCC is harder to converge, pair it with a
robust mixer:

```ini
[dftb]
backend=native
type=mrsf
parameter_path=/path/to/params
lc_gamma=erf
omega=0.25
cam_beta=1.2
scc_mixer=trust
```

## Conical intersections (MECI)

DFTB supplies MRSF-TDDFTB state energies and analytic gradients, so a
minimum-energy conical-intersection (MECI) search is driven by the shared
[`[optimize]`](../keywords/optimize.md) optimizer — there is no separate DFTB
entry point. In particular the **BaekA** two-or-more-state adaptive-penalty
algorithm ([`[optimize] meci_search=baeka`](../keywords/optimize.md#meci_search))
runs on MRSF-TDDFTB states exactly as it does on all-electron MRSF-TDDFT, at
tight-binding cost; this is the engine behind the DTCAM-TB conical-intersection
benchmarks. Because MRSF has the correct S₀/S₁ intersection topology, MRSF-TDDFTB
is the DFTB family to use for S₀/S₁ conical intersections.

The MRSF `S0` is response root 1, so `[optimize] states` is 1-based
(`1`=`S0`, `2`=`S1`). A two-state `S1`/`S0` crossing:

**`.inp`**

```ini
[input]
method=dftb
runtype=meci
charge=0
basis=sto-3g
functional=

[tdhf]
type=mrsf
nstate=3

[dftb]
backend=native
type=mrsf
parameter_path=/path/to/params

[optimize]
meci_search=baeka
states=1,2
gap=1.0e-4
```

**`.oqp`**

```text
mrsf-tddftb(nstate=3) geom="guess.xyz" meci(S0,S1,algorithm=baeka,gap=1e-4) dftb(parameter_path="params.opdftb")
```

**Python**

```python
from oqp.openqp import OpenQP

job = OpenQP(project="mrsf_ci")
job.molecule("guess.xyz", charge=0)
job.dftb(response_type="mrsf", nstate=3, parameter_path="/path/to/params")
job.workflow.meci(states=[1, 2], algorithm="baeka", gap=1.0e-4)
job.run()
```

The BaekA controls (`sigma`, `alpha`, `delta_beta`, `beta_schedule`, `gap`, and
the ordered `states` list) and its distinction from the legacy three-state
`runtype=tci` deck are documented once in the
[`[optimize]`](../keywords/optimize.md#meci_search) reference and apply unchanged
to the DFTB method. See also the [BaekA Multistate MECI](baeka-multistate-meci.md)
workflow.

## NACME and surface hopping

Nonadiabatic couplings are overlap-based time-derivative couplings, computed
from a cross-geometry Slater–Koster state overlap. NACME uses two geometries and
requires `backend=native`:

```ini
[input]
runtype=nacme
method=dftb
basis=sto-3g
functional=
system=
  C 0.0 0.0 0.0
  H 0.0 0.86 -0.55
  H 0.0 -0.86 -0.55
system2=
  C 0.0 0.0 0.0
  H 0.0 0.865 -0.55
  H 0.0 -0.86 -0.55

[tdhf]
type=mrsf
nstate=3

[dftb]
backend=native
type=mrsf
parameter_path=/path/to/params

[nac]
dt=1
align=reorder
```

Surface-hopping dynamics uses the shared FSSH driver (`runtype=namd`) with an
MRSF-TDDFTB electronic structure and the [`[md]`](../keywords/md.md) section;
`[md] active` is 1-based over the MRSF manifold (root 1 = `S0`, so `active=2`
starts on `S1`).

## Spin-orbit coupling

MRSF-TDDFTB SOC uses the one-center approximation: per-element, per-shell
constants `xi_l` supplied through the parameter file as `soc Z l xi` records
(`l=1` for p, `l=2` for d; `xi` in Hartree). It powers standalone SOC
(`runtype=soc`) and, with `[md] soc=true`, spin-orbit-coupled NAMD. For SOC-NAMD
use `[md] soc_basis=mch` (the local-diabatization MCH basis conserves energy;
the spin-adiabatic basis is less robust).

## QM/MM

DFTB QM/MM uses Mulliken-monopole electrostatic embedding: the MM electrostatic
potential enters the SCC Hamiltonian directly, so no ESPF grid fitting is
needed, and the analytic gradient carries the coupling. Activate it with
[`[input] qmmm_flag=true`](../keywords/input.md#qmmm_flag) and the
[`[qmmm]`](../keywords/qmmm.md) section (whole-molecule electrostatic embedding;
the legacy `split` scheme is not supported). Hydrogen link atoms across covalent
QM/MM boundaries are handled by the shared QM/MM layer. Gas-phase SOC-NAMD and
whole-molecule electrostatic QM/MM NAMD are supported; SOC combined with QM/MM
embedding is not yet wired for the DFTB method.

## Python API

The `.dftb(...)` builder accepts `response_type` values `ground`, `dftb0`,
`tddftb`, `sf`, and `mrsf`, along with any `[dftb]` keyword (for example
`lc_gamma`, `omega`, `scc_mixer`). The run type is set either with `runtype=...`
on the builder or through `job.workflow.energy()`, `.gradient(state=N)`,
`.optimize(istate=N)`, and `.meci(...)`:

```python
from oqp.openqp import OpenQP

job = OpenQP(project="thymine_dftb")
job.molecule("thymine.xyz", charge=0)
job.dftb(response_type="mrsf", nstate=3, parameter_path="/path/to/params")
job.workflow.gradient(state=2)
job.run()
```

MRSF-TDDFTB jobs additionally drive the `job.workflow.soc()` and
`job.workflow.namd()` workflows (development preview).
