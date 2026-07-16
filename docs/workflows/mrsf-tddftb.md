# MRSF-TDDFTB (OpenQP-DFTB backend)

**MRSF-TDDFTB** transfers the spin-adapted MRSF-TDDFT response — independent
singlet and triplet CSF equations of motion, recovered open-shell spin
complements, and conical-intersection capability — into the atom-resolved
transition-charge framework of long-range corrected DFTB. It is provided by the
optional **OpenQP-DFTB** backend and is selected with
[`[input] method=dftb`](../keywords/input.md#method) plus
[`[tdhf] type=mrsf`](../keywords/tdhf.md#type). The backend also provides
ground-state DFTB2, SF-TDDFTB, and ordinary TDDFTB. All keywords live in the
[`[dftb]`](../keywords/dftb.md) section.

!!! warning "External library and development preview"
    OpenQP-DFTB is a separate, optional library
    ([`openqp-dftb`](https://github.com/Open-Quantum-Platform/openqp-dftb),
    loaded via `ctypes`); install it with `pip install openqp-dftb` or build
    OpenQP with `-DENABLE_OPENQP_DFTB=ON`. The integration is tracked in OpenQP
    PR [#266](https://github.com/Open-Quantum-Platform/openqp/pull/266) and is
    not part of OpenQP 1.2.0.

## Why DFTB

The DFTB electronic problem is minimal-basis and replaces four-center
electron-repulsion integrals by atom-resolved transition charges, so the
complete MRSF response, its analytic gradient, and state couplings are delivered
in seconds for hundreds of atoms. This brings MRSF-level photochemistry —
including nonadiabatic dynamics — to large chromophores, molecular aggregates,
and long trajectories that are out of reach for routine all-electron
MRSF-TDDFT, while keeping the same singlet/triplet spin separation and
multireference character near conical intersections.

## Energy and gradient

MRSF-TDDFTB uses a high-spin ROKS DFTB reference; the root convention follows
MRSF-TDDFT (the lowest singlet response root is relabeled `S0`).

```ini
[input]
runtype=grad
method=dftb
basis=sto-3g
functional=

[tdhf]
type=mrsf
nstate=3

[dftb]
type=mrsf
parameter_path=/path/to/params

[properties]
grad=1
```

Set `[dftb] type=ground` (or run `runtype=energy`/`grad` with no excited state)
for a ground-state DFTB2 energy or gradient, `type=sf` for SF-TDDFTB, and
`type=tddftb` for ordinary TDDFTB.

### Long-range kernels and the erf-tuned operator

Two response kernels are available through [`[dftb] lc_gamma`](../keywords/dftb.md):
`yukawa` (LC-DFTB2 Yukawa–Slater) and `erf` (erf$(\omega R)/R$). The **erf-tuned**
combination `lc_gamma=erf`, `omega=0.25`, `cam_beta=1.2` reproduces the
MRSF-TDDFT ordering of near-degenerate bright/dark states, which the stock
kernels can invert. Because its `cam_beta>1` LC ground-state SCC is harder to
converge, pair it with a robust mixer:

```ini
[dftb]
type=mrsf
parameter_path=/path/to/params
lc_gamma=erf
omega=0.25
cam_beta=1.2
scc_mixer=trust
```

## NACME and surface hopping

Nonadiabatic couplings are overlap-based time-derivative couplings, computed
from a cross-geometry Slater–Koster state overlap. NACME uses two geometries:

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
[`[qmmm]`](../keywords/qmmm.md) section (full-ESPF electrostatic embedding; the
legacy `split` scheme is not supported). Hydrogen link atoms across covalent
QM/MM boundaries are handled by the shared QM/MM layer. Gas-phase SOC-NAMD and
whole-molecule electrostatic QM/MM NAMD are supported; SOC combined with QM/MM
embedding is not yet wired for the DFTB backend.

## Python API

```python
from oqp.openqp import OpenQP

job = (
    OpenQP(project="thymine_dftb")
    .molecule("thymine.xyz", basis="sto-3g")
    .dftb(runtype="grad", response_type="mrsf", nstate=3,
          parameter_path="/path/to/params")
)
job.run()
```

`response_type` accepts `ground`, `tddftb`, `sf`, and `mrsf`. MRSF-TDDFTB jobs
can drive the `job.workflow.soc()` and `job.workflow.namd()` workflows.
