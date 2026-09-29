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

## Trajectory Output

| Keyword | Default | Meaning |
| --- | --- | --- |
| `trajectory_interval` | `1` | Write every Nth step; `0` selects approximately every 10 fs. |
| `trajectory_file` | `<project>.namd.trj` | Appendable packed binary trajectory. |
| `energy_file` | derived from the project name | Text energy table for ground-state BOMD; not the packed NAMD trajectory. |

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
| `restart_interval` | `10` | Write every Nth step; `0` selects approximately every 10 fs. |
| `restart_file` | `<project>.namd.restart.npz` | Atomic numerical checkpoint. |
| `restart` | `False` | Continue the same calculation from its checkpoint. |

Every canonical NAMD run also writes `<project>.namd.restart.oqp`. Run this
manifest to continue toward the original final `nstep`; `nstep` is not an
additional step count. Keep the manifest beside its NPZ checkpoint.

The checkpoint binds the molecular identity, electronic model, random stream,
surface-hopping scheme, numerical-continuity settings, root/phase tracking, and
diagnostic streaks. OpenQP rejects a restart under trajectory-changing options.

## Local Continuation with a Smaller Time Step

`continuation_checkpoint` and `continuation_trajectory` create a new output
series from a validated source prefix, leaving the source files unchanged.
Both paths are required and `restart=true` must not be present.

The child calculation uses an absolute final `nstep`, not a number of
additional steps. Local continuation currently supports fixed-step, same-spin
NAMD with `tdc=analytic`; the new timestep cannot exceed the source timestep.
