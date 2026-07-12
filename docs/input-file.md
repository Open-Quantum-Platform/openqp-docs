# Input File Format

!!! warning "Development / next release"

    The one-line `.oqp` parser belongs to the current development branch, not
    the published OpenQP 1.2.0 release documented by this site. Traditional
    `.inp` input below remains the released format.

OpenQP accepts two complementary text formats. New inputs can use a compact
`.oqp` file with one readable line:

```text
mrsf/bhhlyp/6-31g* h2o.xyz opt
```

This means an MRSF-TDDFT optimization of `S0`; OpenQP selects the required
working reference automatically. Start with the [`.oqp` Quick
Start](oqp-input.md#quick-start) for state labels, SOC counts, and more
examples.

Traditional `.inp` files use the sectioned format documented on this page and
remain supported unchanged. Keep sectioned syntax in `.inp` and one-line syntax
in `.oqp`; changing formats is optional. The correction assistant is a
secondary aid that produces an inspectable `.resolved.oqp` file, while the
resolved one-line command remains the authoritative calculation record.
OpenQP renders the short positional geometry above as the explicit canonical
spelling `geom="h2o.xyz"`.

The two formats intentionally expose different optimization detail. Concise
`.oqp` geometry drivers always use the native OpenQP engine and have no `lib`
selector. Traditional `.inp` files retain `[optimize] lib=oqp`,
`lib=geometric`, or `lib=scipy` for compatibility; geomeTRIC is an optional
legacy dependency used chiefly for constrained optimization.

OpenQP inputs are INI-like text files. Options are grouped by section:

```ini
[input]
runtype=energy
method=hf
basis=6-31g*

[scf]
type=rhf
```

Lines beginning with `#` are comments. Keyword names are case-insensitive in
normal use, but this manual uses lower-case names to match the Python schema.

## Geometry

Inline coordinates are written under `[input] system` with indented atom lines:

```ini
[input]
system=
   O   0.000000000   0.000000000  -0.041061554
   H  -0.533194329   0.533194329  -0.614469223
   H   0.533194329  -0.533194329  -0.614469223
```

An external XYZ file can be used instead:

```ini
[input]
system=h2o.xyz
```

Some workflows, such as NACME, also use `[input] system2` for the displaced or
previous geometry.

## Core Sections

| Section | Purpose |
| --- | --- |
| `[input]` | Charge, basis, method, run type, geometry, AO convention, threading. |
| `[guess]` | Initial orbitals and restart data. |
| `[scf]` | RHF/ROHF/UHF reference and SCF convergence controls. |
| `[mp2]` | Standalone MP2 spin-scaling controls. |
| `[dftgrid]` | DFT functional/grid controls. |
| `[tdhf]` | TDHF, TDDFT, SF-TDDFT, MRSF-TDDFT, and UMRSF settings. |
| `[dftb]` | DFTB backend, SCC, response, and MRSF-TDDFTB controls. |
| `[md]` | Nonadiabatic-dynamics controls used by `runtype=namd`. |
| `[qmmm]` | OpenMM QM/MM system and molecular-dynamics controls. |
| `[properties]` | Gradients, NAC, NMR, export, and property requests. |
| `[optimize]` | Geometry target and convergence controls; backend selection is retained for traditional `.inp` and Python compatibility. |
| `[oqp]` | Native optimizer, TS-Hessian, IRC, MEP, and NEB controls. |
| `[geometric]` | Optional legacy geomeTRIC controls for traditional `.inp` workflows. |
| `[pcm]` | Reference-SCF PCM/ddX energy settings. |
| `[symmetry]` | Point-group metadata and optional symmetry reductions. |
| `[hess]` | Hessian and frequency controls. |
| `[nac]` | NAC/NACME controls. |
| `[ekt]` | MRSF-EKT IP/EA channel selection. |
| `[neb]` | NEB product/image controls plus optional legacy geomeTRIC compatibility keys. |
| `[json]` | Advanced JSON/restart metadata. |
| `[tests]` | Internal regression-test expectations. |

## Run Types

Common `[input] runtype` values:

| Run type | Meaning |
| --- | --- |
| `energy` | Single-point energy and requested properties. |
| `grad` | Energy plus gradient for the requested state. |
| `hess` | Hessian/frequency workflow. |
| `nac`, `bp` | Numerical nonadiabatic-coupling vector and branching-plane workflows. |
| `nacme` | Time/geometric derivative coupling between MRSF states. |
| `soc` | MRSF-TDDFT, MRSF-TDHF, or MRSF-TDDFTB spin-orbit coupling workflow. |
| `ekt` | MRSF-EKT ionization-potential/electron-affinity workflow. |
| `md` | Ground-state QM/MM molecular dynamics. The command-line runner dispatches this OpenMM path specially. |
| `namd` | Nonadiabatic molecular dynamics using `[md]` controls. |
| `optimize` | Geometry optimization. |
| `meci`, `mecp`, `tci` | Crossing-point searches. |
| `ts`, `irc`, `neb`, `mep` | Reaction-path workflows. |
| `prop`, `data` | Multi-state property/gradient workflows for downstream drivers. |

For QM/MM MD, use `[qmmm] n_steps=N`. The older `[qmmm] nsteps=N` keyword
remains available for legacy bookkeeping. Canonical `qmmm(...)` may accompany
`energy`, `md`, or `namd`; `md` requires it, while `namd` may also run gas
phase. Canonical QM/MM gradients and optimizations are rejected until their
active backends provide the required assembled gradient.

The ordinary `Runner` validator still classifies bare `runtype=md` as
unavailable; the command-line runner recognizes `qmmm_flag=true` plus
`runtype=md` before constructing `Runner` and dispatches the OpenMM driver.
Use `openqp file.inp --nompi` for this legacy ground-state QM/MM-MD path.

Standalone MP2 is selected with `[input] method=mp2`, uses only
`runtype=energy`, and requires an empty `[input] functional`. Spin-scaled MP2
variants are controlled by the optional `[mp2]` section.
