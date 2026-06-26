# API Documentation

OpenQP exposes several layers of programmatic access. Most users should start
with the Python runner API because it follows the same input model as an
ordinary `openqp input.inp` calculation while also returning Python objects for
post-processing.

## API Layers

| Layer | Entry point | Audience | Stability |
| --- | --- | --- | --- |
| Command line | `openqp input.inp` | Production runs, shell scripts, workflows | Stable |
| Python runner | `oqp.pyoqp.Runner` | Python automation and notebooks | Recommended |
| Molecule data | `runner.mol` | Result extraction and advanced workflows | Semi-stable |
| Input checker | `oqp.utils.input_checker.check_input_values` | Input builders, web forms, preflight validation | Recommended |
| Convenience wrapper | `oqp.openqp.OPENQP` | Compact dotted-key Python inputs | Experimental |
| C/Fortran handle | `include/oqp.h`, `oqp_handle_t` | OpenQP developers and native extensions | Internal |

The import package is `oqp`, even though the source tree contains a `pyoqp`
directory and the installable distribution is named `OpenQP`.

## Recommended Starting Points

- Use [Run OpenQP from Python](../python-scripting.md) for complete script-based
  calculation examples.
- Use [Python Runner](python-runner.md) to run calculations from scripts,
  notebooks, services, or tests.
- Use [Results and Molecule Data](results.md) to retrieve energies, gradients,
  orbitals, TDDFT arrays, SOC data, and serialized result dictionaries.
- Use [Input Validation](input-validation.md) when building forms, agents, or
  custom front ends that need actionable diagnostics before launching OpenQP.
- Use [Developer Interface](developer-interface.md) only when working on the
  native OpenQP bridge or adding kernels.

## Generated References

The manual pages above are the curated API guide. The older generated references
remain useful for source browsing:

- [Generated Python API reference](https://open-quantum-platform.github.io/openqp/sphinx/index.html)
- [Generated Fortran API reference](https://open-quantum-platform.github.io/openqp/ford/index.html)

Generated references can expose internal modules that are not intended as stable
user-facing APIs. Prefer the manual pages for supported scripting patterns.
