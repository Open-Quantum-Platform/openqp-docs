# Gold Hydride: Relativistic Bond Contraction

For heavy elements, the inner electrons move fast enough that relativity
changes chemistry. In gold the 6s orbital contracts and drops in energy, and
bonds to gold become markedly shorter. AuH is the classic example. This page
computes its bond length in three ways: non-relativistic with all electrons,
scalar-relativistic Douglas–Kroll–Hess (DKH2) with all electrons, and with an
effective core potential (ECP) that includes relativity implicitly.

<div class="oqp-figs" markdown>
<figure markdown>
![AuH](../assets/worked-examples/mol-auh.png)
<figcaption>AuH at the DKH2 bond length, 1.528 Å</figcaption>
</figure>
</div>

![Potential-energy curves of AuH](../assets/worked-examples/plot-auh-curves.svg)

## Copy and run

The two all-electron calculations need a basis set with uncontracted (free)
primitive functions, provided as a file:
[x2c-svpall_uncontracted_auh.json](inputs/x2c-svpall_uncontracted_auh.json).
Put it in the same folder as the inputs. It is the x2c-SVPall basis of Au and H
with all contractions removed, made with the Basis Set Exchange tool that is
installed with OpenQP:

```bash
bse get-basis x2c-SVPall json --elements 1,79 --unc-gen --unc-seg --unc-spdf > x2c-svpall_uncontracted_auh.json
```

DKH2, all electrons:

```text title="auh-dkh2.oqp"
dft/pbe0/file:x2c-svpall_uncontracted_auh.json scf(scal_rel=2)
geom="""
Au 0.000000 0.000000 0.000000
H  0.000000 0.000000 1.550000
"""
```

Non-relativistic, all electrons: the same input without `scf(scal_rel=2)`
([auh-nonrel.oqp](inputs/auh-nonrel.oqp)).

With the def2-SVP basis set, which brings a 60-electron relativistic ECP for
gold:

```text title="auh-ecp.oqp"
dft/pbe0/def2-svp
geom="""
Au 0.000000 0.000000 0.000000
H  0.000000 0.000000 1.550000
"""
```

[Download auh-dkh2.oqp](inputs/auh-dkh2.oqp) ·
[auh-nonrel.oqp](inputs/auh-nonrel.oqp) ·
[auh-ecp.oqp](inputs/auh-ecp.oqp)

```bash
openqp auh-dkh2.oqp
```

- `file:x2c-svpall_uncontracted_auh.json` reads the basis set from the JSON
  file instead of the built-in library.
- `scf(scal_rel=2)` adds the second-order Douglas–Kroll–Hess scalar
  relativistic correction to the one-electron Hamiltonian. The log confirms it:

    ```text
     scal_rel = 2: applying DK1 + DK2 correction.
     scal_rel_decontract = 1: decoupling in the decontracted (primitive) basis,
    ```

- `def2-svp` for gold replaces the 60 inner electrons by an ECP fitted to
  relativistic atomic calculations; the log reports
  `DFT: number of electrons = 20` instead of 80.

With 4 threads one point takes about 35 s (non-relativistic), 50 s (DKH2), and
3 s (ECP). The curves above were computed from 1.40 to 1.90 Å in steps of
0.05 Å, and the bond lengths come from a polynomial fit to the five points
around each minimum.

## What you get

At r(Au–H) = 1.55 Å:

| Treatment | Electrons | Total energy (hartree) |
| --- | --- | --- |
| Non-relativistic, all-electron | 80 | −17869.5620826 |
| DKH2, all-electron | 80 | −18998.7020527 |
| def2-SVP with ECP | 20 | −136.3048615 |

The total energies are not comparable between treatments: relativity lowers
the energy of the core electrons by more than 1100 hartree, and the ECP run
does not include the core at all. Compare bond lengths and other properties
instead.

| Treatment | r(Au–H) | HOMO (σ Au–H) at 1.55 Å |
| --- | --- | --- |
| Non-relativistic, all-electron | 1.735 Å | −0.2399 hartree |
| DKH2, all-electron | 1.528 Å | −0.2755 hartree |
| def2-SVP with ECP | 1.540 Å | — |
| Experiment | 1.524 Å | — |

For the ECP model, an analytic Hessian at 1.540 Å
([auh-ecp-freq.oqp](inputs/auh-ecp-freq.oqp)) gives a harmonic frequency of
2420 cm⁻¹ (experiment: 2305 cm⁻¹).

## Reading the result

- **Relativity shortens the bond by 0.21 Å.** Without it, PBE0 predicts
  1.735 Å, far from experiment; with DKH2 the bond length is within 0.004 Å of
  the experimental value.
- **The 6s orbital is stabilized.** The HOMO, the Au–H σ bond built mostly from
  Au 6s, lies 0.97 eV lower with DKH2.
- **The relativistic ECP captures most of the effect** at a small fraction of
  the cost (3 s instead of 50 s per point), which is why ECPs are the usual
  choice for heavy elements in molecular calculations.
- **Use uncontracted basis functions for all-electron work with heavy
  elements.** Contracted relativistic basis sets such as x2c-SVPall are built
  for relativistic core orbitals. With the contracted x2c-SVPall basis, the
  non-relativistic energy at 1.52 Å came out 2331 hartree too high
  (−15538.7085 instead of −17869.5587 hartree in the uncontracted basis).

## Try next

- Repeat the curve with `scf(scal_rel=1)` (DKH1) and compare the bond length.
- Replace AuH with AgH or CuH: the relativistic contraction becomes smaller
  for the lighter coinage metals.

See also: [`scal_rel`](../keywords/scf.md#scal_rel),
[`scal_rel_decontract`](../keywords/scf.md#scal_rel_decontract),
[ECP example](hi-ecp.md).
