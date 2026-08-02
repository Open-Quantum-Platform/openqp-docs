# Capabilities

This page summarizes what the current user manual documents. It is not a
promise that every combination of method, property, and backend is available.
When a workflow has limits, use the linked workflow page or keyword page for the
specific input contract.

## Electronic Structure

| Area | Status |
| --- | --- |
| HF and DFT | RHF, ROHF, and UHF references. |
| MP2 | Energy-only standalone MP2 on RHF, UHF, and ROHF references, with spin-scaled variants. |
| Coupled cluster | Development preview in OpenQP PR [#302](https://github.com/Open-Quantum-Platform/openqp/pull/302), not OpenQP 1.2.0. Energy-only CCSD and CCSD(T) on RHF, UHF, and ROHF references, with a frozen core. In-core integrals; the open-shell path is a spin-orbital solver for small systems. See [Coupled Cluster](workflows/coupled-cluster.md). |
| TDHF/TDDFT | Energy and gradient workflows for supported references. |
| SF-TDDFT and MRSF-TDDFT | Multiconfigurational ground- and excited-state energies, gradients, NACME, SOC, and optimization workflows. |
| UMRSF-TDDFT | Energy-only UHF-reference workflow. |
| MRSF-EKT | IP/EA analysis with Dyson-like orbital data. |

## Properties

| Property | Status |
| --- | --- |
| Analytic gradients | Available for the supported HF/DFT and response workflows. |
| HF/DFT Hessians | Native analytic path for supported HF/DFT references. |
| Numerical Hessians | Available through the Hessian workflow. |
| NACME | MRSF-TDDFT state-coupling workflow. |
| SOC | MRSF-TDDFT one-electron and mean-field two-electron SOC. |
| MRSF excited-state analysis | NTOs, attachment/detachment densities, state-to-state transition densities, cube export, QCSchema export, FCIDUMP export, and external-code comparisons through `oqp.interop`. |
| Nonadiabatic MD (NAMD) | Development preview in OpenQP PR [#205](https://github.com/Open-Quantum-Platform/openqp/pull/205), not OpenQP 1.2.0. Covers Tully surface hopping, SOC-NAMD, and ESPF QM/MM embedding. See [SOC-NAMD-QMMM](workflows/soc-namd-qmmm.md). |
| QM/MM | Development preview in OpenQP PR [#205](https://github.com/Open-Quantum-Platform/openqp/pull/205), not OpenQP 1.2.0. Covers ESPF electrostatic embedding for single-point energies, ground-state MD, and nonadiabatic dynamics. See [`[qmmm]`](keywords/qmmm.md). |
| Scalar relativistic correction | Spin-free DKH correction through `[scf] scal_rel=1` or `2`. |
| PCM/ddX | Energy-only reference-SCF path for RHF/ROHF. |
| NMR | Nuclear magnetic shielding via `[properties] scf_prop=nmr`. |
| IR/Raman | Frequency-analysis intensities from supported Hessian workflows. |

## Geometry and Paths

The native optimizer supports `optimize`, `ts`, `meci`, `mecp`, `neb`, `irc`,
and `mep`; legacy `tci` inputs remain compatible. MECI includes the BaekA
adaptive algorithm for two or more same-manifold states. Concise `.oqp`
geometry drivers select the native engine automatically and do not expose a
backend selector. Native TS supports model, numerical, or analytical initial
Hessians and mode following. Native NEB supports endpoint alignment and
relaxation, climbing images, maximum and RMS force convergence, and final
multi-frame XYZ path output.

geomeTRIC and SciPy remain optional compatibility backends for traditional
sectioned `.inp` files and the Python API. Native `.oqp` supports frozen-distance
minimum searches; legacy geomeTRIC remains an escape hatch for advanced
constraint types that the concise grammar does not yet support.

## Upcoming or Limited Areas

- Electrostatic embedding QM/MM is an active development direction. Nonadiabatic
  QM/MM dynamics currently supports whole-molecule QM regions only; covalent
  QM/MM boundaries (link atoms) in dynamics are not yet available.
- PCM gradients, PCM optimizations, and state-specific excited-state PCM are not
  part of the first ddX energy path.
- MP2 gradients, Hessians, RI/Laplace/local MP2 kernels, and periodic MP2 are
  not part of the documented standalone MP2 path.
- Coupled-cluster gradients and derivative workflows are not implemented, and
  there is no integral-direct, density-fitted, or disk-based coupled-cluster
  mode; the integrals are held in memory.
- UMRSF-TDDFT gradients and Hessians are not part of the documented production
  surface yet.
