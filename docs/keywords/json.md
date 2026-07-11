# `[json]`

The `[json]` section carries advanced restart metadata used by internal JSON
interfaces. Most users should configure the calculation through the normal
route and [`[guess]`](guess.md) section instead.

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `scf_type` | string | empty | SCF reference label stored with imported JSON data. |
| `basis` | string | empty | Basis label associated with the JSON payload. |
| `library` | string | empty | Basis-library mapping associated with the payload. |
| `do_init` | string | `no` | Whether the JSON interface requests its initialization path. |

These keys are compatibility metadata, not an alternative to the `.oqp`
method, basis, and reference syntax.
