# `[pcm]`

The `[pcm]` section controls implicit-solvent settings. The current production
path is an energy-only reference-SCF PCM/ddX workflow for RHF/ROHF references.

## Minimal Example

```ini
[pcm]
enabled=true
backend=ddx
mode=reference_scf
model=ddpcm
epsilon=78.3553
```

## Keywords

### `enabled`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | PCM runtime activation |

Enables the PCM reaction-field contribution. When true, the input checker
requires the current production scope: `backend=ddx`, `mode=reference_scf`,
`runtype=energy`, and RHF/ROHF.

### `backend`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `ddx` |
| Values | `ddx`, `pcmsolver` |
| Used by | PCM backend selection |

Selects the PCM backend. Only `ddx` has an implemented runtime energy path in
the current production scope.

### `mode`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `reference_scf` |
| Values | `reference_scf`, `reference_scf_plus_post_state`, `post_state_correction` |
| Used by | PCM coupling mode |

Selects the coupling mode. Only `reference_scf` is currently implemented.

### `model`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `ddpcm` |
| Values | `ddcosmo`, `ddpcm`, `ddlpb`, `iefpcm`, `cpcm` |
| Used by | continuum model |

Selects the continuum model. With `backend=ddx`, use `ddcosmo`, `ddpcm`, or
`ddlpb`.

### `solvent`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `water` |
| Used by | solvent label |

Solvent label for readability and future solvent-model support.

### `epsilon`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `78.3553` |
| Used by | dielectric constant |

Static dielectric constant. Must be numeric and greater than `1`.

### `radii`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `uff` |
| Used by | cavity radii model |

Selects the cavity radii model.
