# Two-electron integrals in SCF

OpenQP 1.4 uses the Head-Gordon–Pople (HGP) recurrence by default for
eligible two-electron repulsion integrals in the SCF Fock build. The choice
is made separately for each shell quartet:

| Shell quartet | Integral evaluation |
| --- | --- |
| All four shells are s, p, or d | Rotated-axis integrals |
| At least one f, g, or h shell, with total angular momentum at most 16 | HGP for the full Coulomb operator when the shells with angular momentum at least 2 all use the same Cartesian or spherical representation |
| Other quartets above d, including `(hh\|hh)`, mixed representations, and range-separated integrals | Rys quadrature in the native build |

Here the total angular momentum is the sum over all four shells. For example,
`(hh|hh)` has total angular momentum 20 and uses Rys quadrature even with HGP
enabled.

The `scf` option `eri_hgp=auto` is the default. To evaluate the same SCF model
with Rys quadrature for the quartets that would use HGP, set `eri_hgp=off`:

```text
rhf/cc-pvtz energy
geom="water.xyz"
scf(eri_hgp=off)
```

For legacy input, set `eri_hgp=off` in `[scf]`. The setting leaves the
rotated-axis integrals unchanged. It does not select an HGP algorithm for
analytic two-electron derivatives. When the Fock build computes HGP
quartets, the calculation log includes `HGP ERI quartets computed:` and a count.
