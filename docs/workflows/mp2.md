# MP2

OpenQP supports standalone second-order Moller-Plesset ground-state correlation
with `[input] method=mp2`. The calculation first converges an HF reference, then
adds the MP2 correlation energy and reports the correlated `E(HF+MP2)` total.

The available workflows depend on the HF reference:

- RHF supports `energy`, the analytic `grad` calculation, and the
  gradient-driven `optimize`, `ts`, `mep`, and `irc` calculations.
- UHF and ROHF support `energy` only. Their gradient requests stop explicitly;
  OpenQP does not apply the restricted formula to an open-shell reference.
- Leave `[input] functional` empty. MP2 on Kohn-Sham references is rejected.
- Use `[scf] type=rhf`, `uhf`, or `rohf` for the reference.
- Use `[mp2]` when selecting spin scaling or an energy transformation.

## Energy

### `.oqp`

```text
mp2(reference=uhf)/6-31g scf(conv=1e-10)
geom="../geometries/H2O-0381125c86f2.xyz"
```

The `reference` route option accepts `rhf`, `rohf`, or `uhf` and lowers to
`[scf] type`. It is separate from the `[mp2]` spin-scaling section.

### Python

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

### Legacy `.inp`

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

Runnable input:
[`examples/MP2/h2o_ump2_6-31g.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/MP2/h2o_ump2_6-31g.oqp)
or its same-stem legacy `.inp` companion.

For the H2O / 6-31G example, the validated installed-package run reports:

| Quantity | Value (Ha) |
| --- | --- |
| `E(MP2, correlation)` | `-0.1278307451` |
| `E(MP2, total)` | `-76.1121207760` |

## Energy Transformation

The default `transform=auto` chooses direct Coulomb builds for small bases and
packed AO-to-MO transformations above 120 basis functions or when the pair-build
count exceeds its guard. To request the packed form on a small molecule:

```text
mp2(reference=uhf,transform=n5)/6-31g scf(conv=1e-10)
geom="../geometries/H2O-0381125c86f2.xyz"
```

```python
job.mp2(reference="uhf", basis="6-31g", transform="n5", conv=1e-10)
```

In legacy input, add `[mp2] transform=n5`. Explicit `n5` can fall back from full
to occupied-virtual storage, but stops if neither packed form succeeds. Explicit
`direct` retains `OQP_MP2_MAX_JBUILDS` and stops when its count is exceeded.
Automatic selection retains the guarded direct fallback after packed failure.
See [`transform`](../keywords/mp2.md#transform) for the complete selection and
memory behavior. The setting does not select the analytic-gradient assembly.

The small UHF H2O/6-31G input is
[`examples/MP2/h2o_ump2_n5_6-31g.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/codex/pr470-mp2-n5-20261011-e133/examples/MP2/h2o_ump2_n5_6-31g.inp).
Its geometry, reference, SCF settings and committed energy reference are shared
with the conventional example above; the new selector's installed-package
execution remains pending in [engine PR #489](https://github.com/Open-Quantum-Platform/openqp/pull/489).

## Analytic RHF Gradient

The RHF derivative is evaluated from a stationary MP2 Lagrangian. It includes
the relaxed one-particle density, the amplitude-linear two-particle density,
and the coupled-perturbed RHF orbital response. No finite-difference gradient
is substituted. The same equations use the selected same-spin and
opposite-spin coefficients, so conventional MP2, SCS-MP2, SOS-MP2, and custom
spin scaling all have analytic gradients.

### `.oqp`

```text
mp2/6-31g grad(S0) scf(conv=1e-10,incremental=false)
geom="../geometries/H2O-0381125c86f2.xyz"
```

Runnable input:
[`examples/MP2/h2o_rmp2_6-31g_grad.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/MP2/h2o_rmp2_6-31g_grad.oqp)
or its same-stem legacy `.inp` companion.

### Python

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_rmp2_grad", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.mp2(basis="6-31g", reference="rhf", variant="scs-mp2")
job.workflow.gradient(state=0)

mol = job.run()
print(mol.get_grad())
```

The same analytic gradient supplies the native geometry workflows. For a
minimum search, replace `job.workflow.gradient(state=0)` with
`job.workflow.optimize(istate=0)` or use `opt(S0)` in concise input.

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

The energy calculation uses direct Coulomb builds or packed AO-to-MO
transformations according to `transform`. A guard limits direct pair builds;
packed transformations check available memory and allocation status. If a job
stops at the direct-build guard, use `auto` or `n5`, reduce the basis/problem
size, or raise the guard only after checking runtime and memory requirements.

The first analytic-gradient implementation forms dense AO and MO four-index
quantities and therefore has fourth-power memory growth. It stops above 60
basis functions by default. `OQP_MP2_GRAD_MAX_NBF` can raise that limit after
the required memory has been checked. The gradient supports Cartesian and pure
spherical shells. MP2 Hessians, open-shell MP2 gradients, NACME, SOC, PCM, NMR,
IR, and Raman derivatives are not implemented.

See [References](../references.md#mp2-and-spin-scaled-mp2) for the MP2 and
spin-component-scaling papers behind the supported presets.
