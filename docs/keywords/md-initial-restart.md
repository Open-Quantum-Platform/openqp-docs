# Initial Conditions and Restart

## Initial Velocity

### `velocity`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `maxwell` |
| Values | `maxwell`, `zero`, or a file path |

`maxwell` samples classical Maxwell--Boltzmann velocities at `temperature`.
`zero` starts from rest. A path reads a specified velocity array. NVE controls
heat exchange after initialization; it does not imply zero initial temperature.

### Velocity-file format and units

The file contains exactly one `vx vy vz` line per atom in geometry order. It
contains no atom labels, atom count, or comment line. Components are Cartesian
velocities in atomic units, bohr per atomic unit of time, not momenta:

```text
 1.2345678901234567e-04 -2.3456789012345678e-04  3.4567890123456789e-05
-4.5678901234567890e-05  5.6789012345678901e-05 -6.7890123456789012e-05
```

OpenQP requires exactly `3N` finite values, reshapes them to `(N,3)`, and
removes centre-of-mass translation. It does not remove overall rotation.

Useful conversions are

```text
v [bohr / atomic unit of time] = 0.0457102876725563 * v [angstrom / fs]
v [bohr / atomic unit of time] = v [bohr / fs] / 41.341374575751
```

For a Wigner ensemble, preserve each sampled geometry with its paired velocity.
Do not combine a Wigner geometry with an independently sampled Maxwell velocity
unless that mixed distribution is intended.

### `temperature`

Default: `300.0` K. It controls internal Maxwell--Boltzmann initialization and
is the target for `ensemble=nvt`. It does not change velocities read from a
file, set to zero, or restored from a checkpoint.

### `seed` and `rng_stream`

`seed=0` is resolved once to the local date as `YYYYMMDD` and frozen in the
restart manifest. Set a nonzero seed for a reproducible ensemble.
`rng_stream=1` is the default independent trajectory identifier. Keep one
campaign seed and assign a different stream to each trajectory. A hopping draw
is determined by `(seed, rng_stream, physical MD step)`.

## Output Files

The same `md(...)` output keywords are read by all three dynamics drivers, but
each driver writes its own file types.

| Keyword | Gas-phase ground-state MD | QM/MM ground-state MD | NAMD (gas phase or QM/MM) |
| --- | --- | --- | --- |
| `trajectory_file` | `<prefix>.md.xyz` | `qmmm_trajectory.pdb` (or `.dcd`) | `<project>.namd.trj` |
| `energy_file` | `<prefix>.md.csv` | `total_energy.npz` | not used |
| `trajectory_interval` | default `1` | default `1` | default `1` |

`<prefix>` is the log-file name without its extension. `trajectory_interval=N`
writes every Nth step, and `0` selects approximately every 10 fs. The
gas-phase energy table keeps every step whatever the interval; the QM/MM MD
frames and the rows of its text log `qmmm_trajectory.dat` share the interval.

The gas-phase `.md.csv` table contains, per step, the step, time (fs),
potential, kinetic and total energy (hartree), instantaneous temperature (K),
and the energy exchanged with the thermostat in that step and cumulatively. No
output may name an input of the same calculation (geometry, velocity file,
input deck, log, PDB, force field, or snapshot); such an input is rejected
before the first electronic evaluation.

### Packed NAMD trajectory

The final point and a point that triggers a strict diagnostic policy are
written even if they are not on the normal interval. Read the packed file
without loading the complete trajectory:

```python
from oqp.library.namd import read_namd_trajectory

header, trajectory = read_namd_trajectory("job.namd.trj")
print(trajectory["active"])
print(trajectory["overlap_tdc_au"][:, 0, 1])
```

The records include coordinates, velocities, energies, populations, complex
coefficients, hop decisions, RNG values, overlaps, TDCs, state tracking, and
NVE diagnostics. SOC records additionally include complex spin-adiabatic
overlaps and TDCs.

## Atomic Restart

| Keyword | Default | Meaning |
| --- | --- | --- |
| `restart_interval` | `10` | Write the checkpoint every Nth step; `0` selects approximately every 10 fs for NAMD and disables the periodic checkpoint for QM/MM MD. |
| `restart_file` | `<project>.namd.restart.npz` (NAMD), `qmmm_md.restart.npz` (QM/MM MD) | Atomic numerical checkpoint. |
| `restart` | `False` | Continue the same calculation from its checkpoint. |

