# Water: MP2 and CCSD(T) Energies

Hartree–Fock treats each electron in the average field of the others. The
difference from the exact energy is the correlation energy. MP2 recovers most of
it at low cost, and CCSD(T), the usual reference method for small molecules,
recovers more. This example computes both for water in the cc-pVDZ basis set.

<div class="oqp-figs" markdown>
<figure markdown>
![Water](../assets/worked-examples/mol-water.png)
<figcaption>Water at the PBE0/6-31G* geometry</figcaption>
</figure>
</div>

## Copy and run

```text title="water-mp2.oqp"
mp2/cc-pvdz
geom="""
O      0.000000     0.000000     0.122745
H      0.000000     0.759541    -0.471922
H      0.000000    -0.759541    -0.471922
"""
```

```text title="water-ccsdt.oqp"
ccsd_t/cc-pvdz
geom="""
O      0.000000     0.000000     0.122745
H      0.000000     0.759541    -0.471922
H      0.000000    -0.759541    -0.471922
"""
```

[Download water-mp2.oqp](inputs/water-mp2.oqp) ·
[Download water-ccsdt.oqp](inputs/water-ccsdt.oqp)

```bash
openqp water-mp2.oqp
openqp water-ccsdt.oqp
```

Both start from an RHF reference. All electrons are correlated, including the
oxygen 1s pair; add `cc(nfzc=1)` to the CCSD(T) route to freeze it. cc-pVDZ uses
spherical d functions, so water has 24 basis functions. Each run takes 2–3
seconds.

## What you get

The MP2 block of `water-mp2.log` separates same-spin and opposite-spin pairs:

```text
  E(reference, SCF)      =       -76.0263514813
  E(MP2, same-spin total)=        -0.0516187358
  E(MP2, opp-spin  ab)   =        -0.1529199712
  E(MP2, correlation)    =        -0.2045387069
  E(MP2, total)          =       -76.2308901882
```

The CCSD(T) run starts its iterations from the MP2 amplitudes and reports:

```text
  E(reference, SCF)      =       -76.0263514813
  E(CCSD, correlation)   =        -0.2138605036
  E(CCSD, total)         =       -76.2402119848
  E((T), correction)     =        -0.0030969638
  E(CCSD(T), correlation)=        -0.2169574674
  E(CCSD(T), total)      =       -76.2433089486
```

| Method | Total energy (hartree) | Correlation energy (hartree) |
| --- | --- | --- |
| RHF | −76.0263515 | — |
| MP2 | −76.2308902 | −0.2045387 |
| CCSD | −76.2402120 | −0.2138605 |
| CCSD(T) | −76.2433089 | −0.2169575 |

MP2 recovers 94% of the CCSD(T) correlation energy here, and the perturbative
triples (T) add 3.1 millihartree (1.9 kcal/mol) to CCSD. Differences of this size
matter for reaction energies, which is why CCSD(T) is used to benchmark cheaper
methods.

## Cross-check

PySCF 2.13 at the same geometry and basis set, with all electrons correlated,
gives RHF −76.02635148, MP2 −76.23089019, CCSD −76.24021200, and CCSD(T)
−76.24330897 hartree. OpenQP agrees to 10⁻⁸ hartree.

## Try next

- Freeze the oxygen core with `ccsd_t/cc-pvdz cc(nfzc=1)`: the CCSD(T)
  correlation energy becomes −0.2148543 hartree, 2.1 millihartree smaller in
  magnitude.
- Repeat with `cc-pvtz`: the CCSD(T) correlation energy grows to −0.2891606
  hartree, one third larger than with cc-pVDZ. Correlation energies converge
  slowly with the basis set, which is why correlated calculations need larger
  basis sets than HF or DFT.

See also: [MP2](../workflows/mp2.md),
[Coupled Cluster](../workflows/coupled-cluster.md).
