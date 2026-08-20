# OQP Studio: What Other GUIs Provide

A working list of the features published quantum-chemistry GUIs offer, what OQP
Studio does about each, and why the remaining gaps are still gaps. The point is
to keep the comparison concrete: every "planned" row below is a decision to be
argued with, not a wish.

The programs surveyed are the ones an OpenQP user is most likely to have
already: **wxMacMolPlt** (Bode/Gordon, the GAMESS companion), **IQmol**
(Gilbert, Q-Chem), **Avogadro 2** (OpenChemistry), **GaussView** (Gaussian),
**Chemcraft**, **Molden**, **Jmol**, **VMD**, **PyMOL** and
**Schrödinger Maestro**.

## Building and importing

| Feature | Seen in | OQP Studio |
| --- | --- | --- |
| Draw in 2D, convert to 3D | ChemDraw, Avogadro, Maestro | Ketcher sketcher, RDKit ETKDGv3 + MMFF94 embedding |
| 3D builder with fragments | Avogadro, GaussView, Maestro | 2D route only — see below |
| Fetch from a public database | Avogadro, IQmol, Maestro | PubChem by name |
| Template library | GaussView, Maestro | 34 built-in samples |
| Read the code's own formats | all | `.oqp`, `.inp`, `.log`, `.json`, `.molden` |
| Read common exchange formats | all | XYZ, PDB, MOL/SDF, MOL2, CDXML, SMILES |
| Read trajectories | VMD, Molden, Chemcraft | NAMD `.trj`, multi-model PDB, optimisation logs |
| Z-matrix / internal coordinate editing | GaussView, Chemcraft | not planned; Cartesian editing only |

## Viewing

| Feature | Seen in | OQP Studio |
| --- | --- | --- |
| Ball-and-stick, wireframe, spacefill, surface | all | yes, plus Mol\*'s automatic preset |
| Protein cartoons | PyMOL, VMD, Maestro, Jmol | yes, for PDB input |
| Atom labels and numbering | MacMolPlt, GaussView | element symbol or atom number |
| Ambient occlusion, outlines, print background | IQmol, Maestro, PyMOL | yes |
| Measure distance, angle, dihedral by picking | MacMolPlt, Avogadro, GaussView | yes — 2, 3 or 4 atoms |
| Save the view as an image | all | PNG from the render buffer |
| Ray-traced publication render | PyMOL, Maestro | not yet; the offline path is sketched in the proposal |
| Animation / movie export | VMD, MacMolPlt | not yet |

## Orbitals and scalar fields

| Feature | Seen in | OQP Studio |
| --- | --- | --- |
| MO isosurfaces from a Molden file | Molden, MacMolPlt, IQmol | yes, Cartesian s–g shells |
| Phase colour, opacity, mesh or solid | MacMolPlt, IQmol | yes, with MacMolPlt / IQmol / print presets |
| Orbital energy level diagram | GaussView, IQmol | yes, frontier region, click a level to draw it |
| Electron density | Molden, GaussView, Chemcraft | yes |
| Spin density | GaussView, Chemcraft | yes (restricted, ROHF and unrestricted files) |
| Electrostatic potential | GaussView, MacMolPlt, IQmol | yes, from atomic charges — see the caveat below |
| ESP mapped onto a density surface | GaussView, Maestro, PyMOL | not yet; needs per-vertex colouring |
| NTOs, attachment/detachment densities | IQmol, Q-Chem tools | not yet; needs `oqp.interop` in-process |
| Spherical (5D/7F) Molden files | Molden, Chemcraft | refused with a clear message rather than drawn wrongly |

The electrostatic potential deserves the caveat spelled out. OQP Studio builds
it as `V(r) = Σ q_A / |r − R_A|` from atomic partial charges: RESP or Löwdin
charges when the run exported them, Mulliken charges computed here from the
Molden orbitals and an analytic Gaussian overlap otherwise. That is the
charge-model MEP, not the exact density integral
`Σ Z_A/|r−R_A| − ∫ ρ(r′)/|r−r′| dr′`. It has the right sign structure and the
right qualitative shape, and it is what several viewers draw; it is not
quantitative near the nuclei. The exact form needs nuclear-attraction integrals
over the basis at every grid point, which is a real integral engine rather than
a grid loop.

## Results and spectra

| Feature | Seen in | OQP Studio |
| --- | --- | --- |
| Energies, components, convergence | all | yes |
| Thermochemistry (ZPE, U, H, G) | GaussView, Chemcraft | yes, read from the log |
| Dipole moment | all | yes, a.u. and Debye |
| Partial charges | GaussView, Chemcraft, IQmol | yes |
| Point group | GaussView, Chemcraft | yes, when the run recorded it |
| Vibrational frequency table | all | yes, with IR and Raman intensities |
| Normal mode animation | MacMolPlt, GaussView, Molden | yes, amplitude adjustable |
| Normal mode displacement arrows | MacMolPlt, Chemcraft | not yet |
| IR and Raman spectra | GaussView, Chemcraft, MacMolPlt | yes |
| UV/Vis absorption spectrum | GaussView, Chemcraft, IQmol | yes |
| Emission and excited-state absorption | rare — Chemcraft partially | yes, from the same state list |
| Choice of line shape | GaussView (Lorentzian/Gaussian) | Lorentzian (default), Gaussian, pseudo-Voigt |
| Spectrum data export | Chemcraft, GaussView | CSV, curve plus sticks |
| Optimisation energy profile plot | GaussView, Chemcraft | not yet; the geometries already animate |

### Why Lorentzian is the default

A stick spectrum is a set of delta functions. Homogeneous broadening — finite
excited-state lifetime — gives each line a Lorentzian profile, so a Lorentzian
convolution is the one with a physical origin rather than a numerical
convenience. A Gaussian is the right choice for inhomogeneous broadening
(sample disorder, unresolved rotational structure) and it decays far too fast
in the wings to reproduce a measured band. Real spectra usually sit between the
two, which is what the pseudo-Voigt option is for. Widths are entered as FWHM,
in cm⁻¹ for vibrational spectra and eV for electronic ones, and every profile
is normalized so peak heights track intensities rather than the width setting.

## Running calculations

| Feature | Seen in | OQP Studio |
| --- | --- | --- |
| Build input from a form | GaussView, Maestro, IQmol | workflow cards plus an options panel |
| Run locally from the GUI | IQmol, Avogadro, Maestro | in-process pyoqp, native binary, or WSL |
| Live log | IQmol, Maestro | yes |
| Queue / remote submission | IQmol, Maestro | not yet; one job at a time, locally |
| Recover past jobs after a restart | Maestro | yes, job directories are adopted at startup |

## What is deliberately not planned

- **Force-field optimisation in the GUI.** Avogadro's main draw, but OpenQP is
  the engine here; a second energy model in the viewer would only confuse which
  numbers came from where. RDKit's MMFF is used for 2D→3D embedding and nothing
  else.
- **A scripting console.** OpenQP already has a documented Python API, and the
  jobs the GUI writes are ordinary input files. A console inside the app would
  be a worse version of a terminal beside it.
- **Editing a structure by dragging atoms in 3D.** Attractive, and a large
  amount of interaction code for something the coordinate table already does
  precisely.
