# PCM/ddX

The current PCM production path is an energy-only reference-SCF workflow using
the ddX backend.
PCM treats the solvent as a polarizable dielectric continuum around a molecular
cavity. OpenQP currently exposes the ddX-backed reference-SCF energy path, which
is the first production solvent route and should be kept separate from future
state-specific excited-state PCM work. See the
[References](../references.md#pcm-and-ddx) page for continuum-solvation and
domain-decomposition ddPCM background.

Input style:

```ini
[input]
runtype=energy
method=hf
basis=6-31g*

[scf]
type=rhf
multiplicity=1

[pcm]
enabled=true
backend=ddx
mode=reference_scf
model=ddpcm
epsilon=78.3553
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_pcm", silent=1, usempi=False)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory("hf", basis="6-31g*")
job.workflow.pcm(
    enabled=True,
    backend="ddx",
    mode="reference_scf",
    model="ddpcm",
    epsilon=78.3553,
)

mol = job.run()
```

Runnable input:
[`examples/PCM/H2O_RHF-HF_DDPCM_ENERGY_ISPHER.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/PCM/H2O_RHF-HF_DDPCM_ENERGY_ISPHER.inp).

## Scope

- Supported production mode: `backend=ddx`, `mode=reference_scf`,
  `runtype=energy`.
- Reference support: RHF and ROHF.
- Python `job.workflow.pcm(...)` requires an HF/DFT reference-SCF theory. It
  blocks MRSF-TDDFT, non-ddX backends, non-`reference_scf` modes, and UHF
  references before runtime.
- `ispher` is selected automatically from the basis-shell convention; users do
  not normally need to set it for PCM/ddX inputs.
- MRSF-TDDFT can use the high-spin ROHF reference density as a reference-SCF
  PCM baseline.
- PCM gradients, PCM optimizations, Hessians, NACs, and state-specific
  excited-state PCM are outside this first energy path.
