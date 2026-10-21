# ODP Umbrella Sampling

One-dimensional-projection (ODP) umbrella sampling computes a potential of mean
force (PMF) along a reaction coordinate `xi` defined by one or more collective
variables (CVs) and a reactant and a product reference. Each window is an
ordinary NAMD run, or a ground-state QM/MM MD run, with an
[`[odp]`](../keywords/odp.md) bias; the windows are combined afterwards with
WHAM.

ODP windows run

- in all-QM NAMD, in QM/MM NAMD and in ground-state QM/MM MD
  (`md(...) qmmm(...)`, see below),
- in the NVE ensemble or the Langevin NVT ensemble
  (`md(...,ensemble=nvt)`),
- in nonperiodic QM/MM and in periodic orthorhombic QM/MM (`qmmm(cutoff=PME)`),
- in QM/MM NAMD only: together with the [FlexiBLE](../keywords/flexible.md)
  solvent boundary, when solvent molecules belong to the QM region
  (`[flexible]` is not connected to ground-state QM/MM MD).

ODP is not available with SOC-NAMD.

## One window

For a free energy, sample each window canonically. The OpenQP example
`examples/ODP/H2CO_BHHLYP-MRSF-NAMD-ODP-NVT.oqp` is one NVT window of
formaldehyde with three CVs:

```text
mrsf(nstate=2)/bhhlyp/sto-3g
namd(T0,scheme=Overlap,substep=20,decoherence=off)
md(nstep=3,dt=0.1,ensemble=nvt,friction=5.0,seed=20260803,trajectory_interval=1,restart_interval=1)
odp(enabled=true,cv="distance(1,2);asymmetric_distance(1,3,1,4);angle(3,1,4)",scale="0.5,0.5,1.0",reference_r="2.10,-0.10,1.90",reference_p="2.50,0.10,2.20",center=0.5,k_parallel=0.02,k_perpendicular=0.005,window=1)
geom="../geometries/CH2O-2bc62dda4b8a.xyz"
```

`namd(...)` holds the electronic treatment and `md(...)` the nuclear
propagation, as described under [`md`](../keywords/md.md). `ensemble=nvt`
selects the Langevin thermostat at `temperature` (default 300 K; for example
`md(...,ensemble=nvt,temperature=310)`) with `friction` in ps⁻¹. Without
`ensemble=nvt` the window is an NVE run (`examples/ODP/H2CO_BHHLYP-MRSF-NAMD-ODP.oqp`);
OpenQP accepts it and records the ensemble, and WHAM then warns that it assumes
canonical sampling.

## A set of windows

Copy the window input once per window and give each copy

- its own `window` label and `center` in `odp(...)` (for example `center`
  from 0 to 1 in steps that let neighbouring `xi` distributions overlap), and
- for NAMD, its own trajectory file,
  `md(...,trajectory_file="window-07.namd.trj")`, or its own project name;
- for ground-state QM/MM MD, its own directory (or its own
  `qmmm(energy_file=...)`): the energy table that WHAM reads defaults to the
  fixed name `total_energy.npz` and would otherwise be overwritten.

Keep `cv`, `scale`, `reference_r`, and `reference_p` identical in all windows;
WHAM refuses trajectories whose recorded coordinate definitions differ.
`k_parallel` and `k_perpendicular` may differ between windows, and WHAM reads
them from each trajectory.

## Periodic QM/MM

In a periodic cell each CV is measured at its own minimum image: every atom
pair a CV uses is taken at its minimum-image separation, independently of the
other CVs. The run stops only when a pair is exactly half the box length apart
along an axis. CV atom indices are 1-based indices of the full QM+MM system.

When the reaction involves solvent molecules, put them in the QM region and add
the [FlexiBLE boundary](../keywords/flexible.md), a finite bias that makes an
exchange of QM and MM solvent during the window unlikely (penalized, not
forbidden, for finite `alpha`). The OpenQP example
`examples/QMMM/ala-box_BHHLYP-MRSF-NAMD-QMMM-PME-FLEXIBLE-ODP.oqp` combines a
periodic PME box, one QM water kept near the solute by FlexiBLE, and one NVT ODP window:

