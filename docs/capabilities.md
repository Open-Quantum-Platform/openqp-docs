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

The native optimizer is selected with `[optimize] lib=oqp` and supports
`optimize`, `ts`, `meci`, `mecp`, `tci`, `neb`, `irc`, and `mep`. geomeTRIC and
SciPy remain optional backends for the workflows wired to them.

## Upcoming or Limited Areas

- Electrostatic embedding QM/MM is an active development direction. Nonadiabatic
  QM/MM dynamics currently supports whole-molecule QM regions only; covalent
  QM/MM boundaries (link atoms) in dynamics are not yet available.
- PCM gradients, PCM optimizations, and state-specific excited-state PCM are not
  part of the first ddX energy path.
- MP2 gradients, Hessians, RI/Laplace/local MP2 kernels, and periodic MP2 are
  not part of the documented standalone MP2 path.
- UMRSF-TDDFT gradients and Hessians are not part of the documented production
  surface yet.
