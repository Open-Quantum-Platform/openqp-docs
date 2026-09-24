# QM/MM Preparation and Calculation

QM/MM partitions a molecular system into a quantum-mechanical region and a
molecular-mechanical environment. The QM region describes bond rearrangement,
electronic excitation, charge transfer, or another local electronic process;
the MM region supplies the steric and electrostatic environment at lower cost.
The partition is part of the scientific model and must be reported with the
electronic-structure method and force field.

## Prepare the PDB structure

A deposited PDB entry is a structural starting point, not a calculation-ready
chemical model. Before importing it into Studio, inspect and, where necessary,
prepare:

- missing hydrogen atoms, residues, side chains, and cofactors;
- alternate locations and partial occupancies;
- protonation and tautomeric states;
- metal coordination and nonstandard residues;
- crystallographic solvent, ions, ligands, and biological assembly;
- the total charge and spin state of the intended QM region; and
- periodic cell information when a periodic MM method is required.

Studio preserves the imported PDB with the generated project. It does not infer
the chemically correct protonation state or repair a force-field topology.

## Select the QM region

After a PDB file is opened or fetched, Studio displays **QM/MM calculation** in
Builder. Select atoms in the molecular viewer; the list is written as
zero-based atom indices accepted by OpenQP. Consecutive atoms are compressed to
ranges such as `18-27 31 45-52`.

The QM region should normally contain:

- every atom directly involved in bond formation or cleavage;
- the complete conjugated or electronically active unit;
- metal ions and directly coordinated atoms when their electronic structure is
  central to the calculation; and
- enough surrounding residues or solvent molecules to avoid placing the
  QM/MM boundary through a strongly polarized or delocalized bond.

Convergence with respect to QM-region size is a model validation step. Compare
the quantity of interest after expanding the region, not just the total energy
of two differently partitioned systems.

## MM force field

**MM force-field files** accepts one or more OpenMM XML names separated by
commas. `amber14-all.xml` is the initial value. A solvated Amber model commonly
uses `amber14-all.xml,amber14/tip3p.xml`; choose only files appropriate to the
actual residues and water model.

OpenMM must be able to parameterize every MM atom. Nonstandard ligands,
cofactors, and metal sites may require validated custom parameters. A successful
PDB parse does not establish force-field coverage.

## Embedding

**Electrostatic (ESPF)** includes the MM charge environment in the QM
Hamiltonian through the OpenQP electrostatic-potential fitting treatment. This
allows the QM density to polarize in response to the environment.

**Mechanical** omits electrostatic coupling to the QM Hamiltonian; the QM/MM
interaction contains only the bonded and van der Waals terms retained by the
partition. It is therefore less responsive to local electric fields and can
change excitation energies or charge-transfer behavior substantially.

The selected embedding model must be used consistently when comparing
structures or states.

## Covalent boundary and frontier charges

If the QM/MM boundary crosses a covalent bond, OpenQP constructs the boundary
treatment supported by the selected calculation. The electrostatic frontier
scheme controls MM charges near that cut:

| Studio choice | Input value | Meaning |
| --- | --- | --- |
| Full ESPF field | `none` | Retain the unmodified MM charge field |
| Redistributed charge and dipole | `rcd` | Redistribute frontier charge while preserving local charge and dipole behavior |
| Redistributed charge | `rc` | Redistribute the frontier charge to neighboring MM sites |
| Delete frontier charge | `z1` | Remove the frontier-site charge |

Inspect the boundary rather than selecting a scheme only by name. Avoid cutting
through aromatic, multiple, or strongly polarized bonds when a larger QM region
can move the boundary to a chemically simpler location.

## Nonbonded method and periodicity

`NoCutoff` is the default isolated-system treatment. `CutoffNonPeriodic` uses a
finite nonperiodic cutoff. `PME`, `Ewald`, and `CutoffPeriodic` require periodic
box vectors. Studio refuses to generate those periodic choices when the PDB
lacks a `CRYST1` record, because silently treating an unknown cell as periodic
would define a different physical system.

**MM constraints** and **Rigid MM water** control the classical environment.
They can permit a larger integration time in dynamics, but they also change the
degrees of freedom and must be recorded.

## Generated input

For a nonperiodic electrostatic calculation, Studio can generate:

```text
route qmmm_flag=true
dft/b3lyp/6-31g*
qmmm(pdb_file="enzyme.pdb",forcefield_files="amber14-all.xml",qm_atoms="18-27 31")
geom="enzyme.pdb 18-27 31"
```

Only settings that differ from OpenQP defaults are added. For example:

```text
qmmm(pdb_file="solvated.pdb",forcefield_files="amber14-all.xml,amber14/tip3p.xml",qm_atoms="18-27 31",frontier_scheme=rcd,cutoff=PME,constraints=HBonds,rigidwater=true)
```

The PDB file is copied into the calculation directory beside the `.oqp` input.
Keep both files together when moving or archiving the calculation.

## Run and verify

Before starting a calculation, verify:

1. The PDB atom order matches the QM atom list.
2. The QM charge and multiplicity describe the selected atoms and link-atom
   treatment.
3. Every MM residue has force-field parameters.
4. Periodic methods have the intended cell and solvent model.
5. The QM/MM boundary is chemically defensible.
6. The chosen OpenQP workflow supports the requested QM/MM calculation.

After execution, inspect the OpenQP log for topology, boundary, embedding, and
SCF diagnostics before interpreting an energy or spectrum. For dynamics, also
check energy conservation, time step, constraints, state tracking, and failed
trajectory steps.

The current OpenQP concise interface accepts QM/MM with **Single-point energy**,
**Ground-state QM/MM dynamics**, and embedded **Nonadiabatic dynamics**. Generic
QM/MM gradient and geometry-optimization drivers are rejected because they do
not yet expose the assembled total QM/MM gradient. NAMD imposes an additional
whole-molecule QM-region restriction. Consult
[SOC-NAMD-QM/MM](../workflows/soc-namd-qmmm.md) and the
[qmmm keyword reference](../keywords/qmmm.md) for the exact engine version.
