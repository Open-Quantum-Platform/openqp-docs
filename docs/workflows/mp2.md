# MP2

OpenQP supports standalone second-order Moller-Plesset ground-state correlation
with `[input] method=mp2`. The calculation first converges an HF reference, then
adds the MP2 correlation energy and reports the correlated `E(HF+MP2)` total.

MP2 is currently an energy-only post-SCF workflow:

- Use `runtype=energy`.
- Leave `[input] functional` empty. MP2 on Kohn-Sham references is rejected.
- Use `[scf] type=rhf`, `uhf`, or `rohf` for the reference.
- Use `[mp2]` only when selecting a spin-scaled variant or custom scale factors.

## Energy

### One-line `.oqp` Style

```text
mp2(reference=uhf)/6-31g geom="../geometries/H2O-0381125c86f2.xyz" charge=0 mult=1 energy scf(conv=1e-10)
```

The `reference` route option accepts `rhf`, `rohf`, or `uhf` and lowers to
`[scf] type`. It is separate from the `[mp2]` spin-scaling section.

### Input File Style

```ini
[input]
system=
 8   0.000000000   0.000000000  -0.041061554
 1  -0.533194329   0.533194329  -0.614469223
 1   0.533194329  -0.533194329  -0.614469223
charge=0
runtype=energy
method=mp2
functional=
basis=6-31g

[guess]
type=huckel

[scf]
type=uhf
multiplicity=1
conv=1.0e-10

[mp2]
variant=mp2
```

### Pythonic Style

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mp2", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.mp2(basis="6-31g", reference="uhf", variant="mp2", conv=1.0e-10)

mol = job.run()
print("MP2 total energy:", mol.get_results()["energy"])
```

For custom spin scaling in Python, pass the scale factors through the same
helper:

```python
job.theory.mp2(
    basis="6-31g",
    reference="uhf",
    variant="custom",
    same_spin_scale=0.50,
    opposite_spin_scale=1.10,
)
```

Runnable input:
[`examples/MP2/h2o_ump2_6-31g.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/MP2/h2o_ump2_6-31g.oqp)
or its same-stem legacy `.inp` companion.

For the H2O / 6-31G example, the validated installed-package run reports:

| Quantity | Value (Ha) |
| --- | --- |
| `E(MP2, correlation)` | `-0.1278307451` |
| `E(MP2, total)` | `-76.1121207760` |

## Spin-Scaled Variants

The native MP2 kernel computes same-spin and opposite-spin components
separately. Named presets choose scale factors for

```text
E(MP2) = c_ss * (E_aa + E_bb) + c_os * E_ab
```

| Variant | Same-spin scale `c_ss` | Opposite-spin scale `c_os` |
| --- | --- | --- |
| `mp2`, `conventional` | `1.0` | `1.0` |
| `scs-mp2`, `scs` | `1.0 / 3.0` | `1.2` |
| `sos-mp2`, `sos` | `0.0` | `1.3` |
| `os-mp2`, `os`, `opposite-spin` | `0.0` | `1.0` |
| `ss-mp2`, `ss`, `same-spin`, `sss-mp2`, `sss` | `1.0` | `0.0` |
| `scs-mi-mp2`, `scs-mi` | `1.29` | `0.40` |

For any other literature parameterization, use `variant=custom`:

```ini
[mp2]
variant=custom
same_spin_scale=0.50
opposite_spin_scale=1.10
```

Named presets overwrite `same_spin_scale` and `opposite_spin_scale`. Set
`variant=custom` when the numeric scales should be read directly.

## Implementation Notes

OpenQP assembles the MP2 energy in spin-blocked form on semicanonicalized
orbitals. ROHF references are semicanonicalized before the correlation step so
the denominator expression is well defined.

The current implementation uses direct per-occupied-MO-pair Coulomb builds
through the existing two-electron driver. It does not store a full fourth-order
MO integral tensor. A guard limits the number of pair builds; if a job aborts
with `OQP_MP2_MAX_JBUILDS`, reduce the basis/problem size or raise that guard
only after checking the expected runtime and memory cost.

Derivative workflows are not implemented for MP2 yet. Use HF/DFT or response
methods for gradients, Hessians, optimization, NACME, SOC, PCM, NMR, IR, and
Raman workflows until MP2-specific derivatives are added.

See [References](../references.md#mp2-and-spin-scaled-mp2) for the MP2 and
spin-component-scaling papers behind the supported presets.
