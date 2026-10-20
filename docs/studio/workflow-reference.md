# Workflow Scientific Reference

This chapter explains the scientific purpose of every calculation available in
the OQP Studio Workflow menu. It supplements the keyword reference: the form
controls determine *how* a calculation is run, while this chapter explains
*what question* the calculation can answer and *what must be checked* before a
result is interpreted.

!!! important
    A completed process is not automatically a chemically meaningful result.
    Inspect convergence, electronic-state identity, structural stability, and
    method applicability for every calculation.

## Electronic structure at a fixed geometry

### Single-point energy

**Purpose.** A single-point calculation solves the electronic-structure
problem without changing the supplied nuclear coordinates. It is used to
compare conformers, evaluate a higher-level method on an optimized structure,
or provide the reference wavefunction and orbitals for subsequent properties.

**Interpretation.** Compare energies only when composition, charge,
multiplicity, Hamiltonian, basis, solvent model, and numerical settings are
consistent. An SCF energy is the reference energy for a response calculation;
it must not be labeled as an excited-state energy.

**Check.** Confirm electronic convergence, the intended charge and
multiplicity, and the absence of an unintended state or orbital occupation.

### Energy gradient

**Purpose.** The nuclear gradient is the first derivative of the electronic
energy with respect to nuclear coordinates. Its negative is the force used by
geometry optimization, reaction-path, and molecular-dynamics algorithms.

**Interpretation.** A small gradient indicates a stationary region only when
all relevant unconstrained coordinates are included. A selected excited-state
gradient belongs to that state at the current geometry and does not by itself
establish that the state is followed continuously along a path.

**Check.** Verify gradient norms, constrained coordinates, and the identity of
the target state.

### Molecular properties

**Purpose.** Property calculations characterize the electronic distribution
at a fixed geometry through populations, multipole moments, and available
state-resolved quantities. Population analyses are model-dependent partitions
of the density, not observables by themselves.

**Check.** State the population or property definition and compare values only
within the same definition, basis, and electronic-structure method.

### NMR shielding

**Purpose.** Magnetic response calculations give the nuclear shielding tensor.
The isotropic shielding is the tensor trace divided by three; a chemical shift
requires a consistently calculated or experimental reference compound.

**Check.** Use a geometry and solvent model appropriate to the experiment,
inspect tensor components when anisotropy matters, and do not report an
absolute shielding as an experimental chemical shift without referencing.

See [NMR, IR, and Raman](../workflows/nmr-ir-raman.md).

### ACID current density

**Purpose.** The anisotropy of the induced current density (ACID/AICD) depicts
the response of electronic current to an applied magnetic field. It can support
analysis of local and global ring currents when the field direction and
integration surface are defined.

**Check.** Treat an isosurface as a visualization of a response field, not a
standalone aromaticity index. Record the field direction, isovalue, and current
integration convention.

See [ACID current-density maps](../workflows/acid.md).

### PCM solvation

**Purpose.** A polarizable continuum model represents bulk dielectric response
around a molecular cavity. It captures continuum electrostatics but not a
specific hydrogen bond, ion pair, or other discrete solvent structure unless
those species are included explicitly.

**Check.** Record solvent, dielectric constant, cavity radii, and equilibrium
or nonequilibrium response. PCM requires an OpenQP engine built with ddX; the
menu remains unavailable in Studio packages where ddX is disabled.

See [PCM/ddX](../workflows/pcm.md).

## Structure and vibrational analysis

### Geometry optimization

**Purpose.** Geometry optimization searches for a stationary point on a chosen
potential-energy surface. The native OpenQP optimizer uses energies and
gradients in Cartesian or internal coordinates and updates an approximate
Hessian as the structure changes.

**Check.** Require all requested convergence criteria, then calculate a Hessian.
A minimum has no imaginary vibrational mode after translations and rotations
are removed. Constraints change the stationary-point definition and must be
reported.

See [Optimization](../workflows/optimization.md).

### Bond-distance scan

**Purpose.** A rigid scan evaluates fixed structures along one internuclear
distance. A relaxed scan optimizes the remaining degrees of freedom at each
distance. Scans reveal qualitative profiles and provide guesses for stationary
points, but the chosen distance may not be the true reaction coordinate.

