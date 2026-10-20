# Worked Examples

Each worked example is one small molecule, one complete `.oqp` input that you
can copy and run as it is, and the results that the run produces. The
coordinates are written inside the input, so no separate geometry file is
needed. Some examples need extra files, downloaded with them into the same
folder: the [QM/MM examples](formaldehyde-qmmm.md) read their structure and force
field from a PDB file and two OpenMM XML files, and the all-electron inputs of
the [gold hydride example](auh-relativity.md) read an uncontracted basis set
from a JSON file. Run the input, then compare your numbers with the reference values on
the page.

```bash
openqp water-scf.oqp
```

Every input on these pages can also be downloaded from the link under its code
block. With 2 to 8 CPU threads, most runs take between 2 seconds and 1
minute. The path, conical-intersection, and dynamics examples take longer:
about 3.5 minutes for each IRC direction and for the MECI search, 4.5 minutes
for methanol MD, 5 minutes for the QM/MM dynamics, and 9 minutes for ethylene
NAMD. Each page states its run
time.

<div class="oqp-gallery" markdown>

<a class="oqp-card" href="water-scf/" markdown>
![Water](../assets/worked-examples/orb-water-side-homo.png)
<strong>Water energy and orbitals</strong>
<span>Total energy, orbital energies, HOMO and LUMO pictures, dipole moment, and atomic charges.</span>
</a>

<a class="oqp-card" href="formaldehyde-opt-freq/" markdown>
![Formaldehyde C=O stretch](../assets/worked-examples/mode-hcho-co-mode.png)
<strong>Geometry and vibrations</strong>
<span>Optimize formaldehyde, then compute harmonic frequencies, zero-point energy, and thermochemistry.</span>
</a>

<a class="oqp-card" href="formaldehyde-uv/" markdown>
![Formaldehyde pi* orbital](../assets/worked-examples/orb-hcho-side-lumo.png)
<strong>UV absorption (TDDFT)</strong>
<span>Excitation energies and oscillator strengths, and the orbitals behind the n→π* band.</span>
</a>

<a class="oqp-card" href="ethylene-twist/" markdown>
![Twisted ethylene](../assets/worked-examples/mol-ethylene-twisted.png)
<strong>Twisted ethylene (MRSF-TDDFT)</strong>
<span>S0, S1, and S2 along the C=C twist, where S0 becomes a diradical.</span>
</a>

<a class="oqp-card" href="formaldehyde-soc/" markdown>
![Formaldehyde](../assets/worked-examples/mol-hcho.png)
<strong>Spin-orbit coupling</strong>
<span>Singlet-triplet coupling matrix elements in cm⁻¹ and El-Sayed's rule.</span>
</a>

<a class="oqp-card" href="benzene-nmr/" markdown>
![Benzene](../assets/worked-examples/mol-benzene.png)
<strong>NMR chemical shifts</strong>
<span>GIAO shieldings of benzene and TMS, converted to ¹H and ¹³C chemical shifts.</span>
</a>

<a class="oqp-card" href="hcn-isomerization/" markdown>
![HCN transition state](../assets/worked-examples/mode-hcn-ts-mode.png)
<strong>Transition state and barrier</strong>
<span>Locate the HCN → HNC transition state, confirm one imaginary frequency, and compute the barrier.</span>
</a>

<a class="oqp-card" href="water-correlation/" markdown>
![Water](../assets/worked-examples/mol-water.png)
<strong>MP2 and CCSD(T) energies</strong>
<span>Correlation energies of water at the MP2 and CCSD(T) levels.</span>
</a>

<a class="oqp-card" href="h2-dissociation/" markdown>
![H2 dissociation](../assets/worked-examples/plot-h2-dissociation.svg)
<strong>H₂ dissociation: six methods</strong>
<span>RHF, UHF, PBE0, MP2, CASSCF, and CCSD along a breaking bond.</span>
</a>

<a class="oqp-card" href="allyl-radical/" markdown>
![Allyl spin density](../assets/worked-examples/spin-allyl.png)
<strong>Allyl radical spin density</strong>
<span>Open-shell UKS optimization, spin populations, and spin polarization.</span>
</a>

<a class="oqp-card" href="water-ekt/" markdown>
![Dyson orbital](../assets/worked-examples/dyson-water-1b1.png)
<strong>Ionization energies (MRSF-EKT)</strong>
<span>Ionization energies of water and the Dyson orbital of each ionization.</span>
</a>

<a class="oqp-card" href="benzene-acid/" markdown>
![ACID of benzene](../assets/worked-examples/acid-benzene.png)
<strong>Ring current (ACID)</strong>
<span>Current-density isosurface showing the aromatic ring current of benzene.</span>
</a>

<a class="oqp-card" href="methanol-md/" markdown>
![Methanol MD](../assets/worked-examples/plot-methanol-md.svg)
<strong>Ground-state MD</strong>
<span>200 fs of Born–Oppenheimer dynamics and an energy-conservation check.</span>
</a>

