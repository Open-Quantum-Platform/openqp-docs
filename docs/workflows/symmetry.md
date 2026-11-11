# Molecular symmetry

OpenQP detects the molecular point group and its Abelian subgroup, labels
orbitals, excited states and normal modes with their irreducible
representations, and can optionally use symmetry to reduce the integral and
response work.

Detection is **on by default** (`[symmetry] enabled`). The reductions are not.

## What is on, and what that changes

| | Default | Changes the numbers? |
| --- | --- | --- |
| `enabled` — detection and labeling | `true` | Excited-state results and minimum-energy geometries, see below |
| `use_integral_symmetry` — petite-list reduction | `False` | Yes, and reorients the molecule |
| `use_response_symmetry` — residual projection | `False` | Yes (experimental) |

At a fixed geometry, the full integral list is used by default, and
reference-SCF or ordinary HF/DFT ground-state energies are identical to a run
with symmetry switched off. An MRSF physical `S0` is a
response root, not the reference-SCF energy, and can change when symmetry
information repairs response-block coverage.

## Preserving symmetry during geometry optimization

For a minimum-energy optimization of an isolated molecule with the default
OpenQP optimizer, the point group detected at the starting geometry is
preserved automatically. For example, a C3 structure can relax through all
displacements that preserve its threefold rotation. The optimizer projects
the gradient for step selection and convergence. The result file stores the
original Cartesian gradient, and the optimization settings in the log show
the preserved group and the number of allowed displacements.

No extra keyword is needed. Set `symmetry(enabled=false)` in a `.oqp` input to
allow symmetry breaking. This also disables symmetry detection and labeling.
The geometry constraint applies to native minimum-energy optimizations of
isolated molecules.

## C3 ROHF and ROKS reference orbitals

For an isolated C3 molecule, OpenQP preserves the closed and singly occupied orbital
spaces in ROHF and ROKS energy, gradient and native minimum-energy
optimization calculations. Each space can contain A orbitals and complete
real E pairs. If a restart or a fresh guess splits an E pair, OpenQP selects
complete symmetry subspaces close to the guess while retaining the alpha and
beta electron counts. DIIS diagonalizes the effective Fock matrix in the
A and E spaces and preserves their occupation counts. SOSCF and TRAH
restrict their orbital rotations to the C3-invariant subspace. The default
SCF escalation still tries DIIS, SOSCF and then TRAH as needed. The log
reports the solver and the final occupied-space symmetry residual.

The resulting energy is stationary within the selected C3 occupation.
Different C3 occupations can give different stationary solutions. For an
unrestricted search over spatial symmetry or to follow a user-selected
orbital occupation, set `symmetry(enabled=false)`.

## Why detection changes excited-state results

The Davidson solver starts from trial vectors that are single excitations
|Φ<sub>ia</sub>⟩, chosen by smallest orbital-energy gap. With point-group
symmetry the response matrix is block diagonal by irrep — the coupling between
two excitations vanishes unless they carry the same irrep:

```text
A(ia,jb) = 0    unless    G_i (x) G_a  =  G_j (x) G_b
```

where `G_p` is the irrep of orbital `p` and `(x)` is the direct product.

Each trial vector lies entirely inside one block, and Davidson expands with
preconditioned residuals, which never leave the block they start in. So a block
that receives no initial trial vector is never reached at all: its roots are
**absent from the spectrum**, not merely unconverged.

Nothing about the run looks wrong when this happens. It converges cleanly, to
the requested tolerance, in a normal number of iterations. But the surviving
Ritz values are renumbered 1, 2, 3, …, so every index **at or above the first
missing root** shifts down by the number of omissions preceding it — one if a
single root is missing, more when an unseeded block holds several. Roots below
the first omission keep their numbering, which is why the worked example below
moves state 3 while states 1 and 2 stay put. Every result selected by an
affected state index follows the shift:
excited-state gradients, geometry optimization, MECP/MECI searches, the
z-vector solve, NACME and NAMD.

