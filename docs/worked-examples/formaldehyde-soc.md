# Formaldehyde: Spin-Orbit Coupling

Spin-orbit coupling (SOC) mixes singlet and triplet states and controls the rate
of intersystem crossing and phosphorescence. This example computes the
singlet and triplet states of formaldehyde with MRSF-TDDFT and the SOC matrix
elements between them, including the one-electron spin-orbit term and a
mean-field treatment of the two-electron term. The result shows El-Sayed's rule directly.

<div class="oqp-figs" markdown>
<figure markdown>
![Formaldehyde](../assets/worked-examples/mol-hcho.png)
<figcaption>Formaldehyde at the PBE0/6-31G* geometry</figcaption>
</figure>
<figure markdown>
![n orbital](../assets/worked-examples/orb-hcho-homo.png)
<figcaption>n (b2): the lone pair excited in the nπ* states</figcaption>
</figure>
<figure markdown>
![pi* orbital](../assets/worked-examples/orb-hcho-side-lumo.png)
<figcaption>π* (b1): the orbital that receives the electron</figcaption>
</figure>
</div>

## Copy and run

```text title="formaldehyde-soc.oqp"
mrsf(nstate=3)/bhhlyp/6-31g* soc
geom="""
C      0.000000     0.000000    -0.526342
O      0.000000     0.000000     0.676110
H      0.000000     0.937620    -1.119884
H      0.000000    -0.937620    -1.119884
"""
```

[Download formaldehyde-soc.oqp](inputs/formaldehyde-soc.oqp)

```bash
openqp formaldehyde-soc.oqp
```

`mrsf(nstate=3)` with `soc` computes three singlets (S0, S1, S2) and three
triplets (T0, T1, T2), then the SOC between every singlet–triplet and
triplet–triplet pair. The run takes about 4 seconds.

## What you get

The `SOC_MRSF` section first lists every matrix element in cm⁻¹, split into
one-electron (`1e`) and two-electron (`2e`) parts. The column `Absolute` is
|1e + 2e| for that spin component. The largest elements are:

```text
  State_i    State_j         Re(1e)      Im(1e)      Re(2e)      Im(2e)      Absolute
     S0    / T0(Ms= 0)       0.0000    -90.0740      0.0000     35.2698   54.804170567800
     S1    / T0(Ms= 0)       0.0000      0.0000      0.0000     -0.0000    0.000000000003
     S1    / T1(Ms= 0)       0.0000    -82.0876      0.0000     31.4124   50.675189621085
```

It then diagonalizes the full singlet–triplet Hamiltonian and lists the
spin-orbit states with their composition:

```text
  State    cm-1        eV        Composition

     1       -0.15   -0.000019        S0 (100.0%)
     2    30971.21    3.839941    T0(+1) ( 50.0%)     T0(-1) ( 50.0%)
     3    30971.21    3.839942    T0(-1) ( 50.0%)     T0(+1) ( 50.0%)
     4    30971.45    3.839971    T0( 0) (100.0%)
     5    32960.08    4.086530        S1 (100.0%)
     6    47753.41    5.920669    T1(-1) ( 50.0%)     T1(+1) ( 50.0%)
     7    47753.43    5.920672    T1(+1) ( 50.0%)     T1(-1) ( 50.0%)
     8    47753.45    5.920674    T1( 0) (100.0%)
```

| State | Character | Energy above S0 |
| --- | --- | --- |
| T0 | ³nπ\* | 3.840 eV |
| S1 | ¹nπ\* | 4.087 eV |
| T1 | ³ππ\* | 5.921 eV |

| Coupling | Reference value |
| --- | --- |
| ⟨S0 \| H_SO \| T0, Ms = 0⟩ | 54.80 cm⁻¹ |
| ⟨S1 \| H_SO \| T0⟩ | 0 (all components) |
| ⟨S1 \| H_SO \| T1, Ms = 0⟩ | 50.68 cm⁻¹ |

## Reading the result

- **El-Sayed's rule.** S1 and T0 are both nπ\* states with the same orbital
  occupation, and their coupling is zero. S1 couples strongly to T1 (ππ\*),
  where the orbital type changes. Intersystem crossing from S1 therefore needs
  the ππ\* triplet or vibrational distortion of the molecule.
- **S0–T0 coupling** (54.8 cm⁻¹) controls phosphorescence from the ³nπ\* state
  back to the ground state.
- **The two-electron term matters.** It has the opposite sign to the
  one-electron term and reduces the coupling by about 40%; a one-electron-only
  calculation would overestimate SOC.
- The spin-orbit splitting of each triplet is below 1 cm⁻¹ in this light
  molecule, so the spin-orbit states keep almost pure singlet or triplet
  character.

## Try next

- Request different numbers of singlets and triplets with
  `soc(ns=3,nt=5)` and a route without `nstate`:
  `mrsf/bhhlyp/6-31g* soc(ns=3,nt=5)`.
- Pyramidalize the molecule by moving both hydrogens a little along x, and
  compare the S1–T0 coupling with the planar value of zero.

See also: [Spin-Orbit Coupling](../workflows/soc.md),
[MRSF-TDDFT](../workflows/mrsf-tddft.md).
