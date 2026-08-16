# CASSCF Nuclear Gradient

OpenQP computes the nuclear gradient of a **state-specific** CASSCF energy
analytically. Set `[input] method=casscf` and `runtype=grad`; the gradient is
taken for the root the orbitals were optimized for, `[casscf] root`.

The analytic path replaces the `6 * natom` displaced CASSCF calculations a
central difference needs with one CI solve at the converged orbitals plus one
pass of derivative integrals, so its cost stops growing with the number of
nuclei. It is also free of a failure mode the numerical route has: each
displaced CASSCF run is an independent chance to converge onto a different
solution branch, and nothing in a numerical gradient says that it did.

## Energy expression

With `x` a nuclear coordinate and the superscript `x` a derivative of the AO
integrals at fixed MO coefficients,

```text
dE/dx = sum D^AO h^x + 1/2 sum Gamma^AO (..|..)^x - sum X^AO S^x + dV_NN/dx
```

where `D^AO = C D C^T` is the spin-summed one-particle density, `X^AO = C F C^T`
is the energy-weighted density built from the generalized Fock matrix, and
`Gamma^AO` is the two-particle density.

There is **no orbital-response (Z-vector) term and no CI-response term**. That
is a consequence of full variationality, and it holds only because a converged
state-specific CASSCF solution is stationary with respect to every wavefunction
parameter:

- the CI vector is an eigenvector of the active Hamiltonian at the current
  orbitals — true of an excited root as well, since a stationary point need not
  be a minimum;
- the non-redundant orbital-rotation gradient is what the optimizer drove to
  zero;
- rotations *within* the inactive, active and virtual blocks leave the energy
  invariant, the active block because the CI spans the full CAS.

This is a different object from the orbital-rotation gradient the optimizer
reports as `|g_orb|`. That gradient vanishing is the **precondition** for the
expression above, not an approximation of it.

## Convergence matters more than usual

The gradient error at a non-stationary point is **first order** in `|g_orb|`, so
a loosely converged orbital optimization gives a plausible-looking but wrong
gradient. Converge tighter than you would for an energy:

```ini
[casscf]
gradient_norm_tol=1.0e-7
```

Every gradient run prints its own stationarity diagnostics, and the driver
refuses to return a gradient when `|g_orb|` exceeds
`max(1e-4, 100 x [casscf] gradient_norm_tol)`:

```text
 Differentiated root                        0
 Orbital-rotation gradient norm        2.02955556E-08
 Generalized Fock asymmetry            6.17901000E-09
 Active 2-RDM correction vectors           10
```

