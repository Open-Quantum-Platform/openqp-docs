# `[flexible]`

The `[flexible]` section adds the FlexiBLE boundary potential of Shen and
Glover ([J. Chem. Phys. 155, 224112 (2021)](../references.md#qmmm-espf-embedding))
to QM/MM nonadiabatic dynamics. It keeps solvent molecules that start in the QM
region closer to a boundary centre than the MM solvent molecules of the same
kind, so a QM water cannot diffuse into the MM region and an MM water cannot
diffuse into the QM region while the QM/MM partition of the atoms stays fixed.

`[flexible]` is connected only to `runtype=namd` (`namd(...)` in `.oqp`) with
QM/MM (`qmmm(...)`). It is rejected for every other runtype and for all-QM
NAMD. In `.oqp` input write it as `flexible(...)`:

```text
mrsf(nstate=2)/bhhlyp/6-31g
namd(S0,scheme=Overlap,nstep=2,ensemble=nvt,thermostat=langevin)
qmmm(forcefield_files="amber14-all.xml amber14/tip3p.xml",qm_atoms="8,9,16,17,18,244,245,246",cutoff=PME)
flexible(enabled=true,alpha=5.0,temperature=300,atoms="8,9,16,17,18")
geom="ala_box.pdb"
```

This input (OpenQP `examples/QMMM/ala-box_BHHLYP-MRSF-NAMD-QMMM-PME-FLEXIBLE-ODP.oqp`,
which also adds one ODP window) moves water HOH 76 (atoms 244-246) into the QM
region of the periodic alanine-dipeptide box and keeps it there.

## Potential

Every solvent molecule *i* is represented by an anchor at distance
*r<sub>i</sub>* from the boundary centre. For a partition of the molecules into
a QM set and an MM set

```text
h(QM, MM) = exp( - sum_{i in QM, j in MM} g(r_i - r_j) )
g(R)      = (alpha R)^3 / (1 + alpha R)   for R > 0, and 0 otherwise
V         = - k_B T ln[ h(actual partition) / sum over partitions h ]
```

The sum in the denominator runs over all partitions with the same number of QM
molecules. `V` is close to zero when every QM molecule is nearer to the centre
than every MM molecule and rises when a QM and an MM molecule exchange their
order. The force is the exact derivative of the evaluated sum, including the
force on the atoms that define a moving centre.

Only partitions near the distance-ordered one contribute. They are collected as
in the authors' OpenMM reference kernel: starting from the ordered partition, a
QM label moves one distance rank outwards while the term stays above
`threshold`; the threshold is then multiplied by `scale` and the sum is
evaluated again until it changes by no more than `threshold` relative to the
previous sum. Unlike the reference kernel, OpenQP always evaluates the sum at
least once at a lowered threshold: a first sum of exactly one only means that
no alternative partition lies above the initial threshold, not that the sum has
converged.

## Molecule selection

A residue whose name is listed in `resnames` is a solvent molecule of the
boundary. It is a QM molecule when all its atoms are in `qmmm(qm_atoms=...)`
and an MM molecule when none are. A residue split between the QM and MM regions
is an error. At least one QM and one MM solvent molecule are required, and the
anchor atom must sit at the same position in every solvent residue.

## Periodic cells

With `qmmm(cutoff=PME)` the anchor-to-centre distance is the minimum-image
distance in the orthorhombic cell. Every QM solvent molecule must stay closer
to the centre than half the shortest box length; otherwise the boundary would
reach its own periodic image and the run stops with an error. MM molecules
beyond half the box contribute nothing. `center=molecules` is not defined in a
periodic cell and is rejected.

## Output

The trajectory header records the settings and the numbers of QM and MM
solvent molecules under `independent_controls.flexible`. The FlexiBLE energy is
part of the per-step `conservative_restraint_energy_hartree` record, together
with the other conservative restraints (`droplet`, `solute_com`); it is a
conservative potential and enters the total-energy conservation check.

## Keywords

### `enabled`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | `runtype=namd` with QM/MM |

Turns the boundary potential on.

### `alpha`

| Field | Value |
| --- | --- |
| Type | float |
| Default | none (required, positive) |
| Units | 1/angstrom |

Steepness of the pair term `g`. The reference kernel's tests use 50 nm<sup>-1</sup>,
that is `alpha=5.0`. A small `alpha` lets very many partitions contribute; the
run then stops with an error rather than enumerating more than 200 000 of them.

### `temperature`

| Field | Value |
| --- | --- |
| Type | float |
| Default | none (required, positive) |
| Units | K |

Temperature *T* in `k_B T` of the potential. It is not taken from the
thermostat; set it to the simulation temperature explicitly.

### `center`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `solute` |
| Values | `solute`, `point`, `molecules` |

Boundary centre. `solute` is the mass-weighted centre of `atoms`, made whole
across the periodic cell about its first atom; it moves with those atoms and
they receive the reaction force. `point` is the fixed position `point`.
`molecules` is the centre of mass of all QM and MM solvent molecules of the
boundary (nonperiodic QM/MM only).

### `atoms`

| Field | Value |
| --- | --- |
| Type | string (integer list) |
| Default | empty |
| Indexing | 0-based, full QM+MM system |

Atoms that define `center=solute`. When empty, the QM atoms that are not in a
QM solvent molecule are used.

### `point`

| Field | Value |
| --- | --- |
| Type | three floats |
| Default | `0.0,0.0,0.0` |
| Units | angstrom |

Fixed centre for `center=point`.

### `anchor`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `O` |

Atom name (as in the PDB/topology) that places each solvent molecule, or `com`
for the molecular centre of mass. The name must occur exactly once in each
solvent residue.

### `resnames`

| Field | Value |
| --- | --- |
| Type | string list |
| Default | `hoh,wat,sol,tip3,tip3p` |

Residue names (case-insensitive) that form the solvent of the boundary.

### `threshold`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.01` |
| Range | 0 < `threshold` < 1 |

Initial cutoff on a partition term, and the relative convergence tolerance of
the partition sum.

### `scale`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Range | 0 < `scale` < 1 |

Factor by which the threshold is lowered between successive evaluations of the
partition sum.

### `max_iterations`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `20` |
| Range | at least 2 |

Maximum number of threshold evaluations. The run stops with an error when the
sum has not converged.

### `keep_below_threshold`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |

Also count a partition whose term falls below the current threshold, without
moving further from it (the reference kernel's alternative cutoff method). The
default discards such a partition.
