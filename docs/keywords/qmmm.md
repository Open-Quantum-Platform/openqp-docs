# `[qmmm]`

The `[qmmm]` section configures hybrid quantum-mechanics/molecular-mechanics
(QM/MM) calculations. A quantum region described by an OpenQP method (HF, DFT, or
MRSF-TDDFT) is embedded in a classical force-field environment handled by
[OpenMM](https://openmm.org). The QM/MM path is activated by
`[input] qmmm_flag=true`, and it is used by single-point QM/MM energies,
ground-state QM/MM molecular dynamics, and nonadiabatic
[SOC-NAMD-QMMM](../workflows/soc-namd-qmmm.md) dynamics.

!!! warning "Development preview"
    This section documents the QM/MM implementation branch in
    OpenQP PR [#205](https://github.com/Open-Quantum-Platform/openqp/pull/205).
    It is not part of OpenQP 1.2.0; use that source branch or a later release
    that includes the `[qmmm]` schema.

## Background

The QM subsystem is polarized by the MM electrostatic potential through the
**electrostatic potential-fitted (ESPF) operator**: the MM point charges enter
the QM core Hamiltonian, and the reaction of the QM density on the MM atoms is
represented by ESPF-fitted atomic charges. This gives an analytic,
energy-conserving QM/MM gradient. See
[References](../references.md#qmmm-espf-embedding) for the ESPF operator and its
periodic (particle-mesh Ewald) extension.

Two ways of defining the QM region are supported, matching the two driver paths:

- **Single-point / ground-state QM/MM** reads the geometry and QM selection from
  `[input] system = file.pdb <indices>` (see [`[input] system`](input.md#system)).
  Dangling covalent bonds crossing the QM/MM boundary are capped automatically
  (see [Link atoms](#link-atoms)).
- **QM/MM molecular dynamics and SOC-NAMD-QMMM** (`runtype=namd`) read the PDB,
  force field, and QM selection from the `[qmmm]` keys `pdb_file`,
  `forcefield_files`, and `qm_atoms` below.

## Minimal QM/MM Example

Single-point QM/MM energy (QM selection inline in `[input] system`):

```ini
[input]
qmmm_flag  = true
runtype    = energy
method     = hf
functional = bhhlyp
basis      = 6-31g*
system     = ala.pdb 9 10 17 18 19

[scf]
type = rhf
```

QM/MM molecular dynamics (QM selection in the `[qmmm]` section):

```ini
[input]
qmmm_flag  = true
runtype    = namd
method     = tdhf
functional = bhhlyp
basis      = 6-31g

[scf]
type = rohf
multiplicity = 3

[tdhf]
type   = mrsf
nstate = 5

[qmmm]
pdb_file         = water_box.pdb
forcefield_files = amber14-all.xml,amber14/tip3p.xml
qm_atoms         = 0-2
cutoff           = PME
embedding        = electrostatic
```

## Keywords

### `pdb_file`

| Field | Value |
| --- | --- |
| Type | string (path) |
| Default | *(empty)* |
| Used by | QM/MM molecular dynamics and SOC-NAMD-QMMM |

Path to the PDB file that defines the full QM+MM system (coordinates and
topology) for `runtype=namd`. The single-point and ground-state QM/MM paths take
the PDB path from `[input] system` instead.

### `forcefield_files`

| Field | Value |
| --- | --- |
| Type | string (comma- or space-separated list) |
| Default | *(empty)* |
| Used by | QM/MM molecular dynamics and SOC-NAMD-QMMM |

OpenMM force-field XML files applied to the MM region, e.g.
`amber14-all.xml,amber14/tip3p.xml` for a protein/water system or `tip3p.xml`
for a pure water box. Multiple files are combined by OpenMM in order.

### `forcefield`

| Field | Value |
| --- | --- |
| Type | string list |
| Default | `amber14-all.xml,amber14/tip3p.xml` |
| Used by | ground-state QM/MM setup |

Default force-field list used when a driver builds the MM system without an
explicit `forcefield_files` value. New QM/MM-MD decks should set
`forcefield_files` explicitly.

### `qm_atoms`

| Field | Value |
| --- | --- |
| Type | string (index list) |
| Default | *(empty)* |
| Used by | QM/MM molecular dynamics and SOC-NAMD-QMMM |

Zero-based indices of the atoms placed in the QM region, as individual indices
and/or ranges, e.g. `0 1 2` or `0-2` or `0-8 12 15`. In the nonadiabatic
(`runtype=namd`) path the QM molecule is built from `qm_atoms` only, so the QM
selection must be a **whole molecule**; covalent QM/MM boundaries are not yet
supported in dynamics (see the
[SOC-NAMD-QMMM scope note](../workflows/soc-namd-qmmm.md#scope-and-limitations)).

### `cutoff`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `NoCutoff` |
| Values | `NoCutoff`, `PME`, `Ewald`, `CutoffNonPeriodic`, `CutoffPeriodic` |
| Used by | QM/MM molecular dynamics and SOC-NAMD-QMMM |

OpenMM nonbonded method for the MM region. `NoCutoff` is used for isolated
(non-periodic) clusters. `PME` (particle-mesh Ewald) or `Ewald` select a
periodic box and enable ESPF-PME electrostatics for a solvated/periodic system;
these turn on the periodic branch of the driver.

### `embedding`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `electrostatic` |
| Values | `electrostatic`, `mechanical` |
| Used by | QM/MM electrostatic coupling |

Selects how the MM environment couples to the QM subsystem.

| Value | Meaning |
| --- | --- |
| `electrostatic` | Full ESPF electrostatic embedding. The MM charges polarize the QM density through the ESPF operator, and the QM density reacts on the MM atoms via ESPF-fitted charges. This is the production value and gives the analytic, energy-conserving QM/MM gradient. |
| `mechanical` | No electrostatic coupling into the QM Hamiltonian; the QM/MM interaction is mechanical (bonded/van der Waals) only. |

Legacy spellings such as `espf` and `split` appear in older decks; new inputs
should use `electrostatic`.

### `rigidwater`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | MM constraint setup |

Apply rigid-water (SHAKE/RATTLE) constraints to MM water molecules. QM atoms are
never constrained. Rigid water removes the stiff O-H stretch from the MM region
and allows a normal MD timestep (~0.5-1 fs). The nonadiabatic velocity-Verlet
loop always constrains MM rigid water; QM atoms move under the QM forces.

### `nonbondedmethod`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `NoCutoff` |
| Used by | ground-state QM/MM setup |

OpenMM nonbonded method for the ground-state QM/MM path. The nonadiabatic and
newer MD paths use `cutoff` instead.

### `constraints`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `None` |
| Used by | ground-state QM/MM MD |

OpenMM bond/angle constraint setting for the MM region in the ground-state MD
path (for example, constrain X-H bonds).

### `temperature`

| Field | Value |
| --- | --- |
| Type | float (K) |
| Default | `300.0` |
| Used by | ground-state QM/MM MD |

Target/initial temperature for the ground-state QM/MM MD path. The nonadiabatic
path sets the initial temperature from [`[md] init_temp`](md.md#init_temp).

### `timestep`

| Field | Value |
| --- | --- |
| Type | number (fs) |
| Default | `1` |
| Used by | ground-state QM/MM MD |

MD timestep for the ground-state QM/MM MD path. The nonadiabatic path uses
[`[md] dt`](md.md#dt).

### `nsteps`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | ground-state QM/MM MD |

Number of MD steps for the ground-state QM/MM MD path. The nonadiabatic path
uses [`[md] nstep`](md.md#nstep).

### `istate`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | ground-state QM/MM |

Electronic state index for the ground-state QM/MM path (`0` = reference state).

## Link atoms

When the QM region defined through `[input] system = file.pdb <indices>` cuts a
covalent bond, OpenQP caps each dangling bond automatically with a **hydrogen
link atom** — there is no keyword to enable it; the boundary bonds are detected
from the PDB topology. The link hydrogen is placed along the broken QM-MM bond at
a scaled distance set by the covalent-radius factor

```
g = (r_H + r_QM) / (r_QM + r_MM)
```

where `r_H`, `r_QM`, and `r_MM` are the covalent radii of hydrogen and of the QM
and MM boundary atoms. Only hydrogen capping is currently supported.

!!! note "Link atoms are single-point / ground-state only"
    Automatic link-atom capping applies to the single-point and ground-state
    QM/MM paths. The nonadiabatic (`runtype=namd`,
    [SOC-NAMD-QMMM](../workflows/soc-namd-qmmm.md)) path builds the QM molecule
    from `qm_atoms` only and therefore supports **whole-molecule** QM regions;
    covalent QM/MM boundaries in dynamics are not yet available.

## Notes

- Set `[input] qmmm_flag=true` to activate any QM/MM path; without it the
  `[qmmm]` section is ignored.
- For nonadiabatic QM/MM dynamics, combine this section with the
  [`[md]`](md.md) section and see the
  [SOC-NAMD-QMMM workflow](../workflows/soc-namd-qmmm.md).
- Use `cutoff = PME` (or `Ewald`) with a solvated periodic water box for
  production QM/MM-MD; `NoCutoff` is for isolated clusters.
