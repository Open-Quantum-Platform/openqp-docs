# OpenQP Documentation

This repository contains the user manual for
[OpenQP](https://github.com/Open-Quantum-Platform/openqp), the Open Quantum
Platform.

Manual site:
[https://open-quantum-platform.github.io/openqp-docs/](https://open-quantum-platform.github.io/openqp-docs/)

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

Keep keyword pages aligned with the OpenQP input schema and checker:

- [`oqpdata.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/molecule/oqpdata.py)
- [`input_checker.py`](https://github.com/Open-Quantum-Platform/openqp/blob/main/pyoqp/oqp/utils/input_checker.py)

When OpenQP changes input defaults, allowed values, or workflow support, update
the matching page under `docs/keywords` or `docs/workflows`.
