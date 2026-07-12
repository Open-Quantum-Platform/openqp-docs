# Examples

The
[OpenQP example inputs](https://github.com/Open-Quantum-Platform/openqp/tree/main/examples)
are the preferred source of runnable input decks. Use them as templates before
writing a new input from scratch.

| Folder | Contents |
| --- | --- |
| `examples/HF` | RHF, ROHF, and UHF Hartree-Fock energies and gradients. |
| `examples/DFT` | DFT energies, gradients, and optimization examples. |
| `examples/MP2` | Standalone MP2 energy and reference-value examples. |
| `examples/SCF` | SCF convergence controls such as DIIS variants, MOM, pFON, and SOSCF. |
| `examples/TDHF` | TDHF energy and gradient examples. |
| `examples/TDDFT` | TDDFT energy and gradient examples. |
| `examples/SF-TDDFT` | Spin-flip TDDFT examples. |
| `examples/MRSF-TDDFT` | MRSF-TDDFT energies, gradients, and optimization data. |
| `examples/OPT` | Native optimization, MECI, MECP, TCI, TS, IRC, NEB, and MEP; one optional legacy geomeTRIC deck is retained only for constrained optimization. |
| `examples/HESS` | Analytic and numerical Hessian workflows. |
| `examples/PCM` | ddX reference-SCF PCM energy cases. |
| `examples/SOC` | MRSF-TDDFT SOC cases. |
| `examples/NMR` | NMR shielding examples. |
| `examples/TRAH` | TRAH SCF examples. |
| `examples/ISPHER` | Spherical-harmonic AO convention examples. |
| `examples/ECP` | Effective-core-potential examples. |
| `examples/UMRSF-TDDFT` | UMRSF-TDDFT energy examples. |
| `examples/XAS` | X-ray absorption examples. |
| `examples/QMMM` | ESPF electrostatic QM/MM (requires OpenMM): NAMD / SOC-NAMD dynamics, ground-state QM/MM MD, covalent-boundary (link atom + `frontier_scheme`), and single-point energies. |

Run a single example:

```bash
openqp examples/HF/H2O_RHF-HF_ENERGY.inp
```

For the standalone MP2 example:

```bash
openqp examples/MP2/h2o_ump2_6-31g.inp
```

Run the packaged example tests:

```bash
openqp --run_tests all
```

Geometry and reaction-path examples use the native OpenQP engine. The only
geomeTRIC compatibility deck retained in `examples/OPT` is
[`HCN_RHF-DFT_CONSTRAINED_GEOMETRIC.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/OPT/HCN_RHF-DFT_CONSTRAINED_GEOMETRIC.inp),
because native constraints are not yet available. It requires the optional
`openqp[geometric]` extra.

## QM/MM examples

The `examples/QMMM` decks exercise ESPF electrostatic QM/MM (a QM region embedded
in an OpenMM MM environment). They require the optional **OpenMM** backend
(`pip install openmm`) and read their `*.pdb` / `*.xml` auxiliary files from the
same folder. The nonadiabatic (`runtype=namd`) decks are part of
`openqp --run_tests all` and are reported **SKIPPED** without OpenMM; the
ground-state (`runtype=md`) and single-point decks are skipped by the suite —
run them directly.

| Deck | Type | What it shows |
| --- | --- | --- |
| `H2CO-water_BHHLYP-MRSF-NAMD-QMMM.inp` | `runtype=namd` | MRSF-TDDFT Tully FSSH (internal conversion, `[md] soc=false`) with ESPF QM/MM: formaldehyde QM + 5 TIP3P waters, `NoCutoff` cluster. |
| `H2CO-water_BHHLYP-SOC-NAMD-QMMM.inp` | `runtype=namd` | SOC-NAMD (intersystem crossing, `[md] soc=true`) on the spin-adiabatic manifold with ESPF QM/MM, same system. |
| `ala-dipeptide_BHHLYP-QMMM-MD-RCD.inp` | `runtype=md` | Ground-state QM/MM MD across a **covalent boundary**: alanine dipeptide, QM = the C-terminal amide (cuts the ALA C–CA bond), hydrogen link-atom cap + `frontier_scheme=rcd`. |
| `run.inp` | `runtype=md` | Ground-state QM/MM MD, whole-molecule QM region (one water of a water dimer). |
| `ala.inp` | single-point | QM/MM energy of the alanine amide (QM selection via `[input] system = file.pdb <indices>`). |
| `2E4E_RHF-DFT-QMMM_energy.inp` | single-point | QM/MM energy on a protein fragment. |

Run a NAMD-QMMM example:

```bash
openqp examples/QMMM/H2CO-water_BHHLYP-MRSF-NAMD-QMMM.inp
```

Run the covalent-boundary ground-state QM/MM MD example (from the folder, so the
PDB/force-field files resolve):

```bash
cd examples/QMMM && openqp ala-dipeptide_BHHLYP-QMMM-MD-RCD.inp
```

See the [`[qmmm]`](../keywords/qmmm.md) keyword page for the input contract and
[covalent QM/MM boundaries](../keywords/qmmm.md#covalent-qmmm-boundaries), and the
[SOC-NAMD-QMMM workflow](../workflows/soc-namd-qmmm.md) for the nonadiabatic path.

When adding a new manual page, link to an OpenQP repository example whenever
possible instead of pasting a long input deck into prose.
