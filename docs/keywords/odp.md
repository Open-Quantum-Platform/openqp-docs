# `[odp]`

The `[odp]` section adds one one-dimensional-projection (ODP) umbrella window to
nonadiabatic dynamics (`runtype=namd`, `namd(...)` in `.oqp`) or to ground-state
QM/MM molecular dynamics (`md(...)` with `qmmm(...)`). Several windows
sampled this way are combined into a potential of mean force with WHAM; see the
[ODP umbrella sampling workflow](../workflows/odp-umbrella.md).

ODP runs in all-QM NAMD, in QM/MM NAMD and in ground-state QM/MM MD, in the
NVE ensemble or the Langevin NVT ensemble, and in nonperiodic or periodic
(orthorhombic `cutoff=PME`) QM/MM. It is not available with SOC-NAMD
(`soc=true`), with all-QM ground-state MD, or with other runtypes.

```text
odp(enabled=true,cv="distance(1,2);asymmetric_distance(1,3,1,4);angle(3,1,4)",scale="0.5,0.5,1.0",reference_r="2.10,-0.10,1.90",reference_p="2.50,0.10,2.20",center=0.5,k_parallel=0.02,k_perpendicular=0.005,window=1)
```

## Bias

Each collective variable *q<sub>i</sub>* (CV) is mapped to the dimensionless
coordinate *X<sub>i</sub>* = `scale`<sub>i</sub> *q<sub>i</sub>*. With the
reactant and product references *R* and *P* in the same scaled space

```text
d     = scale * (reference_p - reference_r)          path direction
u     = scale * q - scale * reference_r              displacement from R
xi    = (u . d) / (d . d)                            0 at R, 1 at P
u_perp = u - xi d
V     = 1/2 k_parallel (xi - center)^2 + 1/2 k_perpendicular |u_perp|^2
```

The atomic force is the exact derivative of `V`. `V` is added to the potential
energy, so it is part of the conserved energy in NVE and of the energy balance
in NVT.

In a periodic QM/MM cell every CV takes its own minimum-image value: each
atom pair a CV uses (the two atoms of a distance, both pairs of an asymmetric
distance, and both arms of an angle from its vertex) is taken at its
minimum-image separation, independently of the other CVs. CVs whose pairs form
a ring around the cell are therefore measured correctly as well. The run stops
only when a pair is exactly half the box length apart along an axis, where the
minimum image is not unique.

## Keywords

### `enabled`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | `runtype=namd`; `runtype=md` with QM/MM |

Turns the umbrella window on.

### `cv`

| Field | Value |
| --- | --- |
| Type | string |
| Default | none (required) |
| Indexing | 1-based; in QM/MM, indices of the full QM+MM system |

Semicolon-separated CVs: `distance(a,b)` (bohr), `asymmetric_distance(a,b,c,d)`
= d(a,b) - d(c,d) (bohr), and `angle(a,b,c)` with vertex `b` (radian).

### `scale`

| Field | Value |
| --- | --- |
| Type | float list, one positive value per CV |
| Default | none (required) |
| Units | 1/bohr for distances, 1/radian for angles |

Converts each CV into the dimensionless coordinate used by the projection.

### `reference_r`, `reference_p`

| Field | Value |
| --- | --- |
| Type | float list, one value per CV |
| Default | none (required) |
| Units | bohr or radian, as the CV |

Reactant and product values of the CVs. The scaled references must differ.

### `center`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.0` |

Target value of `xi` for this window (0 at the reactant, 1 at the product).

### `k_parallel`

| Field | Value |
| --- | --- |
| Type | float |
| Default | none (required, positive) |
| Units | Hartree |

Force constant along `xi`.

### `k_perpendicular`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.0` (no perpendicular restraint) |
| Units | Hartree |

Force constant on the scaled displacement perpendicular to the path.

### `window`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |

Non-negative label of the window. It is written to every trajectory record and
used by WHAM to group the samples of one window.

## Output

The packed NAMD trajectory (`<project>.namd.trj`) stores the window definition
in its header (`odp`) and, for every step, `odp_window`, `odp_xi`, the raw,
scaled, and perpendicular CVs, and the parallel, perpendicular, and total bias
(`odp_bias_hartree`). The header also records the ensemble and, for NVT, the
thermostat temperature that WHAM checks.

Ground-state QM/MM MD writes the same per-step records into its energy table
(`total_energy.npz`), next to the unbiased potential (`E_unbiased`,
`e_unbiased_pot_hartree`) and the `droplet` and `solute_com` restraint
energies. The table stores the window definition, the ensemble, the thermostat
temperature and an identity of the system as `bias_metadata_json`: topology
and QM region; every QM option that changes the surface (method, basis with
file-backed basis sets by content, library, `ispher`, `scf`, `dftgrid`, ...);
the contents of the force-field files and of every file they include, with the
QM/MM Hamiltonian options; the `ESPF_*` environment controls; the contents of
DFTB/xTB parameter and backend files; the frozen atoms and constraints; and,
for PME, the cell. WHAM reads these tables like packed NAMD trajectories and
refuses to combine windows whose identities differ.