In every driver that supports restart, `nstep` is the total length of the
trajectory, not a number of additional steps; raise it to continue a finished
trajectory.

Gas-phase ground-state MD writes no checkpoint. It rejects `restart`,
`restart_file`, `snapshot`, and `snapshot_interval`; rerun such a trajectory
from its initial conditions.

### NAMD restart

Every canonical NAMD run also writes `<project>.namd.restart.oqp`. Run this
manifest to continue toward the original final `nstep`. Keep the manifest
beside its NPZ checkpoint.

The checkpoint binds the molecular identity, electronic model, random stream,
surface-hopping scheme, numerical-continuity settings, root/phase tracking, and
diagnostic streaks. OpenQP rejects a restart under trajectory-changing options.

### QM/MM MD restart

QM/MM ground-state MD writes `restart_file` every `restart_interval` steps and
at the end of the run. Rerunning the same input with `restart=true` replaces
the PDB coordinates, the periodic cell, and the velocities by those of the
checkpoint, keeps the step counter, and appends to the trajectory, log, and
energy outputs. Output written after the checkpoint by an interrupted run is
discarded first, so no step appears twice.

The checkpoint stores both the integrator velocities, which lag the positions
by half a time step, and the velocities at the positions. With the same `dt`,
the integrator velocities are restored and an NVE trajectory continues as if it
had not been interrupted. With a different `dt`, the half-step offset of the
stored velocities no longer applies; OpenQP starts from the velocities at the
positions, applies the half-step offset of the new `dt`, and reports the
change.

## Phase-Space Snapshots (QM/MM)

A snapshot is one `.npz` file that holds the positions, the velocities at
those positions, the masses, and, for a periodic system, the cell of every atom
of the QM/MM system. It transfers an equilibrated state to later QM/MM MD or
QM/MM NAMD trajectories.

| Keyword | Default | Meaning |
| --- | --- | --- |
| `snapshot_interval` | `0` | QM/MM MD writes a numbered snapshot every N steps; `0` writes none. |
| `snapshot` | none | Start a new QM/MM MD or QM/MM NAMD trajectory from this snapshot. |

Numbered snapshots are named after `restart_file`: with
`restart_file=run.restart.npz`, step 200 is written to
`run.snapshot.00000200.npz`. No other output and no input of the same run may
name one of these files, directly or through a link; such an input is rejected
before the run starts.

A snapshot starts a new trajectory at step zero, whereas `restart=true`
continues an existing one; the two cannot be combined. A snapshot supplies the
initial velocities, so it cannot be combined with `velocity`, and it supplies
the positions, so it cannot be combined with `qmmm(qm_atoms_xyz=...)`. The atom
count and masses of the snapshot must match the PDB topology. Gas-phase MD and
gas-phase NAMD reject `snapshot`.

A typical protocol equilibrates the cell classically, equilibrates the QM/MM
system with NVT MD while writing snapshots, and starts one surface-hopping
trajectory from each snapshot:

```text
# equilibration
bhhlyp/6-31g* geom="system.pdb 1-4"
md(nstep=2000,dt=0.5,ensemble=nvt,temperature=300,snapshot_interval=200,
   restart_file="equil.restart.npz")
qmmm(pdb_file="system.pdb",forcefield_files="forcefield.xml",cutoff=PME)

# production, one input per snapshot
mrsf(nstate=4)/bhhlyp/6-31g* geom="system.pdb 1-4"
namd(S1,scheme=TDC_NAC)
md(nstep=400,dt=0.5,snapshot="equil.snapshot.00000200.npz")
qmmm(pdb_file="system.pdb",forcefield_files="forcefield.xml",cutoff=PME)
```

QM/MM NPT dynamics is not available; equilibrate the cell classically and start
from a snapshot of that cell. A classical equilibration written by a short user
script can produce a snapshot with `oqp.utils.md_snapshot.write_snapshot`,
which takes OpenMM units (nm, nm/ps, dalton).

## Local Continuation with a Smaller Time Step

`continuation_checkpoint` and `continuation_trajectory` create a new output
series from a validated source prefix, leaving the source files unchanged.
Both paths are required and `restart=true` must not be present.

The child calculation uses an absolute final `nstep`, not a number of
additional steps. Local continuation currently supports fixed-step, same-spin
NAMD with `tdc=analytic`; the new timestep cannot exceed the source timestep.
