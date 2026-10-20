# UMRSF-TDDFT: An Unrestricted Reference

MRSF-TDDFT builds its states from a restricted open-shell (ROHF/ROKS) triplet
reference. UMRSF-TDDFT uses an unrestricted (UHF/UKS) triplet reference
instead, in which α and β electrons have different spatial orbitals. The two
are compared here for formaldehyde at the same geometry and level.

<div class="oqp-figs" markdown>
<figure markdown>
![Formaldehyde](../assets/worked-examples/mol-hcho.png)
<figcaption>Formaldehyde at the PBE0/6-31G* geometry</figcaption>
</figure>
</div>

## Copy and run

```text title="formaldehyde-umrsf.oqp"
umrsf(nstate=3)/bhhlyp/6-31g*
geom="""
C      0.000000     0.000000    -0.526342
O      0.000000     0.000000     0.676110
H      0.000000     0.937620    -1.119884
H      0.000000    -0.937620    -1.119884
"""
```

[Download formaldehyde-umrsf.oqp](inputs/formaldehyde-umrsf.oqp)

```bash
openqp formaldehyde-umrsf.oqp
```

The only difference from the MRSF input of the
[SOC example](formaldehyde-soc.md) is the route name `umrsf`. OpenQP selects the
UHF triplet reference automatically, as the log reports:

```text
   PyOQP Reference:                   triplet UHF (internal working reference)
```

The run takes about 3 seconds.

## What you get

```text
 State      Energy       Excitation   Excitation(eV)  <S^2>  ...  Oscillator
    S0   -114.4196483022    -2.903524     0.000000      0.002  ...      0.0000
   REF   -114.3129457579     0.000000     2.903524        (triplet ROHF/UHF internal working reference)
    S1   -114.2666186519     1.260625     4.164149      0.008  ...      0.0000
    S2   -114.1003391297     5.785321     8.688845      0.023  ...      0.0049
```

| Quantity | MRSF-TDDFT (ROHF reference) | UMRSF-TDDFT (UHF reference) |
| --- | --- | --- |
| Triplet reference energy | −114.3083030 hartree | −114.3129458 hartree |
| S0 | −114.4212164 hartree | −114.4196483 hartree |
| S0 → S1 (n→π\*) | 4.087 eV | 4.164 eV |
| ⟨S²⟩ of S1 | — | 0.008 |

The MRSF values are from the [Python analysis example](python-state-analysis.md)
at the same geometry.

## Reading the result

- **The UHF reference is lower** (by 4.6 millihartree) because its α and β
  orbitals can relax independently; an ROHF reference forces them to share
  spatial orbitals.
- **The excited states stay close.** S0→S1 differs by 0.08 eV between the two
  references, and the UMRSF states remain essentially spin-pure (⟨S²⟩ ≤ 0.023).
- UMRSF-TDDFT has analytic gradients and the same geometry drivers as MRSF
  (`grad`, `opt`, `meci`, `mecp`), so either reference can be used for the
  workflows on the other pages. Report which one was used, because energies at
  the 0.1 eV level depend on the choice.

## Try next

- Optimize S1 with `umrsf(nstate=3)/bhhlyp/6-31g* opt(S1)` and compare with the
  [MRSF S1 optimization](formaldehyde-s1-opt.md).
- Repeat for a molecule whose triplet reference has strong spin polarization,
  such as a twisted or stretched double bond, and compare the two references
  carefully.

See also: [MRSF-TDDFT](../workflows/mrsf-tddft.md),
[`tdhf` keywords](../keywords/tdhf.md).
