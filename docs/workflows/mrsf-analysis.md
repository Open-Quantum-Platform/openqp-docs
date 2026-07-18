# MRSF Analysis and Interoperability

The MRSF analysis toolkit turns a finished MRSF-TDDFT energy calculation into
Python objects for excited-state analysis, visualization, and data exchange.
Use it when you need natural transition orbitals, attachment/detachment
densities, state-to-state transition densities, cube files, QCSchema payloads,
FCIDUMP files, or comparison against external excited-state results.

The public import surface is `oqp.interop`. The lower-level implementation lives
in `oqp.analysis`, `oqp.export`, and `oqp.quantum`, but user scripts should
normally import from `oqp.interop`.

## `.oqp` Calculation

Run the underlying MRSF energy calculation first:

```text
mrsf(nstate=4)/bhhlyp/6-31g*
energy
geom="formaldehyde.xyz"
```

The analysis itself is performed through the Python API below.

## Python Style

Run the calculation with the high-level `OpenQP` wrapper, then wrap the returned
`Molecule` with `MRSFExcitedStates`.

```python
from oqp.openqp import OpenQP
from oqp.interop import (
    MRSFExcitedStates,
    nto_excitation,
    attachment_detachment,
    participation_ratio,
)

job = OpenQP("formaldehyde_mrsf", silent=1)
job.molecule(
    """
C   0.000000   0.000000  -0.529700
O   0.000000   0.000000   0.677500
H   0.000000   0.934200  -1.124000
H   0.000000  -0.934200  -1.124000
""",
    charge=0,
)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=4)

mol = job.run()
states = MRSFExcitedStates(mol)

target = 1
print("S0 -> S1 dipole:", states.transition_dipole(0, target))
print("S0 -> S1 oscillator strength:", states.oscillator_strength(0, target))

nto = nto_excitation(states, target)
ad = attachment_detachment(states, target)
print("Significant NTO pairs:", nto["n_significant"])
print("NTO participation ratio:", participation_ratio(nto["weights"]))
print("Promoted charge:", ad["n_promoted"])
```

Analysis state indices are zero-based. `0` is the lowest MRSF response root
used as `S0`; `1` is the first `S0 -> S1` target in the examples above.

## Legacy `.inp` Style

The analysis layer works on the same MRSF energy calculation that is available
from an input file.

```ini
[input]
runtype=energy
method=tdhf
functional=bhhlyp
basis=6-31g*

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=4
```

If a script already has an input file, use `Runner` and then pass `runner.mol`
to the same `oqp.interop` functions:

```python
from oqp.pyoqp import Runner
from oqp.interop import MRSFExcitedStates, nto_excitation

runner = Runner(
    project="formaldehyde_mrsf",
    input_file="formaldehyde_mrsf.inp",
    log="formaldehyde_mrsf.log",
    silent=1,
    usempi=False,
)
runner.run()

states = MRSFExcitedStates(runner.mol)
nto = nto_excitation(states, 1)
```

## Transition And State Densities

`MRSFExcitedStates` reads the MRSF state-interaction density tags produced by
the energy driver. It exposes transition densities, unrelaxed state densities,
transition dipoles, oscillator strengths, and spin-flip amplitude matrices.

```python
tdm_mo = states.tdm_mo(0, 1)
tdm_ao = states.tdm_ao(0, 1)
density_s1 = states.state_density_ao(1)
delta_s1 = states.diff_density_mo(1)
amplitudes = states.amplitude_matrix(1)
```

These densities are MRSF state-interaction objects. The MRSF `S0` is itself a
response root, so standard closed-shell TDDFT reference-to-excited-state
formulas should not be substituted for the `MRSFExcitedStates` API.

## Descriptors

The descriptor helpers summarize excited-state character.

