# MRSF-EKT

MRSF-EKT computes ionization-potential and electron-affinity channels from an
MRSF-TDDFT reference.

Input style:

```ini
[input]
runtype=ekt
method=tdhf
functional=bhhlyp
basis=6-31g

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=10

[ekt]
ip=True
ea=False
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_mrsf_ekt", silent=1)
job.molecule(geometry="water", basis="6-31g", charge=0)
job.input(functional="bhhlyp")
job.mrsf(nstate=10, runtype="ekt")
job.ekt(ip=True, ea=False)

mol = job.run()
```

Runnable inputs:

- [`examples/other/h2o_rohf_mrsf_ekt_ip_6-31g_bhhlyp.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/other/h2o_rohf_mrsf_ekt_ip_6-31g_bhhlyp.inp)
- [`examples/other/h2o_rohf_mrsf_ekt_ea_6-31g_bhhlyp.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/other/h2o_rohf_mrsf_ekt_ea_6-31g_bhhlyp.inp)

At least one of `[ekt] ip` or `[ekt] ea` must be true. Set both to true to run
both channels in one job.
