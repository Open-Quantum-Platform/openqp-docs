# Ethylene with SF-TDDFT: Spin Contamination

Spin-flip TDDFT (SF-TDDFT) starts, like MRSF-TDDFT, from a high-spin triplet
reference and flips one spin to reach the singlet ground state and excited
states. Its response states, however, are not guaranteed to be pure singlets or
triplets. This example repeats the [ethylene twist](ethylene-twist.md) with
SF-TDDFT and uses ⟨S²⟩ to identify the spin of each root, which shows why
MRSF-TDDFT was developed.

<div class="oqp-figs" markdown>
<figure markdown>
![Planar ethylene](../assets/worked-examples/mol-ethylene.png)
<figcaption>Planar ethylene (0°)</figcaption>
</figure>
<figure markdown>
![Twisted ethylene](../assets/worked-examples/mol-ethylene-twisted.png)
<figcaption>Twisted ethylene (90°)</figcaption>
</figure>
</div>

## Copy and run

```text title="ethylene-planar-sf.oqp"
sf(nstate=4)/bhhlyp/6-31g*
geom="""
C      0.000000     0.000000     0.664311
C      0.000000     0.000000    -0.664311
H      0.000000     0.923944     1.237411
H      0.000000    -0.923944     1.237411
H      0.000000     0.923944    -1.237411
H      0.000000    -0.923944    -1.237411
"""
```

[Download ethylene-planar-sf.oqp](inputs/ethylene-planar-sf.oqp) ·
[ethylene-twisted-sf.oqp](inputs/ethylene-twisted-sf.oqp) (the 90° geometry
from the [twist example](ethylene-twist.md))

```bash
openqp ethylene-planar-sf.oqp
```

`sf(nstate=4)` requests four spin-flip roots. The geometry and the
BHHLYP/6-31G* level are the same as in the MRSF twist example, so the two
methods can be compared directly. Each run takes about 2 seconds. For the full
scan, use the script on the [twist page](ethylene-twist.md) with the first line
`sf(nstate=4)/bhhlyp/6-31g*`.

## What you get

SF-TDDFT prints a summary table with ⟨S²⟩ for every root. For planar ethylene:

```text
 State      Energy       Excitation   Excitation(eV)  <S^2>         Transition dipole moment, a.u.        Oscillator
           Hartree           eV          rel. GS                  X          Y          Z        Abs.      strength
   1    -78.5258933521    -4.269938     0.000000      0.004     0.0000     0.0000     0.0000     0.0000      0.0000
   0    -78.3689760267     0.000000     4.269938        (ROHF/UHF Reference state)
   2    -78.3414039996     0.750273     5.020211      1.999     0.0000     0.0000    -0.0000     0.0000      0.0000
   3    -78.2207343818     4.033861     8.303799      1.005    -0.0000     0.0000     0.0000     0.0000      0.0000
   4    -78.2183549845     4.098607     8.368545      0.012     0.0000     0.0000    -0.0000     0.0000      0.0000
```

State 0 is the high-spin triplet reference, not a response root. The roots
are numbered by energy, whatever their spin: ⟨S²⟩ ≈ 0 means a singlet,
⟨S²⟩ ≈ 2 a triplet, and a value in between a mixture of the two.

| Root | Planar (0°) | ⟨S²⟩ | Twisted (90°) | ⟨S²⟩ |
| --- | --- | --- | --- | --- |
| 1 | 0.000 eV | 0.004 (S0) | −78.3961119 hartree | 1.999 (triplet) |
| 2 | 5.020 eV | 1.999 (triplet) | −78.3957383 hartree | 0.007 (S0) |
| 3 | 8.304 eV | **1.005 (mixed)** | 2.19 eV above root 2 | 0.053 |
| 4 | 8.369 eV | 0.012 | 2.25 eV above root 2 | 0.055 |

![SF-TDDFT roots along the twist, coloured by S^2](../assets/worked-examples/plot-sf-twist.svg)

The coloured points are the four SF roots at each angle, coloured by ⟨S²⟩; the
dashed lines are MRSF-TDDFT S0 and S1 from the [twist example](ethylene-twist.md).

## Reading the result

- **The SF ground state is fine.** SF root 1 at 0° (−78.5258934 hartree) and
  the singlet root at 90° (−78.3957383 hartree) agree with MRSF-TDDFT S0
  (−78.5257616 and −78.3957310 hartree) to within 0.13 millihartree.
- **Some SF roots are half singlet, half triplet.** At the planar geometry
  root 3 has ⟨S²⟩ = 1.005, and between 15° and 45° roots 3 and 4 have
  ⟨S²⟩ between 0.1 and 1.0. Such a root is not a physical state: its energy and
  properties mix those of a singlet and a triplet. MRSF-TDDFT removes this
  spin contamination by construction: its S1 (dashed line) has ⟨S²⟩ ≤ 0.003
  at every angle.
- **Root order changes with spin.** At 90° the triplet falls below the singlet,
  so root 1 is the triplet and S0 is root 2. Because the spin of a root is known
  only after the calculation, SF state-specific inputs use root numbers,
  for example `grad(root=2)`, never `S0` or `T1`; see
  [SF-TDDFT](../workflows/sf-tddft.md).

## Try next

- Compute the gradient of a chosen root after checking its ⟨S²⟩ in an energy
  run at the same geometry: for the twisted input, `grad(root=2)` gives the
  gradient of the singlet S0.
- Compare with `mrsf(nstate=3)/bhhlyp/6-31g*` at the same geometry, which
  returns only singlets (S0, S1, S2), and with `energy(T0)` for the triplets.

See also: [SF-TDDFT](../workflows/sf-tddft.md),
[MRSF-TDDFT](../workflows/mrsf-tddft.md).