```text
mrsf(nstate=2)/bhhlyp/6-31g
namd(S0,scheme=Overlap) scf(conv=1e-09)
md(nstep=2,ensemble=nvt,restart_interval=2)
qmmm(forcefield_files="amber14-all.xml amber14/tip3p.xml",qm_atoms="8,9,16,17,18,244,245,246",cutoff=PME,ewald_tol=1e-06,lj_switch=true,h_lj=true,mm_charge_width=0.7)
flexible(enabled=true,alpha=5.0,temperature=300,atoms="8,9,16,17,18")
odp(enabled=true,cv="distance(17,245); distance(9,245)",scale="1.0,1.0",reference_r="6.2,7.3",reference_p="5.4,5.5",center=0.1,k_parallel=0.05,k_perpendicular=0.01,window=1)
geom="ala_box.pdb"
```

Note the two index conventions: `qmmm(qm_atoms=...)` and `flexible(atoms=...)`
are 0-based, `odp(cv=...)` is 1-based. Atom 245 in the CVs is the oxygen of the
QM water, atoms 244-246 (0-based) in `qm_atoms`.

The FlexiBLE potential and the ODP bias are both conservative and both enter
the total energy. The ODP bias is written to `odp_bias_hartree`, the FlexiBLE
energy to `conservative_restraint_energy_hartree`. WHAM unbiases only the ODP
bias; FlexiBLE is part of the sampled Hamiltonian, as the QM/MM partition is.

## Ground-state QM/MM MD

The original ODP application (Baek and Choi, JCTC 14, 2312 (2018)) samples a
ground-state reaction in solution. Write the window as a ground-state QM/MM MD
run; `droplet(...)` keeps the solvent of a nonperiodic system together and
`solute_com(...)` holds the solute in the middle of it. The example
`examples/QMMM/H2CO-water_HF-QMMM-MD-ODP.oqp` is one such window:

```text
hf/sto-3g
md(nstep=3,dt=0.5,ensemble=nvt,temperature=300,friction=5.0,seed=7,trajectory_interval=1,restart_interval=3)
qmmm(pdb_file="formaldehyde_water.pdb",forcefield_files="formaldehyde.xml tip3p.xml",qm_atoms="0-3")
droplet(enabled=true,radius=3.0,buffer=0.5,force_constant=2.0,max_penetration=5.0)
solute_com(enabled=true,force_constant=1.0,atoms="0-3")
odp(enabled=true,cv="distance(1,5); distance(2,5)",scale="1.0,1.0",reference_r="7.6,5.3",reference_p="5.3,6.4",center=0.2,k_parallel=0.1,k_perpendicular=0.02,window=2)
geom="formaldehyde_water.pdb"
```

The bias energy and force are added to the QM/MM energy and force before the
OpenMM integrator, so the dynamics samples the biased potential. Run each
window in its own directory and pass the energy tables to WHAM:

```python
from oqp.library.odp import odp_wham

result = odp_wham(["window-01/total_energy.npz", "window-02/total_energy.npz"],
                  300.0, bins=60, discard=1000)
```

`discard=1000` drops the first 1000 recorded steps of each window as
equilibration; it assumes production windows of several thousand steps. For
the three-step example above use `discard=0`.

`[flexible]` is connected only to NAMD. In a periodic cell the ground-state
bias requires an orthorhombic box. A window continued with
`md(...,restart=true)` must keep the bias, the restraints, the QM/MM
Hamiltonian and the temperature of the table it extends; otherwise the run
stops before adding any row.

## WHAM

Analyze all windows with the OpenQP example script:

```console
python examples/ODP/odp_wham.py --temperature 300 --output odp-wham.npz window-*.namd.trj
```

The same script and function accept the `total_energy.npz` tables of
ground-state QM/MM MD windows.

or from Python:

```python
from oqp.library.odp import odp_wham

result = odp_wham(["window-01.namd.trj", "window-02.namd.trj"], 300.0,
                  bins=100, discard=0, stride=1, output="odp-wham.npz")
```

`--discard` drops the first records of each window and `--stride` thins them.
The temperature is required. For NVT windows it must equal the recorded
thermostat temperature, otherwise WHAM stops with an error; NVE windows are
accepted with a warning. Continuation trajectories of one window are joined in
the order given. The result contains the bins along `xi` (`bin_edges`, `bin_centers`), the PMF
(`free_energy_hartree`, `free_energy_kcal_mol`), the window free energies, and
the convergence of the WHAM equations (`converged`, `residual`).

## Restart

A NAMD window is continued from its checkpoint with the generated
`restart=true` manifest. A ground-state QM/MM MD window has no manifest: rerun
the same input with `md(...,restart=true)` and a larger `nstep` (the total
length); the run continues from its checkpoint and appends to its energy
table. `examples/ODP/odp_restart.py` runs one step, extends the manifest to
a second step, runs it, and verifies the final checkpoint.