**Check.** Look for discontinuous electronic states, failed optimization at an
individual point, hysteresis between forward and reverse scans, and omitted
coordinates that change along the process.

### Frequencies (Hessian)

**Purpose.** The mass-weighted energy Hessian gives harmonic normal modes and
frequencies. At a minimum it also supports zero-point and thermal corrections;
at a transition state its unstable mode identifies the local reaction
coordinate.

**Check.** A minimum should have zero imaginary modes and a first-order saddle
point one. Very low frequencies are sensitive to numerical noise and the
harmonic approximation. Inspect the animated displacement rather than relying
only on the signed frequency.

See [Hessian and frequencies](../workflows/hessian.md).

### Transition-state search

**Purpose.** A transition-state search targets a first-order saddle point:
maximum energy along one local coordinate and minimum energy along all others.
A chemically informed initial structure and approximate unstable mode greatly
improve the search.

**Check.** Convergence alone is insufficient. Require exactly one chemically
relevant imaginary mode and follow the intrinsic reaction coordinate in both
directions to establish the connected minima.

### Intrinsic reaction coordinate

**Purpose.** The IRC follows mass-weighted steepest descent away from a
transition state toward reactant and product valleys on the same electronic
surface.

**Check.** Run both directions, optimize the endpoints, and verify their
identity. An IRC is a local path from the supplied saddle point, not a kinetic
simulation or proof that competing pathways are absent.

### Minimum-energy path

**Purpose.** A minimum-energy path follows the energy surface using local
gradients and records structures and energies along a reaction or relaxation
coordinate. Depending on its starting point and algorithm, it need not pass
through the globally lowest barrier.

**Check.** Inspect structural continuity, state identity, step size, and energy
smoothness. Recalculate suspicious points rather than smoothing over a physical
state change or a failed step.

### Nudged elastic band

**Purpose.** NEB optimizes a chain of images between supplied endpoints. Spring
forces maintain path resolution while perpendicular physical forces relax the
path toward a minimum-energy connection.

**Check.** Endpoints must represent the intended structures. Verify image
spacing, force convergence, and adequate resolution near the highest-energy
region. Refine the maximum-energy image with a transition-state search and
Hessian when a saddle point is required.

## Excited states and spectra

### Vertical excited states

**Purpose.** A vertical calculation evaluates electronic states at fixed
nuclear coordinates. At a ground-state geometry, transitions from S0 and their
oscillator strengths define an absorption stick spectrum. Studio broadens the
sticks for visualization; the chosen line shape and width are presentation
parameters, not additional electronic-structure results.

**Check.** Inspect state character as well as state number, because energetic
ordering can change with geometry. Record excitation energy, oscillator
strength, broadening, and the geometry at which they were calculated.

### Excited-state gradient

**Purpose.** The derivative of a selected excited-state energy indicates the
initial direction of structural relaxation and supplies forces for
state-specific optimization or dynamics.

**Check.** Confirm state tracking from electronic character or overlaps. Near a
crossing, a fixed ordinal label such as S1 may exchange character with S2.

### Excited-state optimization

**Purpose.** This calculation relaxes a selected excited-state potential-energy
surface. A vertical transition from the relaxed excited-state geometry to a
lower state can be used for an emission estimate. Transitions from the current
excited state to higher states define excited-state absorption (ESA).

**Check.** Require geometrical convergence and continuous state identity. Do
not label a spectrum from an unrelaxed ground-state geometry as emission.
Emission and ESA wavelengths must use the relevant state-to-state energy
differences, not absolute total energies or differences relative to an
unrelated reference state.

### Nonadiabatic coupling

**Purpose.** A derivative coupling vector describes the first-order change of
electronic-state mixing with nuclear displacement. Together with the gradient
difference, it spans the branching plane that lifts a two-state conical
intersection.

**Check.** Specify the state pair, phase convention, geometry, and method.
Couplings become sharply geometry-dependent near degeneracy.

### NACME

**Purpose.** A nonadiabatic coupling matrix element is the state-to-state
coupling quantity used by the selected dynamical or electronic representation.
It is related to, but should not be confused with, a full Cartesian derivative
coupling vector.

