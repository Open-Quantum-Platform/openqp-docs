# SOC-NAMD-QMMM

**SOC-NAMD-QMMM** is nonadiabatic molecular dynamics that combines three
capabilities in one propagation loop:

- **NAMD** — Tully fewest-switches surface hopping (FSSH) on MRSF-TDDFT states;
- **SOC** — spin-orbit-coupled intersystem crossing (ISC), so hops occur on the
  spin-adiabatic manifold of mixed singlet/triplet states;
- **QM/MM** — the MRSF-TDDFT chromophore is embedded in a classical (OpenMM) MM
  environment through the ESPF operator.

It is dispatched by `runtype=namd` with `[md] soc=true` and
`[input] qmmm_flag=true`, and is configured through the [`[md]`](../keywords/md.md)
and [`[qmmm]`](../keywords/qmmm.md) sections. This page introduces the method and
gives a complete, runnable input deck.

## Overview and theory

### FSSH nonadiabatic dynamics

Classical nuclei propagate on one active potential energy surface with
velocity-Verlet while the electronic amplitudes evolve; stochastic hops between
surfaces reproduce population transfer. OpenQP implements FSSH generalized to an
arbitrary number of states on MRSF-TDDFT surfaces, with energy-based decoherence
(EDC), finite-difference time-derivative couplings (TDC), and trivial-crossing
(diabatic) following. See [Tully FSSH](../references.md#nonadiabatic-dynamics).

### SOC-NAMD (intersystem crossing)

With `[md] soc=true`, the spin-orbit MRSF-TDDFT driver (`soc_mrsf`) builds and
diagonalizes the spin-orbit Hamiltonian

```
H = diag(E_MCH) + H_SOC
```

whose eigenvectors define the **spin-adiabatic** states. Here the *MCH*
(molecular Coulomb Hamiltonian) basis is the set of spin-pure MRSF singlet and
triplet states, and `H_SOC` are the spin-orbit matrix elements that couple them.
For `[tdhf] nstate` singlets and the same number of triplets, the manifold has
`ns + 3*nt` SOC states (each triplet contributes three `Ms` sublevels).

Surface hopping is carried out on this spin-mixed manifold, so a hop between a
predominantly singlet and a predominantly triplet spin-adiabatic state *is* an
intersystem-crossing event. Continuity of the eigenvectors from step to step is
maintained by **U-phase tracking** (the phase/ordering of the eigenvector matrix
`U`), and the electronic amplitudes are propagated with local diabatization.

**Active-surface force.** [`soc_basis`](../keywords/md.md#soc_basis) selects the
force basis. The default `soc_basis=adiabatic` propagates on spin-adiabatic SOC
eigenstates and uses the **weighted-MCH diagonal gradient**: each contributing
spin-pure (MCH) component carries its own gradient, weighted by its population in
the active spin-adiabatic state, with components below
[`grad_wthr`](../keywords/md.md#grad_wthr) dropped so the force stays continuous
through strong spin mixing. The `soc_du_dt_corr` and `soc_tdc_grad_corr` flags
are optional approximate corrections for this adiabatic force path.

For production trajectories, `soc_basis=mch` propagates in the spin-pure MCH
basis and uses exact active-root MCH gradients; with QM/MM this selects the
`NAMD_SOC_MCH_QMMM` driver. At an ISC hop, velocities are rescaled to conserve
the total energy (including the ESPF embedding energy change).

### ESPF QM/MM embedding

The MRSF-TDDFT QM region is embedded in the OpenMM MM environment through the
**electrostatic potential-fitted (ESPF) operator**: the MM point charges enter
the QM core Hamiltonian (polarizing the QM density), and the QM density reacts on
the MM atoms through ESPF-fitted atomic charges. All electronic quantities — the
reference SCF, the singlet and triplet MRSF states, and the SOC matrix — inherit
the same embedding. The default full-ESPF electrostatics (`embedding=electrostatic`)
give a finite-difference-exact analytic gradient and energy-conserving dynamics.
Rigid-water SHAKE/RATTLE constraints are applied to the MM region inside the
velocity-Verlet loop, so a normal (~0.5 fs) timestep can be used; QM atoms are
never constrained. A periodic water box uses particle-mesh Ewald
(`cutoff=PME`) with ESPF-PME electrostatics. See the
[`[qmmm]`](../keywords/qmmm.md) page and
[References](../references.md#qmmm-espf-embedding).

### Scope and limitations

SOC-NAMD-QMMM builds the QM molecule from [`[qmmm] qm_atoms`](../keywords/qmmm.md#qm_atoms)
only, so **whole-molecule QM regions** are supported. Covalent QM/MM boundaries
(hydrogen link atoms) in nonadiabatic dynamics are **not yet available** —
single-point QM/MM and ground-state QM/MM MD do handle covalent boundaries (see
[Link atoms](../keywords/qmmm.md#link-atoms)). Use a solvated chromophore in a
periodic (PME) water box, with the whole chromophore in the QM region.

## How the driver is selected

`runfunc.compute_namd` picks the surface-hopping class from `qmmm_flag`, `soc`,
and `soc_basis`:

| [`[input] qmmm_flag`](../keywords/input.md#qmmm_flag) | [`[md] soc`](../keywords/md.md#soc) | [`[md] soc_basis`](../keywords/md.md#soc_basis) | Class |
| --- | --- | --- | --- |
| `false` | `false` | ignored | `NAMD` (gas-phase FSSH) |
| `false` | `true`  | `adiabatic` | `NAMD_SOC` (gas-phase spin-adiabatic SOC-NAMD) |
| `false` | `true`  | `mch` | `NAMD_SOC_MCH` (gas-phase MCH-basis SOC-NAMD) |
| `true`  | `false` | ignored | `NAMD_QMMM` (FSSH + ESPF QM/MM) |
| **`true`** | **`true`** | `adiabatic` | **`NAMD_SOC_QMMM`** (spin-adiabatic SOC-NAMD + ESPF QM/MM) |
| **`true`** | **`true`** | **`mch`** | **`NAMD_SOC_MCH_QMMM`** (MCH-basis SOC-NAMD + ESPF QM/MM) |

## Example deck: SOC-NAMD-QMMM in a periodic water box

A complete deck for a chromophore solvated in a periodic TIP3P water box. The
whole chromophore is the QM region (`qm_atoms`); the water is MM.

```ini
[input]
runtype    = namd
qmmm_flag  = true
method     = tdhf
functional = bhhlyp
basis      = 6-31g*

[scf]
type         = rohf
multiplicity = 3          ; MRSF high-spin (triplet) reference

[tdhf]
type   = mrsf
nstate = 3                ; 3 singlets + 3 triplets -> ns+3*nt = 12 spin-adiabatic states

[md]
soc        = true         ; SOC-NAMD (intersystem crossing)
soc_basis  = mch          ; recommended production force basis
active     = 1            ; initial SOC state (overridden by init_state)
init_state = S1           ; start on the state with dominant S1 character
nstep      = 200
dt         = 0.5
thrshe     = 0.1          ; SOC-NAMD recommended gap gate (blocks large-gap S0 hops at FC)
init_temp  = 300.0
grad_wthr  = 0.001

[qmmm]
pdb_file         = chromophore_water.pdb
forcefield_files = amber14-all.xml,amber14/tip3p.xml
qm_atoms         = 0-14   ; whole-molecule QM region (0-based indices)
cutoff           = PME    ; periodic water box (ESPF-PME)
embedding        = electrostatic   ; full-ESPF (default)
rigidwater       = True
```

Notes on the deck:

- **Reference / states.** SOC-NAMD requires an MRSF-TDDFT setup: a high-spin
  ROHF reference (`[scf] type=rohf multiplicity=3`) and `[tdhf] type=mrsf`. With
  `[tdhf] nstate=3` the spin-adiabatic manifold has `ns + 3*nt = 3 + 9 = 12`
  states, so `[md] active` may range `1..12`.
- **Initial surface.** [`init_state=S1`](../keywords/md.md#init_state) starts on
  the state of dominant S1 character and overrides `active`.
- **Force basis.** [`soc_basis=mch`](../keywords/md.md#soc_basis) uses exact
  active-root MCH gradients and selects `NAMD_SOC_MCH_QMMM`. Use
  `soc_basis=adiabatic` to test the spin-adiabatic weighted-gradient path and
  its optional correction flags.
- **Gap gate.** [`thrshe=0.1`](../keywords/md.md#thrshe) is the recommended
  SOC-NAMD value; the large default would allow spurious S0 hops at the
  Franck-Condon geometry.
- **QM region.** [`qm_atoms`](../keywords/qmmm.md#qm_atoms) must be a whole
  molecule (see [Scope and limitations](#scope-and-limitations)).
- **Periodicity.** [`cutoff=PME`](../keywords/qmmm.md#cutoff) selects the
  periodic ESPF-PME branch for a solvated box; use `NoCutoff` for an isolated
  cluster.

## Outputs and energy conservation

The run writes a trajectory log with, per nuclear step, the time, the active
state, the MCH/spin-adiabatic state energies, the total energy `E_tot`
(potential + kinetic, including the ESPF embedding energy), and hopping events.

Under NVE dynamics with the default full-ESPF electrostatics, `E_tot` should be
**flat** (no systematic drift) — this is the main check that the trajectory is
physically meaningful. To verify, plot `E_tot` versus time from the trajectory
log and confirm it fluctuates around a constant with no trend.

If a SOC force path produces a slow drift,
[`econs=true`](../keywords/md.md#econs) rescales velocities each step to conserve
`E_tot` as a temporary stabilizer. Prefer `soc_basis=mch` for production
SOC-NAMD-QMMM trajectories because it uses exact active-root MCH gradients; see
the [force-basis note](#soc-namd-intersystem-crossing) above.

## References

- MRSF-TDDFT — see [References: MRSF-TDDFT](../references.md#mrsf-tddft).
- Relativistic MRSF-TDDFT spin-orbit coupling — see
  [References: Spin-Orbit Coupling](../references.md#spin-orbit-coupling).
- Tully FSSH and spin-adiabatic surface hopping — see
  [References: Nonadiabatic dynamics](../references.md#nonadiabatic-dynamics).
- ESPF QM/MM embedding and its periodic (PME) extension — see
  [References: QM/MM (ESPF) embedding](../references.md#qmmm-espf-embedding).
