# OpenQP Studio — Design Proposal

Status: draft proposal (2026-08)

This document proposes **OpenQP Studio**, a single cross-platform
(Windows / macOS / Linux) desktop application that unifies the currently
separate OpenQP graphical tools — OpenQP Web, the Input Generator, and
OpenqpView — and adds the missing pieces: molecule building, public-database
import, predefined calculation templates, direct local execution of OpenQP,
and publication-quality molecular graphics (molecular orbitals, densities,
normal modes, spectra).

It is informed by a survey of existing quantum chemistry GUIs:
[GaussView](https://gaussian.com/gaussview6/) (the UX benchmark for the
build → submit → analyze loop),
[wxMacMolPlt](https://github.com/brettbode/wxmacmolplt) (GPL v2, C++/wxWidgets,
GAMESS-oriented; jobs submitted via GamessQ),
[IQmol](https://www.iqmol.org/) (Qt/C++, Q-Chem-integrated, local and remote
job submission), and
[Avogadro 2](https://avogadro.cc/) (BSD-3, modern multithreaded renderer with
ambient occlusion and real-time shadows), and
[Schrödinger Maestro](https://www.schrodinger.com/platform/products/maestro/)
(commercial; the industry's visual high bar — its polished dark workspace,
soft studio lighting, depth-cued shading, and coherent entry/project model
define what "beautiful" means for this proposal).

## 1. Goals

1. **One application, whole loop**: sketch or import a molecule → choose a
   template → generate a validated `.oqp` input → run OpenQP locally (or
   remotely) → watch progress → analyze results, without leaving the app.
2. **Three input paths**:
   - draw structures (2D sketch with automatic 3D embedding, plus direct 3D
     editing),
   - fetch from public databases (PubChem by name/CID/SMILES; PDB and COD
     later),
   - start from predefined templates (molecules *and* calculation recipes
     matching the documented OpenQP workflows: MRSF-TDDFT excited states,
     SF-TDDFT, optimization, Hessian/frequencies, MECI search, SOC, NACME,
     EKT/Dyson, …).
3. **Beautiful, publication-grade graphics** on par with or better than
   IQmol and Avogadro 2: smooth MO isosurfaces, ambient-occlusion shading,
   style presets, high-resolution export.
4. **Cross-platform from one codebase**, installable as a normal app
   (MSI/DMG/AppImage), with the same UI also deployable as a website.
5. **Permissive licensing** compatible with the OpenQP ecosystem (no GPL
   code reuse; wxMacMolPlt is a UX reference only).

## 2. Recommended architecture

**Web-technology frontend + Python backend + lightweight desktop shell.**

```
┌────────────────────────────── OpenQP Studio ─────────────────────────────┐
│  Desktop shell: Tauri 2 (preferred) or Electron                          │
│  ┌──────────────────────────┐      ┌───────────────────────────────────┐ │
│  │ Frontend (TypeScript)    │ HTTP │ Local backend (Python, FastAPI)   │ │
│  │  • Builder (Ketcher 2D,  │◄────►│  • RDKit: SMILES→3D, MMFF pre-opt │ │
│  │    3D editor)            │  WS  │  • pyoqp: run jobs in-process     │ │
│  │  • Template & DB browser │      │  • Job queue (GamessQ-like)       │ │
│  │  • Input form/editor     │      │  • Grid engine: molden→MO cubes   │ │
│  │  • Mol*-based 3D viewer  │      │  • Parsers shared w/ OpenqpView   │ │
│  │  • Spectra/plots         │      │  • Execution adapters:            │ │
│  └──────────────────────────┘      │    local · WSL · SSH/SLURM        │ │
│                                    └───────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

Why this stack rather than a native C++/Qt application (the IQmol/Avogadro
route):

- **OpenQP is Python-driven.** The backend can `import pyoqp` and run jobs
  in-process with live callbacks — a tighter integration than any external
  GUI shelling out to a binary. This is the structural advantage GaussView
  has with Gaussian, obtained almost for free.
- **The parsers already exist.** OpenqpView already reads OpenQP `.log`,
  `.json`, `.hess.json`, Molden, cube, and XYZ. That code moves into the
  Studio frontend unchanged; a C++ fork of wxMacMolPlt or an Avogadro plugin
  would re-implement all of it.
- **One codebase, two deployments.** The same frontend serves as the desktop
  app and as the successor of OpenQP Web / OpenqpView online (browser mode
  simply hides the Run panel).
- **Rendering quality is no longer a native-code advantage.**
  [Mol*](https://molstar.org/) (MIT) is the renderer behind RCSB PDB,
  supports volumetric isosurfaces from cube-style grids, and produces
  publication-quality WebGL output; VTX and Mol* demonstrate that web/GPU
  rendering matches desktop GL quality.

### Key components (all permissive licenses)

| Concern | Component | License |
|---|---|---|
| Desktop shell, auto-update, installers | Tauri 2 (fallback: Electron) | MIT/Apache-2.0 |
| 3D molecular rendering | Mol* (custom OpenQP theme) | MIT |
| 2D structure sketcher | Ketcher | Apache-2.0 |
| SMILES → 3D, force-field pre-optimization | RDKit (backend) | BSD-3 |
| Optional fast pre-optimization | xtb (optional dependency) | LGPL (called as subprocess) |
| Database import | PubChem PUG REST; later PDB, COD | public APIs |
| Backend server | FastAPI + uvicorn, packaged with PyInstaller | MIT/BSD |
| Job engine | pyoqp (in-process) + queue manager | OpenQP |

### Running the Fortran core on each OS

The Studio treats execution as pluggable **backends**, in the spirit of
IQmol's server concept and GamessQ's queue:

1. **Local native** — the platform OpenQP build (Linux/macOS today; the
   in-progress native Windows build when ready).
2. **WSL bridge (Windows)** — until the native Windows port is stable, the
   Studio transparently invokes OpenQP inside WSL (`wsl openqp …`), sharing
   files via the WSL filesystem. Users get the full GUI experience on
   Windows on day one.
3. **Remote SSH / SLURM** — submit to a cluster, monitor, and pull results
   back (Phase 3).

This decouples GUI availability from the Windows-port timeline: the GUI ships
on all three OSs immediately; execution backends improve underneath it.

## 3. Feature design

### 3.1 Build (input side)

- **Sketch tab**: Ketcher 2D drawing → RDKit 3D embedding + MMFF/UFF clean-up
  → editable 3D structure. Optional xtb pre-optimization button.
- **3D edit**: add/delete atoms and bonds, drag atoms, adjust bond
  lengths/angles/dihedrals, fragment library (functional groups, common
  ligands), point-group detection (reusing OpenQP's symmetry module through
  the backend).
- **Import**: PubChem search by name/CID/SMILES; file open for XYZ, Molden,
  previous OpenQP outputs, SDF/MOL.
- **Templates**, two orthogonal kinds:
  - *molecule templates*: curated set (the documented examples: H₂O, PSB3,
    thymine, …) plus user-saved fragments;
  - *calculation templates*: one per documented workflow
    (single point, optimization, Hessian → IR/Raman, MRSF-TDDFT absorption,
    MECI search, SOC, NACME, EKT), each pre-filling `[input]/[scf]/[tdhf]/…`
    groups with recommended defaults and exposing the few knobs users
    actually change.
- **Input editor**: form view generated from the keyword documentation
  (this docs site's keyword pages become a machine-readable schema), plus a
  synchronized raw-text view with validation via the existing
  input-validation API before submission.

### 3.2 Run

- GaussView-style **Submit** and **Quick Launch**; GamessQ-style queue panel
  (pending/running/done, CPU/memory, kill/requeue).
- Live log tail, SCF convergence and optimization-energy plots streaming
  over WebSocket while the job runs.
- Project folders: every job keeps input, log, JSON, Molden, cubes together;
  recent-projects browser.

### 3.3 Analyze (the "beautiful graphics" pass)

Rendering is Mol* with an OpenQP visual theme. The bar to clear, in order:
Avogadro 2's ambient-occlusion look, IQmol's clean orbital surfaces, and
ultimately Maestro's overall visual coherence. Concretely, the Maestro-derived
principles are: **great defaults, zero tweaking** (the first render of any
molecule must look publication-ready); a calm dark workspace with soft
multi-light studio shading, subtle ambient occlusion, and depth cueing/fog;
restrained, consistent color language shared by the 3D scene, plots, and UI
chrome; and smooth, damped camera motion. Mol*'s post-processing pipeline
(SSAO, outlines, fog, adjustable lighting presets) supports all of these in
WebGL today.

- **MO viewer**: orbital list with energies and an interactive MO energy-level
  diagram; click an orbital → backend evaluates it from the Molden basis onto
  a grid (NumPy, cached) → smooth two-lobe isosurface with adjustable isovalue
  and transparency. Densities, spin densities, and OpenQP-specific surfaces:
  MRSF response densities, NTOs, EKT **Dyson orbitals**.
- **Vibrations**: mode list with frequencies, animated displacement vectors,
  IR/Raman spectrum panel with adjustable broadening; click a band → animate
  that mode.
- **Excited states**: UV-Vis stick + broadened spectrum from MRSF-TDDFT
  output; state table with oscillator strengths; NTO pairs side by side.
- **Geometry**: optimization/IRC/MECI trajectory playback, measurement tools,
  overlay of two structures with RMSD.
- **Style system**: presets ("Publication" white/soft-AO, "Presentation"
  dark/glossy, "Print" line-art), element palettes, per-scene lighting
  (ambient occlusion, outline, fresnel rim), and one-click export:
  PNG at arbitrary DPI with transparent background, and turntable/mode
  animations as MP4/GIF.

## 4. Alternatives considered

- **Fork wxMacMolPlt** — fastest path to *a* Windows GUI (VS build files
  exist), but GPL v2, a dated C++/wxWidgets codebase, every OpenQP parser and
  the input writer written from scratch, and graphics far behind IQmol /
  Avogadro 2. Rejected as the main line; retained as a UX reference
  (its GAMESS input builder and surface dialogs are still excellent design
  studies).
- **Build on Avogadro 2 / avogadrolibs** — BSD-3, beautiful renderer, plugin
  architecture. Rejected as the *primary* vehicle because OpenQP-specific
  analysis (MRSF states, Dyson orbitals, `.json` results) would live awkwardly
  in plugins, and the web assets could not be reused. **Recommended as a
  parallel low-cost channel**: contribute an OpenQP input generator and
  output reader to Avogadro so its large existing user base can discover
  OpenQP (~1–2 weeks of work, mostly Python).
- **Native Qt/C++ app like IQmol** — matches the rendering bar but forfeits
  the pyoqp in-process advantage, the OpenqpView code reuse, and the
  web deployment; highest long-term maintenance cost.

## 5. Roadmap

| Phase | Scope | Outcome |
|---|---|---|
| **0. MVP loop** (~1 month) | Monorepo; Tauri shell wrapping OpenqpView; FastAPI backend running pyoqp locally (+ WSL bridge on Windows); Submit button, queue panel, live log. | GaussView-style run-and-view loop on all three OSs. |
| **1. Build side** (~2 months) | Ketcher, RDKit 3D, PubChem import, molecule + calculation templates, keyword-schema input forms with validation. | Full input pipeline; no hand-written inputs needed. |
| **2. Analysis & beauty** (~2–3 months) | Mol* renderer with OpenQP theme, MO/NTO/Dyson viewers, MO diagram, spectra panels, vibration animation, style presets, high-DPI export. | Graphics at or above IQmol/Avogadro 2 quality. |
| **3. Scale-out** (~2 months) | SSH/SLURM backend, project management, auto-update, signed installers; Avogadro plugin released in parallel. | 1.0 release. |

Total: roughly 6–8 months for one focused developer plus part-time help on
the scientific viewers; Phases 1 and 2 can proceed in parallel with two
contributors.

## 6. Immediate next steps

1. Approve the stack (Tauri + TypeScript/Mol* frontend + FastAPI/pyoqp
   backend) and the name *OpenQP Studio*.
2. Create the `open-quantum-platform/openqp-studio` monorepo
   (`frontend/`, `backend/`, `shell/`, shared `parsers/` extracted from
   OpenqpView).
3. Build the Phase-0 MVP against the current OpenQP release, with the WSL
   bridge standing in for the native Windows core.
4. Convert the keyword documentation in this repository into the JSON schema
   that drives the input forms (single source of truth for docs and GUI).
