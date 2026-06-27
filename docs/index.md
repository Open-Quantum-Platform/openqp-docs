# OpenQP Manual

Open Quantum Platform (OpenQP) is a quantum chemistry package centered on
HF/DFT, TDHF/TDDFT, SF-TDDFT, MRSF-TDDFT, and related workflows for
multiconfigurational ground and excited states.
The manual is organized around what users usually need first: install OpenQP,
prepare an input, run a calculation, then look up keywords when a workflow needs
more control. The lower-level API reference is intentionally placed last, after
workflows and keywords.

## Start Here

- [Installation](installation.md): package install, source build, BLAS/LAPACK,
  OpenMP, MPI, and runtime-file layout.
- [Build Options](build-options.md): complete CMake options, package-build
  overrides, BLAS/LAPACK choices, and external dependency cache behavior.
- [Quickstart](quickstart.md): the shortest path from a molecule to an OpenQP
  output file.
- [Run OpenQP from Python](python-scripting.md): drive complete OpenQP
  calculations from Python scripts, notebooks, or workflow managers.
- [Input Files](input-file.md): section layout, geometry input, run types, and
  output files.
- [Examples](examples/index.md): runnable inputs stored in the OpenQP code
  repository.
- [References](references.md): platform, MRSF-TDDFT, SOC, and PCM/ddX papers
  cited by the manual.

## Common Workflows

- Ground-state [HF and DFT](workflows/hf-dft.md)
- [MRSF-TDDFT](workflows/mrsf-tddft.md) energies and gradients
- Geometry [optimization](workflows/optimization.md)
- [Spin-orbit coupling](workflows/soc.md)
- [NACME](workflows/nacme.md)
- Energy-only [PCM/ddX](workflows/pcm.md)
- [MRSF-EKT](workflows/ekt.md) ionization potentials and electron affinities
- [NMR, IR, and Raman](workflows/nmr-ir-raman.md)

## Keyword Reference

The [keyword reference](keywords/index.md) is the code-aligned lookup layer for
high-drift input sections such as `[input]`, `[scf]`, `[optimize]`, `[oqp]`,
`[pcm]`, and `[symmetry]`. It should be checked against
[`pyoqp/oqp/molecule/oqpdata.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/molecule/oqpdata.py)
and
[`pyoqp/oqp/utils/input_checker.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/utils/input_checker.py)
when OpenQP changes.

## API Documentation

The [Run OpenQP from Python](python-scripting.md) chapter shows complete
script-based calculations next to ordinary workflow input files. The
[API chapter](api/index.md) appears last in the manual and is the lower-level
reference for `oqp.pyoqp.Runner`, in-memory inputs, result extraction through
`runner.mol`, and the input-checking API used by front ends and automated
workflows.

## Web Tools

- [OpenQP Web](https://app.openqp.org/) prepares inputs in the browser and
  previews structures locally.
- [OpenQP Input Generator](https://open-quantum-platform.github.io/OpenQP_Input_Generator/)
  provides a browser-based input builder.
- [OpenqpView](https://open-quantum-platform.github.io/OpenqpView/) inspects
  OpenQP logs, JSON, Molden, cube, and XYZ data in the browser.
