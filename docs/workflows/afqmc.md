# Auxiliary-Field Quantum Monte Carlo

The optional OpenQP–AFQMC integration provides a standardized molecular input
and a single installation for SCF, integral preparation, trial validation, and
native OpenMP AFQMC propagation.

```text
OpenQP input -> SCF orbitals and native integrals -> Cholesky Hamiltonian
             -> trial wavefunction -> phaseless AFQMC propagation
```

AFQMC is maintained in a private repository. Users must have GitHub access to
that repository before installing the combined package.

## Install from Source

Place the repositories beside each other:

```bash
mkdir oqp-workspace
cd oqp-workspace
git clone https://github.com/Open-Quantum-Platform/openqp.git
git clone git@github.com:Open-Quantum-Platform/AFQMC.git afqmc
cd openqp
python -m pip install .
```

Alternatively, clone AFQMC as `openqp/external/afqmc`. OpenQP detects both
layouts. For another location, specify it explicitly:

```bash
python -m pip install . \
  -C cmake.define.ENABLE_AFQMC=ON \
  -C cmake.define.OPENQP_AFQMC_SOURCE_DIR=/absolute/path/to/afqmc
```

The wheel contains the OpenQP Python package and native library, the adapter,
and `oqp/bin/openqp-afqmc-native`. The `openqp-afqmc` console command finds and
launches that packaged executable.

## Run

For the small CH2 ROHF/STO-3G example distributed with OpenQP:

```bash
openqp-afqmc examples/AFQMC/CH2_ROHF_STO3G_AFQMC.oqp
```

Select another output directory with `--output`, or prepare the Hamiltonian and
trial files without starting propagation:

```bash
openqp-afqmc calculation.oqp --output calculation_afqmc --prepare-only
```

Without `--prepare-only`, the command performs these steps:

1. Run the requested OpenQP HF/DFT reference calculation.
2. Transform the one- and two-electron integrals to the molecular-orbital basis.
3. Factorize the electron-repulsion supermatrix into Cholesky vectors.
4. Write and validate the selected mean-field, SF-CIS, or MRSF-CIS trial.
5. Launch native AFQMC using the controls in [`[afqmc]`](../keywords/afqmc.md).

The output directory contains `HAMILTONIAN`, `FCIDUMP`, `TRIAL` or the selected
multideterminant trial, `OOORBDAT`, `AFQMC.json`, and the OpenQP log.
`AFQMC.KEYWORDS` is also written when the target has nonnegative `MS2`; the
legacy `MULT` convention cannot encode negative target `MS2`, but this does not
prevent native preparation or propagation.

## Multideterminant Trials

Set `trial=mrsf` or `trial=sf` together with `trial_file`. The file is a
normalized CI determinant expansion; TDDFT linear-response `X/Y` vectors are
not interpreted as CI coefficients. Electron counts, orbital indices,
coefficients, and determinant normalization are checked before propagation.

For excited-state work, inspect the trial's spin contamination and lower-state
overlap diagnostics, and converge the time step, walker population, projection
length, Cholesky cutoff, and determinant space. A short example is only an
installation smoke test, not a production energy estimate.

## Current Scaling Limit

The first implementation materializes the native OpenQP AO electron-repulsion
tensor before transformation, giving fourth-power memory scaling in the AO
basis. Use small or moderate orbital spaces until a direct or density-fitted
export path is available.
