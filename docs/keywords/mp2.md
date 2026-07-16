# `[mp2]`

The `[mp2]` section controls spin-component scaling for standalone
`[input] method=mp2` calculations. Ordinary MP2 does not require this section;
the defaults are conventional unscaled MP2.

MP2 is a post-SCF energy workflow. It requires an HF reference, so
`[input] functional` must be empty and `[input] runtype` must be `energy`.
In concise input, select that reference with
`mp2(reference=rhf|rohf|uhf)/BASIS`; the value lowers to `[scf] type` and is
not a keyword in this section.

## Minimal Examples

Conventional MP2:

```ini
[input]
method=mp2
runtype=energy
functional=

[mp2]
variant=mp2
```

Spin-component-scaled MP2:

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
| Used by | standalone MP2 energy |

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

## Notes

- `method=mp2` accepts `runtype=energy` only.
- `method=mp2` rejects non-empty `[input] functional` values.
- The reference is selected through `[scf] type`; RHF, UHF, and ROHF references
  are supported.
- SOS and OS-only variants set the same-spin scale to zero and skip same-spin
  work.

See the [MP2 workflow](../workflows/mp2.md) for complete input and Python
examples.
