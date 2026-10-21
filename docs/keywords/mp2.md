# `[mp2]`

The `[mp2]` section controls spin-component scaling and energy integral
transformation for standalone
`[input] method=mp2` calculations. Ordinary MP2 does not require this section;
the defaults are conventional unscaled MP2.

MP2 requires an HF reference, so `[input] functional` must be empty. RHF
references support analytic nuclear gradients and gradient-driven geometry
calculations; UHF and ROHF references remain energy-only. In concise input,
select the reference with
`mp2(reference=rhf|rohf|uhf)/BASIS`; the value lowers to `[scf] type` and is
not a keyword in this section.

## Minimal Examples

Conventional MP2 in `.oqp`:

```text
mp2/6-31g
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mp2")
job.molecule(geometry="water")
job.theory.mp2(basis="6-31g")
mol = job.run()
```

Analytic RHF-MP2 gradient in `.oqp`:

```text
mp2/6-31g grad(S0)
geom="h2o.xyz"
```

The spin-scaling preset is applied to both the energy and its analytic
gradient. For example, replace the first line with
`mp2(variant=scs-mp2)/6-31g` for SCS-MP2.

Legacy `.inp`:

```ini
[input]
method=mp2
runtype=energy
functional=
```

For spin-component-scaled MP2, add an exact `.oqp` section call:

```text
mp2/6-31g mp2(variant=scs-mp2)
geom="h2o.xyz"
```

The legacy section is:

```ini
[mp2]
variant=scs-mp2
```

Custom scaling:

```ini
[mp2]
variant=custom
same_spin_scale=0.50
opposite_spin_scale=1.10
```

## Keywords

### `variant`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `mp2` |
| Values | `mp2`, `conventional`, `scs-mp2`, `scs`, `sos-mp2`, `sos`, `os-mp2`, `os`, `opposite-spin`, `ss-mp2`, `ss`, `same-spin`, `sss-mp2`, `sss`, `scs-mi-mp2`, `scs-mi`, `custom` |
| Used by | standalone MP2 energy and RHF analytic gradient |

Selects the MP2 spin-scaling preset. The scales multiply same-spin and
opposite-spin correlation components:

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
| `custom` | `same_spin_scale` | `opposite_spin_scale` |

Named presets set both scale factors internally. If you provide
`same_spin_scale` or `opposite_spin_scale` with a named preset, those explicit
numbers are not used; choose `variant=custom` instead.

### `transform`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Values | `auto`, `direct`, `n5` |
| Used by | standalone MP2 correlation energy |

Selects the AO-to-MO transformation used for the correlation energy:

- `auto` uses direct per-occupied-virtual-pair Coulomb builds when their count
  is within [`max_jbuilds`](#max_jbuilds) and the basis has at most 120 functions.
  Otherwise it tries the packed transformation. If that fails, direct builds
  remain available only when their count satisfies the guard.
- `direct` requests direct Coulomb builds and retains the same pair-count
  guard. It stops when the guard is exceeded.
- `n5` requires the packed transformation, including for small bases. A full
  transformation can fall back to occupied-virtual storage. If the packed
  transformation cannot fit or allocate, the calculation stops; it does not
  change to direct Coulomb builds.

The two packed forms use the same MP2 expression. UHF and ROHF opposite-spin
components use the occupied-virtual form with both spin-orbital coefficient
sets. Memory checks include scratch and the ranks on each node. This setting
controls the energy transformation only; the analytic-gradient assembly has
its own storage requirements.

Concise input and Python:

```text
mp2(reference=uhf,transform=n5)/6-31g
geom="h2o.xyz"
```

```python
job.theory.mp2(reference="uhf", basis="6-31g")
job.settings.mp2(transform="n5")
```

The exact section form `mp2(reference=uhf)/6-31g mp2(transform=n5)` is
equivalent. In legacy input, use `[mp2] transform=n5`. The log reports `MP2 path: direct-J`, `MP2 path: n5 full`,
or `MP2 path: n5 occupied-virtual` for each selected or attempted form. A full
attempt can fail before the occupied-virtual fallback succeeds; a path message
alone does not establish completion. The correlated total energy is reported
only after a successful transformation. These messages do not constitute a
performance comparison.

### `same_spin_scale`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | `variant=custom` |

Scale factor for the same-spin MP2 contribution, `E_aa + E_bb`, when
`variant=custom`. The input checker requires finite numeric values for custom
scales.

### `opposite_spin_scale`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | `variant=custom` |

Scale factor for the opposite-spin MP2 contribution, `E_ab`, when
`variant=custom`. The input checker requires finite numeric values for custom
scales.

### `max_jbuilds`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `4000` |
| Used by | standalone MP2 correlation energy |

Guard on the number of per-occupied-virtual-pair Coulomb builds of the direct
transformation (`nocc*nvir` summed over both spins). Under `transform=auto` a
larger count selects the packed transformation, and a failed packed attempt
falls back to direct builds only when the count is within the guard; under
`transform=direct` a larger count stops the calculation. `0` disables direct
builds. Raise it only after checking the runtime and memory of the direct path.

Requires an engine build containing
[OpenQP PR #547](https://github.com/Open-Quantum-Platform/openqp/pull/547);
earlier engines read the `OQP_MP2_MAX_JBUILDS` environment variable instead,
which current engines ignore with an input-check warning.

```text
mp2/cc-pvtz mp2(transform=direct,max_jbuilds=8000)
geom="h2o.xyz"
```

### `grad_max_nbf`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `60` |
| Used by | RHF MP2 analytic gradient |

Largest number of basis functions the dense analytic MP2 gradient accepts. The
gradient stores full AO and MO four-index quantities, so memory grows as the
fourth power of the basis size (about `8·nbf⁴` bytes per tensor). A larger
basis stops after the MP2 energy with a message naming this keyword; raise it
only after checking the required memory.

Requires an engine build containing
[OpenQP PR #547](https://github.com/Open-Quantum-Platform/openqp/pull/547);
earlier engines read the `OQP_MP2_GRAD_MAX_NBF` environment variable instead.

```text
mp2/6-31g* grad(S0) mp2(grad_max_nbf=120)
geom="benzene.xyz"
```

## Notes

- RHF MP2 accepts `runtype=energy`, `grad`, `optimize`, `ts`, `mep`, and `irc`.
- UHF and ROHF MP2 accept `runtype=energy` only; derivative requests stop
  before the electronic-structure calculation.
- `method=mp2` rejects non-empty `[input] functional` values.
- The reference is selected through `[scf] type`; RHF, UHF, and ROHF references
  are supported for energies.
- SOS and OS-only variants set the same-spin scale to zero and skip same-spin
  work.

See the [MP2 workflow](../workflows/mp2.md) for complete input and Python
examples.