`Generalized Fock asymmetry` is `max |F_pq - F_qp|`; the generalized Fock matrix
is symmetric at a stationary point, so a large value is a second, independent
warning that the run was not converged. `Active 2-RDM correction vectors` is the
rank of the all-active two-particle correction (see
[Implementation notes](#implementation-notes)).

## Running it

### `.oqp`

```text
casscf/sto-3g
grad
guess(type=hcore)
scf(conv=1e-10,maxit=80,forced_attempt=3,save_molden=false)
properties(scf_prop="")
cas(active_electrons=4,active_orbitals=4,frozen_core=3,orbital_source=rhf,sort_orbitals=energy,max_det=5000,max_memory=512)
casscf(max_macro_iterations=50,optimizer=newton,root=0,gradient_norm_tol=1e-07,energy_decrease_tol=1e-10,step_norm_tol=1e-08,max_rotation_norm=0.2,level_shift=0.001,canonicalize=true)
ci(nroot=1,solver=dense,eig_tol=1e-10,integral_backend=native,target_spin=any,root_tracking=energy)
geom="../geometries/H2O-95fa99c614ed.xyz"
```

Runnable inputs:
[`examples/WF_methods/H2O_CASSCF_CAS44_grad.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/WF_methods/H2O_CASSCF_CAS44_grad.oqp)
and
[`examples/WF_methods/H4_CASSCF_CAS22_ROOT1_grad.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/WF_methods/H4_CASSCF_CAS22_ROOT1_grad.oqp),
each with a same-stem legacy `.inp` companion.

### Python

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_casscf_grad", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.casscf(active_electrons=4, active_orbitals=4, frozen_core=3,
           basis="sto-3g", runtype="grad", gradient_norm_tol=1.0e-7)

mol = job.run()
print("gradient:", mol.get_results()["gradient"])
```

`root=1` selects an excited root; the helper widens `[ci] nroot` itself so the
requested root is solved for. The returned gradient still occupies public
array slot `0`; `[properties] grad` is an array selector, not the physical CI
root number.

### Excited roots

`[casscf] root` selects the objective the orbitals are optimized for, and the
gradient follows it. On a symmetry-free H4 chain at STO-3G, the two roots give
genuinely different energies **and** genuinely different gradients, each of
which reproduces its own finite difference:

| `[casscf] root` | Energy (Ha) | `max abs(analytic - 5-point O(h^4) FD)` |
| ---: | ---: | ---: |
| `0` | `-2.1174290487` | `6.9e-10` |
| `1` | `-1.7712058509` | `4.4e-09` |

## Geometry optimization

Because `runtype=grad` is analytic, gradient-driven optimizers run on CASSCF
without a numerical-gradient inner loop. Use `runtype=optimize` with the same
`[cas]`, `[ci]` and `[casscf]` sections. Keep `gradient_norm_tol` tight for
every point, not only the first. State-specific CASSCF publishes one gradient
row, so the optimizer selector must be zero even for an excited physical root:

```ini
[casscf]
root=1

[optimize]
istate=0
```

A runnable ground-state example is
[`examples/WF_methods/LiH_CASSCF_optimize.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/WF_methods/LiH_CASSCF_optimize.inp).

## Scope and what is refused

Implemented: the state-specific gradient of the root selected by
`[casscf] root`, for `method=casscf` on a closed-shell RHF reference with the
contiguous inactive/active/virtual partition the native CASSCF driver uses.

The analytic path refuses the following cases rather than silently applying an
invalid formula:

- **`sa-casscf`, or `[state_average] enabled=true`.** A state-averaged run
  optimizes `sum_I w_I E_I`. The individual state's energy is *not* stationary
  with respect to the orbital rotations — the averaged sum is — so an individual
  SA-state gradient needs a Lagrangian/Z-vector response that is not
  implemented. OpenQP routes the public SA-CASSCF gradient workflow to central
  differences; the analytic entry point itself refuses this wavefunction.
- **`[properties] grad` other than `0`.** State-specific CASSCF publishes one
  array row. Select the physical state with `[casscf] root`, while keeping the
  gradient-array selector at zero.
- **A non-Hartree-Fock Hamiltonian.** Leave `[input] functional` empty.
- **A non-contiguous active space.**
- **`method=casci`.** Its orbitals are not optimized, so it needs the
  orbital-response term this derivation drops.

Full active spaces with no non-redundant orbital rotations are supported: their
orbital-gradient norm is exactly zero by construction. An excited-root
Davidson calculation with an explicit subspace is also supported even when its
energy optimization used the Python fallback; gradient eligibility is assessed
independently of native energy-driver eligibility.

Not implemented, and deliberately not claimed: an *analytic* gradient of the
averaged SA-CASSCF objective (the same expression on weight-averaged RDMs) or
analytic individual SA-state gradients (which require the Z-vector solve).

For `optimize`, `ts`, `mep`, and `irc`, use `[cas] orbital_source=rhf`.
JSON-sourced coefficients are fixed in the AO basis at one geometry and are no
longer orthonormal in the AO metric after the nuclei move.

## Implementation notes

`Gamma^AO` splits into a separable part plus an all-active correction. The
separable part, symmetrized over `mu <-> nu`, is exactly `4x` the Hartree-Fock
two-particle density expression evaluated at the CASSCF AO density, so it reuses
that kernel term for term.