<a class="oqp-card" href="ethylene-meci/" markdown>
![Conical intersection](../assets/worked-examples/plot-meci-cone.png)
<strong>Conical intersection (MECI)</strong>
<span>Locate the S0/S1 MECI of ethylene, its g and h vectors, and the cone.</span>
</a>

<a class="oqp-card" href="ethylene-namd/" markdown>
![Ethylene NAMD](../assets/worked-examples/plot-ethylene-namd.svg)
<strong>Nonadiabatic dynamics</strong>
<span>Surface hopping from S1: twisting and return to S0 in 100 fs.</span>
</a>

<a class="oqp-card" href="ethylene-sf-tddft/" markdown>
![SF-TDDFT roots](../assets/worked-examples/plot-sf-twist.svg)
<strong>SF-TDDFT and spin contamination</strong>
<span>SF-TDDFT roots of ethylene identified by ⟨S²⟩, compared with MRSF-TDDFT.</span>
</a>

<a class="oqp-card" href="lih-caspt2/" markdown>
![LiH dissociation](../assets/worked-examples/plot-lih-dissociation.svg)
<strong>CASSCF and CASPT2 vs FCI</strong>
<span>LiH dissociation with RHF, UHF, CASSCF, CASPT2, CCSD(T), and exact FCI.</span>
</a>

<a class="oqp-card" href="formaldehyde-qmmm/" markdown>
![Formaldehyde with water](../assets/worked-examples/mol-hcho-2water.png)
<strong>QM/MM solvent shift</strong>
<span>n→π* shift of formaldehyde from two water molecules, QM/MM vs full QM.</span>
</a>

<a class="oqp-card" href="auh-relativity/" markdown>
![AuH curves](../assets/worked-examples/plot-auh-curves.svg)
<strong>Relativity in gold hydride</strong>
<span>Non-relativistic vs DKH2 vs relativistic ECP: the Au–H bond shrinks by 0.2 Å.</span>
</a>

<a class="oqp-card" href="hi-ecp/" markdown>
![HI sigma orbital](../assets/worked-examples/orb-hi-sigma.png)
<strong>Effective core potentials</strong>
<span>HI with the def2-SVP ECP: optimization, frequency, dipole, valence orbitals.</span>
</a>

<a class="oqp-card" href="ethylene-mecp/" markdown>
![MECP](../assets/worked-examples/plot-mecp-twist.svg)
<strong>Singlet–triplet crossing (MECP)</strong>
<span>S0/T0 minimum-energy crossing point of ethylene and the spin-orbit coupling there.</span>
</a>

<a class="oqp-card" href="formaldehyde-qmmm-namd/" markdown>
![QM/MM NAMD](../assets/worked-examples/plot-qmmm-namd.svg)
<strong>QM/MM excited-state dynamics</strong>
<span>Formaldehyde on S1 with two MM waters: pyramidalization and H-bond breaking.</span>
</a>

</div>

## How the reference values were produced

All reference values on these pages come from running exactly the inputs shown,
with OpenQP 1.3.1 (GitHub `main`, commit `f5361a2`, 20 October 2026) on macOS
x86_64 with 2 to 8 OpenMP threads. Molecule and orbital pictures are snapshots
of the [OQP Studio](../studio/index.md) 3D viewer, made from the output files of
the same runs.

On another computer, SCF energies normally agree with the reference values to
about 10⁻⁶ hartree. Small differences in the last digits come from DFT
integration grids, thread counts, and convergence thresholds. They are not
errors.

Where an independent code was available, the reference values were also checked
against PySCF 2.13 at the same geometry and basis set. Each page states which
values were checked.

## Reading an OpenQP run

Every run writes these files beside the input:

| File | Contents |
| --- | --- |
| `<name>.log` | The full text output, including SCF iterations, orbital energies, and all requested properties. Each page quotes the relevant part. |
| `<name>_scf_*.molden` | Molecular orbitals in Molden format. Open it in OQP Studio Analysis, [OpenqpView](https://open-quantum-platform.github.io/OpenqpView/), Molden, or Avogadro to display orbitals. |
| `<name>.hess.json`, `<name>.freq.molden` | Written by Hessian runs: frequencies, normal modes, and thermochemistry data. Open the `.freq.molden` file to animate the vibrations. |
| `opt.xyz`, `opt_status.txt` | Written by geometry optimizations and transition-state searches: the final geometry and a table of the optimization steps. |

The end of every log has an `ENERGIES AND STATES` block, which is the quickest
place to read the final energies:

```text
   PyOQP LOG | ENERGIES AND STATES
   PyOQP: Final Energy
   ========================================================================
   PyOQP Energy unit:                 Hartree
   PyOQP electronic energies
   PyOQP state 0                            -76.3256993935
```

For the full input syntax, see [`.oqp` Input](../oqp-input.md). For larger
template decks, see the [repository examples](../examples/index.md).
