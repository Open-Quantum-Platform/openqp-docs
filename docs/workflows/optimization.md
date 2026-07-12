# Geometry Optimization and Reaction Paths

Concise `.oqp` geometry drivers use the native OpenQP optimizer automatically.
Users select a physical state and the calculation they want; there is no
backend or `lib` keyword in this format.

```text
dft/pbe0/def2-svp geom="h2o.xyz" opt(S0,maxit=50)
mrsf(nstate=5)/bhhlyp/6-31g* geom="guess.xyz" meci(S0,S1,maxit=100)
```

The native engine supports minima, transition states, MECI, MECP, TCI, MEP,
IRC, and NEB. It uses redundant internal, DLC, TRIC, or Cartesian coordinates
as appropriate, with restricted-step RFO/P-RFO optimization.

## Native Minimum Search

The shortest canonical input is:

```text
dft/bhhlyp/6-31g* geom="h2o.xyz" opt
```

`opt` defaults to `S0`. Add native controls directly when needed:

```text
dft/bhhlyp/6-31g* geom="h2o.xyz" opt(S0,maxit=50,coordsys=tric,trust=0.2,trust_max=0.5)
```

The equivalent traditional sectioned `.inp` spelling remains supported:

```ini
[input]
runtype=optimize
method=hf
functional=bhhlyp
basis=6-31g*

[scf]
type=rhf
multiplicity=1

[optimize]
lib=oqp
istate=0
maxit=50

[oqp]
coordsys=tric
trust=0.2
trust_max=0.5
```

Python also uses the native backend by default. Its explicit backend selector
is retained for compatibility with existing scripts:

```python
from oqp.openqp import OpenQP

job = OpenQP("h2o_opt", silent=1)
job.molecule(geometry="water", charge=0, multiplicity=1)
job.theory.dft(functional="bhhlyp", basis="6-31g*")
job.workflow.optimize(istate=0, maxit=50, coordsys="tric", trust=0.2)
mol = job.run()
```

Runnable traditional input:
[`examples/OPT/H2O_RHF-DFT_OPTIMIZE_OQP.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/OPT/H2O_RHF-DFT_OPTIMIZE_OQP.inp).

## Native Transition State and IRC

Native TS optimization uses P-RFO. `follow` selects the initial mode index, and
`hessian` selects how the starting Hessian is obtained:

```text
dft/pbe0/def2-svp geom="ts_guess.xyz" ts(S0,follow=0,hessian=numerical,maxit=50)
```

`hessian=model` is the inexpensive default. `numerical` or `analytical`
calculates a real Cartesian Hessian for the selected state before the first TS
step. Availability of an analytical Hessian still depends on the electronic
method and basis. For an isolated molecule in full-rank TRIC or Cartesian
coordinates, OpenQP removes whole-molecule translation/rotation zero-mode noise
from a real Hessian and restores positive model curvature in those rigid
directions before P-RFO mode selection; internal-only RIC/DLC modes are left
unchanged. The standalone engine leaves this projection off by default so an
external field can retain genuine lab-frame curvature. Active QM/MM OpenQP
geometry and reaction-path jobs are currently rejected in preflight because
their force backend is not connected to these optimizers; supported QM/MM
workflows remain energy, MD, and NAMD.

After locating a transition state, trace either native IRC branch explicitly:

```text
dft/pbe0/def2-svp geom="ts.xyz" irc(S0,direction=forward,step=0.1,hessian=analytical,gtol=1e-4,maxit=30)
dft/pbe0/def2-svp geom="ts.xyz" irc(S0,direction=backward,step=0.1,hessian=analytical,gtol=1e-4,maxit=30)
```

Native IRC projects mass-weighted translation and rotation modes, then requires
exactly one significant negative vibrational mode. It rejects a minimum (none)
or a higher-order saddle (more than one) before tracing the path.

Native MEP uses the same gradient stopping threshold without requiring a
transition-state Hessian:

```text
mrsf(nstate=5)/bhhlyp/6-31g* geom="start.xyz" mep(S0,points=30,step=0.1,gtol=1e-4)
```

## Native NEB

The reactant comes from `geom`; `product` supplies the second endpoint. Native
NEB can align the endpoints, relax them, run climbing-image NEB, test both
maximum and RMS force thresholds, and write the final band:

```text
dft/pbe0/def2-svp geom="reactant.xyz" neb(S0,product="product.xyz",images=7,spring=0.05,climb=true,fmax=0.002,frms=0.001,dt=0.5,maxmove=0.2,align=true,opt_ends=true,end_fmax=0.001,output="reaction_path.xyz")
```

`climb`, `align`, and `opt_ends` are booleans. If `output` is omitted, OpenQP
writes `<project>_neb.xyz` in the log directory. The multi-frame XYZ file
contains every final image and records each image energy in Hartree.
When `climb=true`, set `climb_fmax >= fmax` so the climbing image activates
before the final convergence threshold can be satisfied.

## Crossing Points

Physical state labels replace internal state indices in `.oqp`:

```text
mrsf(nstate=5)/bhhlyp/6-31g* geom="guess.xyz" meci(S0,S1,maxit=100)
mrsf(nstate=5)/bhhlyp/6-31g* geom="guess.xyz" mecp(S0,T0,maxit=100)
mrsf(nstate=5)/bhhlyp/6-31g* geom="guess.xyz" tci(S0,S1,S2,maxit=100)
```

Traditional `.inp` and Python scripts may continue to use the internal
`istate`, `jstate`, `kstate`, `imult`, and `jmult` fields documented under
[`[optimize]`](../keywords/optimize.md).

## Optional Legacy geomeTRIC Escape Hatch

geomeTRIC is not part of the concise `.oqp` geometry grammar. It remains
available to traditional sectioned `.inp` files and the Python API, primarily
for constrained optimization that has not yet moved to the native engine.
Install the optional dependency first:

```bash
pip install "openqp[geometric]"
```

Then use the established sectioned input:

```ini
[input]
runtype=optimize
method=hf
functional=pbe0
basis=def2-svp
system=reactant.xyz

[scf]
type=rhf
multiplicity=1

[optimize]
lib=geometric
istate=0

[geometric]
coordsys=tric
trust=0.1
constraints_file=my.constraints
```

The compatible Python spelling is also retained:

```python
job.workflow.optimize(
    lib="geometric",
    istate=0,
    coordsys="tric",
    trust=0.1,
    constraints_file="my.constraints",
)
```

Legacy examples, including constrained optimization, remain under
[`examples/OPT`](https://github.com/Open-Quantum-Platform/openqp/tree/main/examples/OPT).