**Check.** Report the representation, state pair, units, and any nuclear
velocity dependence used to form the matrix element.

### Spin-orbit coupling

**Purpose.** Spin-orbit matrix elements mix states of different spin
multiplicity and provide an electronic factor relevant to intersystem crossing.
Rates also depend on energy gaps, nuclear motion, and vibronic coupling.

**Check.** Inspect the complete state pair and component convention. A large
matrix element alone does not determine an intersystem-crossing rate.

See [Spin-orbit coupling](../workflows/soc.md).

### Ionization / electron affinity (EKT)

**Purpose.** The extended Koopmans theorem obtains ionization-potential and
electron-affinity states from reduced-density information. Dyson orbitals show
the one-electron overlap between the initial and ionized or electron-attached
state. They are distinct from SCF molecular orbitals and are state-specific.

**Check.** Identify whether a result is an IP or EA channel and name both
states. Studio reports Dyson strength and its corresponding occupation
contribution according to the OpenQP output convention.

See [MRSF-EKT](../workflows/ekt.md).

## Surface crossings

### MECI search

**Purpose.** A minimum-energy conical intersection (MECI) minimizes energy
subject to degeneracy of two states of the same spin symmetry. It identifies an
energetically accessible point in a crossing seam relevant to ultrafast
internal conversion.

**Check.** Require convergence of both the mean-energy optimization and the
state-energy gap. Inspect state character and, when available, the gradient-
difference and derivative-coupling directions. A small gap at an arbitrary
geometry is not by itself a converged MECI.

See [BaekA multistate MECI](../workflows/baeka-multistate-meci.md).

### MECP search

**Purpose.** A minimum-energy crossing point (MECP) minimizes energy under
equality of two states of different spin. It is a structural descriptor for a
spin-crossing region; spin-orbit and nuclear-motion information are needed for
a transition probability or rate.

**Check.** Verify the energy gap, constrained optimization criteria, spin
identity, and the spin-orbit coupling separately.

### Three-state intersection

**Purpose.** This search treats simultaneous near-degeneracy among three
electronic states. Such regions require a multistate description because three
pairwise gaps and state mixing can change together.

**Check.** Inspect all three energies, electronic characters, and convergence
conditions. Pairwise degeneracy of only two states does not establish a
three-state intersection.

## Dynamics

### Ground-state QM/MM dynamics

**Purpose.** Ground-state QM/MM molecular dynamics propagates a selected QM
region with OpenQP while OpenMM describes the surrounding force-field
environment. NVE follows an isolated trajectory, NVT applies a thermostat, and
NPT also applies pressure control to a periodic system.

**Check.** Validate the prepared PDB, force-field coverage, QM charge and spin,
boundary treatment, time step, constraints, and equilibration protocol. Monitor
total-energy drift in NVE and report thermostat or barostat parameters for NVT
or NPT. This driver is distinct from a generic gas-phase OpenQP gradient or
geometry optimization.

### Nonadiabatic dynamics

**Purpose.** Surface-hopping dynamics propagates nuclei while electronic
amplitudes evolve across coupled potential-energy surfaces. An ensemble of
trajectories estimates populations and branching behavior; one trajectory is
not a statistical prediction.

**Check.** Document initial-condition sampling, active state, time step,
electronic-state space, hopping/decoherence settings, random seeds, energy
conservation, failed trajectories, and ensemble size. State character should be
tracked through crossings.

See [SOC-NAMD-QM/MM](../workflows/soc-namd-qmmm.md) for the coupled dynamics
workflow and its additional requirements.

## Method selection

HF and DFT provide single-reference ground-state descriptions. Linear-response
TDDFT/TDA describe excitations around a reference determinant. Spin-flip and
MRSF-TDDFT methods are intended for situations where low-spin states require a
balanced description derived from a high-spin reference. CASSCF and
state-averaged CASSCF expose an explicit active space and are sensitive to its
orbital and electron selection. Post-SCF methods add correlation with different
cost and applicability.

No menu choice removes the need to test basis-set, functional, active-space,
state-space, and numerical convergence for the system under study. Consult the
[OpenQP workflow chapters](../workflows/hf-dft.md) and
[keyword reference](../keywords/index.md) for implementation-specific options.