(NMR shielding is not affected: it is a reference-SCF property requested with
`[properties] scf_prop=nmr` and carries no state index.)

With detection on, OpenQP *attempts* to cover every symmetry block that has
configurations in it, reassigning trial vectors so the otherwise-missing root
is found. It is an attempt rather than a guarantee: when no trial vector can be
safely reassigned, some blocks stay unseeded and OpenQP prints a warning naming
how many. See [Limits worth knowing](#limits-worth-knowing) below.

### A worked example

CH<sub>2</sub>O, 6-31G, ROHF triplet reference, MRSF-TDDFT, `nstate=3`. The
first three roots, in Hartree:

| | root 1 | root 2 | root 3 |
| --- | --- | --- | --- |
| `nstate=20` reference | −0.00500108 | 0.07496767 | **0.17574606** |
| `enabled=true` (default), `nstate=3` | −0.00500106 | 0.07496767 | **0.17574625** |
| `enabled=false`, `nstate=3` | −0.00500077 | 0.07496767 | **0.23436580** |

Without coverage the third root is never seeded, and what is reported as
"state 3" is actually the fourth root — an error of 0.0586 Hartree, or 1.60 eV.

This case ships as
`examples/MRSF-TDDFT/CH2O_MRSFTDDFT_SYMMETRY_BLOCK_COVERAGE`.

### Limits worth knowing

Covering each irrep once guarantees that block's **lowest** root. If two
requested roots share one block, the second can still be missed. Detection also
cannot help when:

- the molecule is C1, so there is only one block and nothing can be unreachable;
- any orbital comes back labeled `mixed`, e.g. a degenerate π pair in a linear
  molecule, in which case the irrep table is not built and the historical
  behavior applies;
- the trial set has no vector that can be safely reassigned, in which case
  OpenQP prints a warning naming the number of unseeded blocks.

The general safety check is unchanged and always worth doing: **re-run with a
larger `nstate` and confirm the energy of your target state does not move.**

## Reading the symmetry log

A run with detection on prints a block like:

```
   ==============================================
   PyOQP: molecular symmetry
   ==============================================
   detected point group : c2v
   abelian subgroup     : c2v
   response blocking    : pair_table_staged
   (per-pair irrep table staged for Davidson guess coverage only; the residual
    projection stays off -- [symmetry] use_response_symmetry)
```

`pair_table_staged` means the irrep table was built for trial-vector coverage
and the experimental residual projection is off. `active` means the projection
itself is running, which only happens under `use_response_symmetry`.

If the petite-list reduction was requested but did not engage, the block says so
explicitly rather than falling back silently — the C1 fallback gives a
numerically identical answer, so nothing else would reveal it:

```
   integral reduction   : skipped_basis_mismatch
   *** the petite-list reduction is NOT active: this run used the full (C1) integral list ***
```

## Labels

Orbital, state and mode labels are printed by default and are metadata only —
they never change a computed number.

- **Orbitals**: a symmetry table after the converged SCF. `label_mo=false`
  suppresses the table but not the underlying irreps, which the trial-vector
  coverage needs.
- **States**: excited states are labeled by irrep, and as spin-resolved terms
  (`1A1`, `3B2`) when `[tdhf] multiplicity` is set.
- **Normal modes**: a `Symmetry` column in the frequency table, including for a
  cached Hessian read back with `[hess] read=true`.

An orbital or state that cannot be assigned within tolerance is reported as
`mixed` rather than guessed.

## Turning it off

```
[symmetry]
enabled=false
```

This restores the pre-detection behavior in full: no labels, no irrep table, and
excited-state trial vectors chosen purely by orbital-energy gap.

## See also

- [`[symmetry]` keywords](../keywords/symmetry.md)
- [MRSF-TDDFT](mrsf-tddft.md)
- [Hessian and Frequencies](hessian.md)
