# Benzene: Molecular Symmetry

OpenQP detects the point group of every input structure automatically. It uses
the symmetry to label orbitals, states, and vibrations, and to skip integrals
that are related by symmetry. Nothing has to be requested; this example shows
what the detection reports and how much time it saves for benzene.

<div class="oqp-figs" markdown>
<figure markdown>
![Benzene](../assets/worked-examples/mol-benzene.png)
<figcaption>Benzene</figcaption>
</figure>
</div>

![Run time with and without symmetry](../assets/worked-examples/plot-benzene-symmetry.svg)

## Copy and run

```text title="benzene-hf-sym.oqp"
hf/cc-pvtz
geom="""
C      1.392883     0.000000     0.000000
C      0.696465     1.206259     0.000000
C     -0.696465     1.206259     0.000000
C     -1.392883     0.000000     0.000000
C     -0.696465    -1.206259     0.000000
C      0.696465    -1.206259     0.000000
H      2.479666     0.000000     0.000000
H      1.239913     2.147463     0.000000
H     -1.239913     2.147463     0.000000
H     -2.479666     0.000000     0.000000
H     -1.239913    -2.147463     0.000000
H      1.239913    -2.147463     0.000000
"""
```

[Download benzene-hf-sym.oqp](inputs/benzene-hf-sym.oqp) ·
[benzene-hf-nosym.oqp](inputs/benzene-hf-nosym.oqp) (the same input with
`symmetry(enabled=false)` added to the first line)

```bash
openqp benzene-hf-sym.oqp
```

A Hartree–Fock single point with 264 basis functions (cc-pVTZ). With 8 threads
the run takes 28 seconds with symmetry and 95 seconds without.

## What you get

The log starts with the symmetry metadata:

```text
   PyOQP symmetry status:                      enabled
   PyOQP symmetry detected point group:        d2h
   PyOQP symmetry label MO:                    yes
   PyOQP symmetry use integral symmetry:       yes
   PyOQP symmetry tolerance:                   1e-05
```

and the integral setup reports `integral reduction : active (|G| = 8, abelian
subgroup)` with symmetry and `skipped_no_detection` without it. Each orbital
then carries its symmetry label:

```text
   point group:      d2h
   SCF state:        1AG
   alpha MOs:
      ...
      19       -0.49236470  ag
      20       -0.33561499  b2g
      21       -0.33559202  b3g
      22        0.12872521  au
```

| | Symmetry on (default) | `symmetry(enabled=false)` |
| --- | --- | --- |
| Energy | −230.7791170133 hartree | −230.7791170135 hartree |
| SCF iterations | 9 | 9 |
| Wall time (8 threads) | 27.7 s | 95.4 s |

## Reading the result

- **Same answer, 3.4 times faster.** Using the eight operations of D2h, OpenQP
  computes only the symmetry-unique two-electron integrals; the energies agree
  to 2 × 10⁻¹⁰ hartree.
- **Labels come with the run.** The two highest occupied orbitals, 20 (b2g) and
  21 (b3g), differ in energy by only 2 × 10⁻⁵ hartree: they are the two
  components of the degenerate π orbital pair of benzene, labelled in the
  abelian subgroup D2h that OpenQP uses.
- **Detection uses a tolerance** (`symmetry tolerance: 1e-05` in the log), so
  the coordinates must be symmetric to that precision; for these coordinates,
  rounded to six decimals after an optimization, OpenQP reports D2h. Starting
  from symmetric coordinates keeps the symmetry through an optimization, as in
  the [water](water-scf.md) and [formaldehyde](formaldehyde-opt-freq.md)
  examples.
- Symmetry speeds up the integral-heavy parts; the TDDFT response steps of the
  [UV example](formaldehyde-uv.md) do not use it (`use response symmetry: no`).
  A benzene TDDFT run took 20.8 s with and 20.9 s without symmetry.

## Try next

- Add `symmetry(enabled=false)` to another input and compare the run time.
- Start from exactly symmetric coordinates (for example, generated from bond
  lengths and angles) and check the detected group in the log.

See also: [Molecular Symmetry](../workflows/symmetry.md),
[`symmetry` keywords](../keywords/symmetry.md).