The correction is not separable, and a `nbf^4` AO tensor is neither necessary
nor affordable. Symmetrized over the eight-element permutation group of
`(tu|vw)` it is a symmetric `nact^2 x nact^2` matrix, so its eigendecomposition

```text
dGamma_{mu nu la si} = sum_k lambda_k A^k_{mu nu} A^k_{la si},   A^k = C_act V^k C_act^T
```

turns it into at most `nact(nact+1)/2` separable products of ordinary symmetric
AO matrices — the rank printed as `Active 2-RDM correction vectors`. Storage is
`O(nact(nact+1)/2 x nbf_cart^2)` instead of `nbf_cart^4`.

The symmetry petite list is deliberately **not** used. It is valid only for a
totally symmetric contracted density, which the state-specific two-particle
density of an arbitrary root does not guarantee — a spatially degenerate root in
an abelian subgroup is the counterexample. The cost of declining is speed; the
cost of opting in wrongly would be a wrong gradient.

### Cost

Measured on an M3 Ultra with the default thread count, the analytic gradient
adds 3-10% to the wall time of the corresponding `runtype=energy` run and
1-21 MB to its peak resident set; the CASSCF orbital optimization dominates
both. Within the gradient itself, roughly 70-76% is the shared derivative-ERI
kernel and 20-23% is OpenMP load imbalance in the derivative-integral driver,
so the two-particle density assembly specific to CASSCF is a single-digit
percentage even at CAS(10,10).

The all-active correction is linear in its rank: at a fixed cc-pVDZ basis the
two-electron gradient step grows about 4.8 ms per correction vector, which is
1.3% of that step at CAS(4,4) and 6.8% at CAS(10,10).

## Verification

The implementation is checked against a **five-point O(h^4)** finite-difference
stencil at `h = 1e-3` bohr. The usual two-point O(h^2) difference is not
accurate enough here: along a bond-stretching coordinate the third energy
derivative is large enough that its truncation error alone reaches ~1e-5, which
is indistinguishable from a real defect.

| System | Root | `max abs(analytic - FD)` | `max abs(sum_A dE/dR_A)` |
| --- | ---: | ---: | ---: |
| H2O/STO-3G CAS(4,4) | 0 | `4.1e-09` | `2.3e-14` |
| H4/STO-3G CAS(2,2), symmetry-free | 0 | `6.9e-10` | `1.4e-15` |
| H4/STO-3G CAS(2,2), symmetry-free | 1 | `4.4e-09` | `5.0e-16` |
| H2O/cc-pVDZ CAS(6,6) | 0 | `6.2e-08` | `1.2e-13` |

The last row is converged to `gradient_norm_tol=1e-6` rather than `1e-7`; since
the gradient error is first order in `|g_orb|`, `6e-8` is what that convergence
buys.

Translational invariance, `max abs(sum_A dE/dR_A)`, is the sharpest cheap check
available on the Pulay and two-particle terms — the Hellmann-Feynman part alone
would not satisfy it.

!!! warning "A numerical CASSCF reference can silently mix solution branches"

    When cross-checking against a finite difference yourself, sample the energy
    along the coordinate and confirm it is smooth before treating a disagreement
    as a gradient defect. Three separate geometries produced finite-difference
    "failures" during development that were not gradient errors at all: a
    displaced point converging 0.024 Ha higher, a symmetric geometry sitting on
    a branch 8.3e-6 Ha above the one the displaced points fall onto, and an
    out-of-plane displacement that reordered nearly degenerate reference
    orbitals across the `[cas] sort_orbitals=energy` active-space boundary and
    so selected a different active space.

## See also

- [Wavefunction methods](../keywords/wavefunction.md) — `[cas]`, `[ci]`,
  `[casscf]` and `[state_average]` keywords.
- [Optimization](optimization.md) — gradient-driven geometry optimization.
- [Hessian and Frequencies](hessian.md) — second derivatives.
