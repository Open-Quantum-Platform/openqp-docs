# OpenQP Documentation

This repository contains the user manual for
[OpenQP](https://github.com/Open-Quantum-Platform/openqp), the Open Quantum
Platform.

The manual covers installation, input files, Python usage, build options,
capabilities, examples, keyword references, and workflows including HF/DFT,
MP2, TDHF/TDDFT, SF-TDDFT, MRSF-TDDFT, PCM/ddX, SOC, NACME, EKT, Hessians,
optimization, and spectroscopy-related properties.

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

## Maintenance

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
