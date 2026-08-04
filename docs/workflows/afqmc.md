# AFQMC

!!! warning "Companion development build required"
    This workflow is not part of the OpenQP 1.2.0 package installed by
    `pip install openqp`. It requires the companion
    [`openqp-afqmc` development branch](https://github.com/Open-Quantum-Platform/openqp-afqmc/pull/1).
    Clone that repository and build the branch documented by the pull request
    before running the examples on this page. The normal OpenQP 1.2.0 executable
    does not recognize `[input] method=afqmc` or the `afqmc(...)` section call.

OpenQP implements phaseless auxiliary-field quantum Monte Carlo (ph-AFQMC) as
an energy workflow. The calculation rewrites the two-electron interaction as a
sum over Cholesky vectors, samples the resulting auxiliary fields with a walker
population, and uses a trial wavefunction for importance sampling and the
phaseless constraint.

The reported production quantity is the block-averaged mixed estimator,

```text
E_mixed = <Psi_T|H|Psi(beta)> / <Psi_T|Psi(beta)>.
```

The trial controls the phaseless bias and state selectivity. Increasing the
projection time or walker population reduces statistical and population-control
errors, but it does not remove a systematic error caused by an unsuitable
trial.

## Mean-field trial

A small ground-state calculation can start from the converged SCF determinant:

```text
afqmc/sto-3g
energy
afqmc(walkers=64,steps=200,dt=0.005,seed=7)
geom="h2.xyz"
```

Legacy input uses `[input] method=afqmc` and `[afqmc] trial=mean_field`.

## OpenQP MRSF-CSF trial

For a state-specific singlet trial, OpenQP first solves the requested native
MRSF Davidson problem. Its converged vector `X_I` is already expressed in the
MRSF CSF basis. AFQMC therefore does not solve another eigenvalue problem and
does not spin-adapt `X_I` again.

At the boundary to the Slater-based AFQMC kernels:

- `G` and `D` are one-component closed-shell CSFs.
- Every other independent MRSF singlet CSF has a fixed pair of spin-inverted
  Slater components.
- The OpenQP CSF phase convention, including the canonical orbital-column
  phase, is applied while materializing those components.
- Thresholding and normalization happen in CSF space, so the two components of
  one CSF never propagate as independently adjustable trial coefficients.

The walkers themselves remain ordinary orbital matrices. Overlap, force bias,
and local energy contract against all fixed trial components.

```text
mrsf(nstate=3)/bhhlyp/cc-pvdz
energy
afqmc(
  trial=mrsf_state,
  state=2,
  channels="oo+ov",
  nvirtual=2,
  walkers=256,
  steps=2000,
  dt=0.005
)
geom="butadiene.xyz"
```

The current in-memory `mrsf_state` route is fail-closed for non-singlet target
roots and does not accept UMRSF roots. It also does not impose an expected ordering between states; state
ordering is a calculated result.

## Selecting OO, CO, OV, and CV

Let `C` denote doubly occupied orbitals below the two open-shell orbitals `O`,
and let `V` denote virtual orbitals. The selectable trial channels are:

| Channel | Source | Destination |
| --- | --- | --- |
| `OO` | open | open |
| `CO` | closed | open |
| `OV` | open | virtual |
| `CV` | closed | virtual |

Start with `OO`, the default, and enlarge the space deliberately. Useful
sequences include `OO`, `OO+OV`, `OO+CO+OV`, and `all`. `ncore` keeps the
highest `C` orbitals nearest the open-shell pair; `nvirtual` keeps the lowest
`V` orbitals. `-1` means all available orbitals in that class.

OpenQP prints the number of retained CSFs and available CSFs in every channel,
the number of Slater components delivered to the kernel, and the trial
`<S^2>`. The current `CV` representation can retain the known MRSF residual
spin contamination; inspect the printed diagnostic when `CV` is enabled.

## Exact H2 validation

H2/STO-3G is a compact exact oracle for the singlet OO path. With two electrons
in two spatial orbitals, the three singlet OO CSFs span the complete singlet
FCI space. A correct implementation must pass three independent checks:

1. The total energies of the three native MRSF-TDHF Davidson roots equal the
   three singlet FCI eigenvalues.
2. After the fixed OpenQP CSF phases are applied, each root has unit overlap
   with the matching FCI eigenvector, up to an arbitrary global sign.
3. Using each exact root as the AFQMC trial makes the mixed local energy equal
   to that FCI eigenvalue at every propagation step, not merely in the final
   average.

At an H--H distance of 0.74 angstrom, the OpenQP STO-3G regression values are:

| Singlet state | FCI and AFQMC mixed energy (Hartree) |
| --- | ---: |
| `S0` | `-1.137283834652` |
| `S1` | `-0.168352441679` |
| `S2` | `0.483142657390` |

This exact test validates OO enumeration, root selection, CSF coefficients,
relative phases, spin pairing, Cholesky Hamiltonian construction, and the mixed
estimator. It does not by itself validate the physical adequacy of a truncated
CO/OV/CV trial for a larger molecule.

## Production convergence

For a molecule such as butadiene, use independent numerical gates rather than
an assumed state ordering:

1. Extend the projection time until matched late-beta windows agree within
   uncertainty and show no residual drift.
2. Repeat with independent random seeds.
3. Compare at least two walker populations over the identical beta window.
4. Reduce the time step when time-step bias is material at the target accuracy.
5. Enlarge the CSF space in a controlled sequence such as `OO`, `OO+OV`, then
   `OO+CO+OV`; add `CV` only with its spin diagnostic checked.
6. Check the MRSF Davidson residuals and root character before attributing an
   AFQMC change to projection rather than to a changed trial.

Do not publish a diagnostic value as a converged energy until the projection,
seed, and population checks have passed. See [`[afqmc]`](../keywords/afqmc.md)
for every input keyword.
