"""MRSF-TDDFT of formaldehyde from Python, with NTO and attachment/detachment analysis."""
from oqp.openqp import OpenQP
from oqp.interop import MRSFExcitedStates, nto_transition, attachment_detachment
from oqp.export.cubegen import CubeExporter

job = OpenQP("formaldehyde_mrsf", silent=1)
job.molecule(
    """
C      0.000000     0.000000    -0.526342
O      0.000000     0.000000     0.676110
H      0.000000     0.937620    -1.119884
H      0.000000    -0.937620    -1.119884
""",
    charge=0,
)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=4)
mol = job.run()

results = mol.get_results()
ref = results["energy"]                # internal high-spin triplet reference
for n, de in enumerate(results["td_energies"]):   # state energies relative to it
    print(f"S{n}: {ref + de:.7f} hartree")

states = MRSFExcitedStates(mol)
cubes = CubeExporter(states)
for n in (1, 2):
    nto = nto_transition(states, 0, n)
    ad = attachment_detachment(states, n)
    print(f"S0 -> S{n}: oscillator strength {states.oscillator_strength(0, n):.4f}, "
          f"leading NTO weight {nto['weights'][0] / nto['weights'].sum():.3f}, "
          f"promoted electrons {ad['n_promoted']:.3f}")
    cubes.nto_cube(f"S{n}_hole.cube", nto["holes_ao"][:, 0], f"S{n} hole")
    cubes.nto_cube(f"S{n}_particle.cube", nto["particles_ao"][:, 0], f"S{n} particle")
    cubes.attachment_detachment_cubes(f"S{n}_attach.cube", f"S{n}_detach.cube", ad)
