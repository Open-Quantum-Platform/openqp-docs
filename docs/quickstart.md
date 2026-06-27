# Quickstart

This quickstart runs a small MRSF-TDDFT calculation on water. You can start from
either a standard OpenQP input file or the compact Python API.

## Input File

Create `h2o_mrsf.inp`:

```ini
[input]
system=
   8   0.000000000   0.000000000  -0.041061554
   1  -0.533194329   0.533194329  -0.614469223
   1   0.533194329  -0.533194329  -0.614469223
charge=0
runtype=energy
basis=6-31g*
functional=bhhlyp
method=tdhf

[guess]
type=huckel

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=3
```

Run it:

```bash
openqp h2o_mrsf.inp
```

## Python Script

The same calculation can be set up from Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=3)
job.theory("mrsf-tddft", functional="bhhlyp", basis="6-31g*", nstate=3)

mol = job.run()
results = mol.get_results()

print("Ground/reference energy:", results["energy"])
print("TD energies:", results["td_energies"])
```

OpenQP writes a log and structured output files in the working directory. For
more Python examples, see [Run OpenQP from Python](python-scripting.md).

## Next Calculations

Use these input files as nearby templates:

| Goal | Example input |
| --- | --- |
| MRSF-TDDFT energy | [`examples/MRSF-TDDFT/H2O_BHHLYP-MRSFTDDFT_ENERGY.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/MRSF-TDDFT/H2O_BHHLYP-MRSFTDDFT_ENERGY.inp) |
| RHF energy | [`examples/HF/H2O_RHF-HF_ENERGY.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HF/H2O_RHF-HF_ENERGY.inp) |
| DFT gradient | [`examples/DFT/H2O_RHF-DFT_GRADIENT.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/DFT/H2O_RHF-DFT_GRADIENT.inp) |
| Analytic HF/DFT Hessian | [`examples/HESS/H2O_RHF-DFT_ANA_HESS.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/HESS/H2O_RHF-DFT_ANA_HESS.inp) |
| Native geometry optimization | [`examples/OPT/H2O_RHF-DFT_OPTIMIZE_OQP.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/OPT/H2O_RHF-DFT_OPTIMIZE_OQP.inp) |
| SOC | [`examples/SOC/H2O_BHHLYP_SOC.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/SOC/H2O_BHHLYP_SOC.inp) |
| PCM/ddX energy | [`examples/PCM/H2O_RHF-HF_DDPCM_ENERGY_ISPHER.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/PCM/H2O_RHF-HF_DDPCM_ENERGY_ISPHER.inp) |
| NMR shielding | [`examples/NMR/H2O_RHF-NMR.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/NMR/H2O_RHF-NMR.inp) |
