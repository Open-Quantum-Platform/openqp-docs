# Keyword Reference

This chapter is the book-style reference for OpenQP's section-level settings.
Workflow pages lead with the recommended `.oqp` form, then Python, and
finally a legacy sectioned `.inp` equivalent. This chapter explains the
underlying section keywords, their value types and defaults, and the workflow
constraints enforced by the input checker.

The entries are aligned with these OpenQP source files:

- [`pyoqp/oqp/molecule/oqpdata.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/molecule/oqpdata.py)
- [`pyoqp/oqp/utils/input_checker.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/utils/input_checker.py)

## How to Read an Entry

Each keyword entry uses the same structure:

| Field | Meaning |
| --- | --- |
| Type | The parsed value type used by OpenQP. |
| Default | The value inserted when the keyword is omitted. |
| Values | Allowed or commonly used values. If validation enforces a finite set, that set is listed. |
| Used by | The workflows or code paths that normally read the keyword. |
| Description | The practical meaning of the keyword. |
| Notes | Interactions with other keywords, limitations, and common mistakes. |

Boolean keywords accept ordinary true/false spellings such as `true`, `false`,
`yes`, `no`, `1`, and `0` unless a keyword documents a narrower set.

Numeric state indices in traditional sectioned input are workflow dependent.
HF/DFT reference-state properties use state `0`. Ordinary TDHF/TDDFT state `1`
means the first excited state. SF-TDDFT and MRSF-TDDFT internal state `1` means
the lowest response target. The `.oqp` format hides that offset: MRSF uses
physical `S0`, `T0`, and `Q0`, while SF uses `root=1`. See
[`.oqp` input](../oqp-input.md#physical-states-and-reserved-internal-keys).

Method background and literature pointers are collected in
[References](../references.md). The keyword pages link there for MRSF-TDDFT,
MP2, SOC, scalar relativistic correction, and PCM/ddX rather than repeating
full bibliographies inside each keyword entry.

## Section Index

| Section | Purpose |
| --- | --- |
| [`[input]`](input.md) | Global calculation setup, geometry, run type, AO convention, threading. |
| [`[guess]`](guess.md) | Initial orbitals, restart files, and MO swaps. |
| [`[scf]`](scf.md) | Reference type, convergence controls, pFON, TRAH, fallback manager. |
| [`[mp2]`](mp2.md) | Standalone MP2 spin-scaling controls. |
| [`[afqmc]`](afqmc.md) | Trial construction, CSF-space selection, and AFQMC propagation controls. Requires the companion `openqp-afqmc` development build; not recognized by OpenQP itself. |
| [`[dftb]`](dftb.md) | DFTB backend, SCC, response, spin, and MRSF-TDDFTB controls. |
| [`[dftgrid]`](dftgrid.md) | DFT quadrature and hybrid/range-separated functional controls. |
| [`[tdhf]`](tdhf.md) | TDHF/TDDFT/SF/MRSF/UMRSF response settings. |
| [`[md]`](md.md) | Nonadiabatic surface-hopping molecular dynamics (`runtype=namd`), including SOC-NAMD. |
| [`[qmmm]`](qmmm.md) | Hybrid QM/MM setup: QM region, force field, ESPF embedding, and link atoms. |
| [`[properties]`](properties.md) | Gradients, NMR, export, and property requests. |
| [`[hess]`](hess.md) | Hessian, frequency, and thermochemistry controls. |
| [`[nac]`](nac.md) | NAC and NACME state-pair controls. |
| [`[ekt]`](ekt.md) | MRSF-EKT IP/EA channel selection. |
| [`[optimize]`](optimize.md) | Target state and optimization convergence controls. |
| [`[oqp]`](oqp.md) | Native optimizer controls. |
| [`[geometric]`](geometric.md) | Optional legacy geomeTRIC controls for traditional `.inp` and Python workflows. |
| [`[neb]`](neb.md) | NEB endpoints plus traditional `.inp` geomeTRIC compatibility controls. |
| [`[pcm]`](pcm.md) | Reference-SCF PCM/ddX settings. |
| [`[symmetry]`](symmetry.md) | Point-group metadata and optional symmetry reductions. |
| [`[json]`](json.md) | Advanced JSON/restart metadata used by internal interfaces. |
| [`[tests]`](tests.md) | Regression-test expectation controls. |

## Documentation Rule

When an OpenQP pull request changes a default, accepted value, validation rule,
or workflow scope, update the matching keyword page in this documentation
repository before the next release.
