# Keyword Reference

This chapter is the book-style reference for OpenQP input keywords. Workflow
pages show complete input decks; this chapter explains what each keyword means,
what type of value it expects, what default the parser applies, and which
workflow constraints are enforced by the input checker.

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

State numbering is workflow dependent. HF/DFT reference-state properties usually
use state `0`; TDHF, TDDFT, SF-TDDFT, and MRSF-TDDFT excited states use positive
state indices.

## Section Index

| Section | Purpose |
| --- | --- |
| [`[input]`](input.md) | Global calculation setup, geometry, run type, AO convention, threading. |
| [`[guess]`](guess.md) | Initial orbitals, restart files, and MO swaps. |
| [`[scf]`](scf.md) | Reference type, convergence controls, pFON, TRAH, fallback manager. |
| [`[dftgrid]`](dftgrid.md) | DFT quadrature and hybrid/range-separated functional controls. |
| [`[tdhf]`](tdhf.md) | TDHF/TDDFT/SF/MRSF/UMRSF response settings. |
| [`[properties]`](properties.md) | Gradients, NMR, export, and property requests. |
| [`[hess]`](hess.md) | Hessian, frequency, and thermochemistry controls. |
| [`[nac]`](nac.md) | NAC and NACME state-pair controls. |
| [`[ekt]`](ekt.md) | MRSF-EKT IP/EA channel selection. |
| [`[optimize]`](optimize.md) | Target state and optimization convergence controls. |
| [`[oqp]`](oqp.md) | Native optimizer controls. |
| [`[geometric]`](geometric.md) | geomeTRIC optimizer backend controls. |
| [`[neb]`](neb.md) | NEB product endpoint and image count. |
| [`[pcm]`](pcm.md) | Reference-SCF PCM/ddX settings. |
| [`[symmetry]`](symmetry.md) | Point-group metadata and optional symmetry reductions. |

## Documentation Rule

When an OpenQP pull request changes a default, accepted value, validation rule,
or workflow scope, update the matching keyword page in this documentation
repository before the next release.
