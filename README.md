# OpenQP Documentation

This repository contains the user manual for
[OpenQP](https://github.com/Open-Quantum-Platform/openqp), the Open Quantum
Platform.

The manual covers the OQP Studio desktop application, installation, input
files, Python usage, build options, capabilities, examples, keyword references,
and workflows including HF/DFT, MP2, coupled cluster (native CCSD/CCSD(T) and
the external CCpy library from Python), TDHF/TDDFT, SF-TDDFT, MRSF-TDDFT,
PCM/ddX, SOC, NACME, EKT, Hessians, optimization, molecular symmetry,
spectroscopy-related properties, and ODP umbrella sampling in NVT and periodic
QM/MM nonadiabatic dynamics (`[odp]`), including the FlexiBLE solvent boundary
(`[flexible]`).

Manual site:
[https://open-quantum-platform.github.io/openqp-docs/](https://open-quantum-platform.github.io/openqp-docs/)

API guide:
[https://open-quantum-platform.github.io/openqp-docs/api/](https://open-quantum-platform.github.io/openqp-docs/api/)

## Preview Locally

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

## Build

```bash
mkdocs build --strict
```

## Build the full 1.4 manual locally

```bash
mkdocs build --strict
CI_PAGES_URL=http://localhost:8000 OQP_MANUAL_RELEASE_REF=release/1.4 \
  python tools/build_private_manual.py
python -m http.server --bind 127.0.0.1 --directory site 8000
```

Open `/manual/` to select a version. The 1.4 build stages the complete
`docs/` tree and applies only the changes in `release-notes/1.4/`.
`overlay.json` defines exact replacements in shared pages, appended content,
and the extra release navigation. Edit common material in `docs/`; use the
overlay for changes that apply only to 1.4. A stale or ambiguous replacement
fails the build so updates to common pages cannot silently leave old wording
in the versioned manual.

## Maintenance

Development is maintained in the Open Quantum Platform group's GitLab project.
Use GitLab branches and merge requests for new documentation changes; its
`mkdocs build --strict` pipeline must pass before merging.

GitHub remains the public mirror and hosts the published manual. Updates to
GitHub `main` automatically create a GitLab synchronization merge request when
needed. That request is merged only after GitLab CI succeeds. Conflicts remain
visible for manual resolution. Updates from GitLab to GitHub are made on demand,
after checking that `main` is suitable for public release. Automatic outbound
mirroring stays disabled; private branches and archived pull-request refs must
not be published. The existing GitHub Pages workflow publishes the manual when
GitHub `main` is updated.

Keep keyword and API pages aligned with the OpenQP input schema, checker, and
Python entry points:

- [`oqpdata.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/molecule/oqpdata.py)
- [`input_checker.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/utils/input_checker.py)
- [`single_point.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/library/single_point.py)
- [`pyoqp.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/pyoqp.py)
- [`openqp.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/openqp.py)
- [`molecule.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/molecule/molecule.py)
- [`oqp.h`](https://github.com/Open-Quantum-Platform/openqp/blob/main/include/oqp.h)
- [`CMakeLists.txt`](https://github.com/Open-Quantum-Platform/openqp/blob/main/CMakeLists.txt)
- [`pyproject.toml`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyproject.toml)

When OpenQP changes input defaults, allowed values, workflow support, or Python
runner behavior, update the matching page under `docs/keywords`,
`docs/workflows`, `docs/api`, `docs/python-scripting.md`, or
`docs/build-options.md`. Also update this README when a new workflow, keyword
section, or maintenance source file becomes part of the documented surface.
