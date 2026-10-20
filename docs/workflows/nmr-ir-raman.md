# NMR, IR, and Raman

## NMR Shielding

Request NMR shielding with the `nmr` modifier.

`.oqp`:

```text
hf/sto-3g nmr(gauge=cgo)
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_nmr", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.hf(basis="sto-3g")
job.workflow.nmr(gauge="cgo")

mol = job.run()
```

Legacy `.inp`:

```ini
[input]
runtype=energy
method=hf
basis=sto-3g

[scf]
type=rhf
multiplicity=1

[properties]
scf_prop=nmr
nmr_gauge=cgo
```

Runnable `.oqp`:
[`examples/NMR/H2O_RHF-NMR.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/NMR/H2O_RHF-NMR.oqp).
The same-stem `.inp` file is retained for legacy use.

`nmr_gauge` accepts:

| Value | Meaning |
| --- | --- |
| `cgo` | Common-gauge-origin shielding. |
| `giao` | Gauge-including atomic orbital shielding where supported. |

ACID maps come from the same call, but they need the GIAO response, so switch
the gauge as well as enabling them -- `nmr(gauge=giao,acid=true)` rather than
the `gauge=cgo` used above, which the input checker refuses with `acid`. See
[ACID Current-Density Maps](acid.md).

`job.workflow.nmr(...)` requires an HF/DFT reference-SCF theory. CGO NMR is
limited to closed-shell RHF; use `gauge="giao"` for open-shell UHF/ROHF
references. The helper also blocks range-separated and meta-GGA functionals for
NMR because those paths are not implemented.

## IR and Raman

IR and Raman intensities are produced from supported Hessian/frequency
workflows. See [Hessian and Frequencies](hessian.md) for the main Hessian
workflow page.

With the analytical ground-state Hessian (RHF/RKS, UHF/UKS, ROHF/ROKS), the
intensities are analytic and need no extra calculations:

- **IR.** Comes from the nuclear derivatives of the dipole moment, built from
  the relaxed density derivatives the Hessian already computes.
- **Raman.** Comes from the nuclear derivatives of the static polarizability.
  - It needs three extra CPHF right-hand sides plus a fixed number of
    derivative-integral passes, independent of the number of atoms.
  - For Kohn-Sham, the exchange-correlation terms are central differences
    along the relaxed orbital path; no SCF or CPHF is re-solved.
- **Effective core potentials.** These cases are included.
- **Numerical Hessian.** Intensities still come from finite differences:
  6N displaced SCF + CPHF calculations.
- **Log.** The log states which backend produced the intensities, and the
  `.hess.json` sidecar records it in `vibrational_intensity_metadata`.

`.oqp`:

```text
dft/bhhlyp/6-31g* hess(S0,type=analytical) ir raman
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_freq", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.dft(functional="bhhlyp", basis="6-31g*")
job.workflow.hessian(type="analytical", state=0)

mol = job.run()
```

Legacy `.inp`:

```ini
[input]
runtype=hess
method=hf
functional=bhhlyp
basis=6-31g*

[hess]
type=analytical
state=0
```

Runnable `.oqp` inputs:

- [`examples/HESS/H2O_RHF-DFT_ANA_HESS.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2O_RHF-DFT_ANA_HESS.oqp)
- [`examples/HESS/H2O_RHF-DFT_NUM_HESS.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2O_RHF-DFT_NUM_HESS.oqp)
- [`examples/HESS/H2Oplus_UHF_ANA_HESS_IR_RAMAN.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2Oplus_UHF_ANA_HESS_IR_RAMAN.oqp)
- [`examples/HESS/H2Oplus_ROHF_ANA_HESS_IR_RAMAN.oqp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2Oplus_ROHF_ANA_HESS_IR_RAMAN.oqp)

Each has a same-stem legacy `.inp` companion.
