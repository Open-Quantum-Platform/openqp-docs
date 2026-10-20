# ODP Umbrella Sampling

One-dimensional-projection (ODP) umbrella sampling computes a potential of mean
force (PMF) along a reaction coordinate `xi` defined by one or more collective
variables (CVs) and a reactant and a product reference. Each window is an
ordinary NAMD run with an [`[odp]`](../keywords/odp.md) bias; the windows are
combined afterwards with WHAM.

ODP windows run

- in all-QM NAMD and in QM/MM NAMD,
- in the NVE ensemble or the Langevin NVT ensemble
  (`namd(...,ensemble=nvt,thermostat=langevin)`),
- in nonperiodic QM/MM and in periodic orthorhombic QM/MM (`qmmm(cutoff=PME)`),
- together with the [FlexiBLE](../keywords/flexible.md) solvent boundary, when
  solvent molecules belong to the QM region.

ODP is not available with SOC-NAMD.

## One window

For a free energy, sample each window canonically. The OpenQP example
`examples/ODP/H2CO_BHHLYP-MRSF-NAMD-ODP-NVT.oqp` is one NVT window of
formaldehyde with three CVs:

```text
mrsf(nstate=2)/bhhlyp/sto-3g
namd(T0,scheme=Overlap,nstep=3,dt=0.1,substep=20,ensemble=nvt,thermostat=langevin,thermostat_friction=5.0,seed=20260803,trajectory_interval=1,restart_interval=1,decoherence=off)
odp(enabled=true,cv="distance(1,2);asymmetric_distance(1,3,1,4);angle(3,1,4)",scale="0.5,0.5,1.0",reference_r="2.10,-0.10,1.90",reference_p="2.50,0.10,2.20",center=0.5,k_parallel=0.02,k_perpendicular=0.005,window=1)
geom="../geometries/CH2O-2bc62dda4b8a.xyz"
```

The thermostat temperature is `thermostat_temperature` (default 300 K). Without
`ensemble=nvt` the window is an NVE run (`examples/ODP/H2CO_BHHLYP-MRSF-NAMD-ODP.oqp`);
OpenQP accepts it and records the ensemble, and WHAM then warns that it assumes
canonical sampling.

## A set of windows

Copy the window input once per window and give each copy

- its own `window` label and `center` in `odp(...)` (for example `center`
  from 0 to 1 in steps that let neighbouring `xi` distributions overlap), and
- its own trajectory file, `namd(...,trajectory_file="window-07.namd.trj")`,
  or its own project name.

Keep `cv`, `scale`, `reference_r`, and `reference_p` identical in all windows;
WHAM refuses trajectories whose recorded coordinate definitions differ.
`k_parallel` and `k_perpendicular` may differ between windows, and WHAM reads
them from each trajectory.

## Periodic QM/MM

In a periodic cell each CV is measured at its minimum image: the CV atoms are
unwrapped along the atom pairs the CVs use, each atom at the image nearest the
atom it is bonded to. The run stops only when the CV pairs close a ring whose
minimum images cannot be placed consistently. CV atom indices are 1-based
indices of the full QM+MM system.

When the reaction involves solvent molecules, put them in the QM region and add
the [FlexiBLE boundary](../keywords/flexible.md) so that QM solvent does not
exchange with MM solvent during the window. The OpenQP example
`examples/QMMM/ala-box_BHHLYP-MRSF-NAMD-QMMM-PME-FLEXIBLE-ODP.oqp` combines a
periodic PME box, one QM water held by FlexiBLE, and one NVT ODP window:

```text
mrsf(nstate=2)/bhhlyp/6-31g
namd(S0,scheme=Overlap,nstep=2,ensemble=nvt,thermostat=langevin,restart_interval=2) scf(conv=1e-09)
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

## WHAM

Analyze all windows with the OpenQP example script:

```console
python examples/ODP/odp_wham.py --temperature 300 --output odp-wham.npz window-*.namd.trj
```

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

A window is continued from its checkpoint with the generated `restart=true`
manifest. `examples/ODP/odp_restart.py` runs one step, extends the manifest to
a second step, runs it, and verifies the final checkpoint.