```python
from oqp.interop import (
    AOBasis,
    make_box_grid,
    nto_excitation,
    participation_ratio,
    tozer_lambda,
    fragment_ct_matrix,
)

ao = AOBasis(mol)
nto = nto_excitation(states, 1)

origin, npts, dvec, points = make_box_grid(ao.coords, padding=5.0, spacing=0.15)
dV = dvec[0] * dvec[1] * dvec[2]
lambda_value, lambda_details = tozer_lambda(ao, nto, points, dV)

fragments = [[0, 1], [2, 3]]
omega = fragment_ct_matrix(states, ao, 1, fragments)

print("Participation ratio:", participation_ratio(nto["weights"]))
print("Tozer Lambda:", lambda_value)
print("Charge-transfer fraction:", omega["ct_fraction"])
```

Fragment atom indices are zero-based and follow the atom order in the OpenQP
input.

## Cube Export

`CubeExporter` writes Gaussian cube files for molecular orbitals and
MRSF-derived densities.

```python
from oqp.interop import CubeExporter, attachment_detachment, nto_excitation

target = 1
nto = nto_excitation(states, target)
ad = attachment_detachment(states, target)
cubes = CubeExporter(states, padding=5.0, spacing=0.15)

cubes.state_density_cube("S1_density.cube", target)
cubes.transition_density_cube("S0_to_S1.cube", 0, target)
cubes.attachment_detachment_cubes("S1_attach.cube", "S1_detach.cube", ad)
cubes.nto_cube("S1_hole_nto0.cube", nto["holes_ao"][:, 0], "S1 hole NTO 0")
cubes.nto_cube(
    "S1_particle_nto0.cube",
    nto["particles_ao"][:, 0],
    "S1 particle NTO 0",
)
```

The current cube evaluator supports Cartesian Gaussian basis functions. If a
pure spherical-harmonic basis is used, the analysis raises a clear error rather
than writing cube data with the wrong AO dimension.

## QCSchema And FCIDUMP

The QCSchema exporter returns a validating `AtomicResult` payload. Excited-state
data are stored in `extras["oqp"]` because QCSchema does not define standard
top-level fields for MRSF transition densities.

```python
import json
from oqp.interop import to_qcschema, validate_qcschema

payload = to_qcschema(mol, states=states)
result = validate_qcschema(payload)

with open("formaldehyde_qcschema.json", "w") as handle:
    json.dump(payload, handle, indent=2)

print(result.extras["oqp"]["excitation_energies_ev"])
```

FCIDUMP export delegates to `oqp.quantum`, using OpenQP's native one- and
two-electron integrals in the OpenQP MO basis.

```python
from oqp.interop import dump_fcidump, verify_fcidump_fci

metadata = dump_fcidump("reference.FCIDUMP", mol)
print(metadata["engine"])

# Optional cross-check when PySCF is installed.
check = verify_fcidump_fci("reference.FCIDUMP", mol)
print(check["diff"])
```

## External Comparisons

The parser and comparison helpers normalize OQP, cclib, and PySCF excited-state
results into the same dictionary shape.

```python
from oqp.interop import (
    parse_oqp,
    parse_output,
    compare_results,
    format_table,
)

oqp_result = parse_oqp(mol, states)
external = parse_output("gaussian_td.log", program="gaussian")

rows, ok = compare_results(
    oqp_result,
    external,
    {
        "scf_energy_ha": 1.0e-6,
        "excitation_energies_ev": 0.05,
        "oscillator_strengths": 0.02,
    },
    ref_label="OpenQP",
    other_label="Gaussian",
)

print(format_table(rows, ref_label="OpenQP", other_label="Gaussian"))
```

Array length mismatches are reported as failures instead of silently comparing
only the shared prefix.

## Scope And Limits

- The toolkit requires a completed MRSF energy run with `[tdhf] type=mrsf`.
  UMRSF runs do not publish the MRSF state-interaction density tags.
- Attachment/detachment densities are unrelaxed. They do not include orbital
  relaxation from the MRSF gradient Z-vector path.
- Cube generation currently uses the Python Cartesian-GTO evaluator. Use a
  Cartesian basis for cube export until pure spherical-grid support is added.
- Optional validation paths may require extra Python packages such as
  `qcelemental`, `cclib`, or `pyscf`.
