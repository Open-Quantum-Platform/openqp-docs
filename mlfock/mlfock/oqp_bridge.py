"""Glue between mlfock and OpenQP / openqp-dftb (optional imports only here).

* ``OpenQPOracle``   : geometry -> converged ROKS record (the on-the-fly oracle)
* ``run_reference``  : one-off ROKS run for a geometry
* ``run_mrsf_tddftb_with_reference`` : MRSF-TDDFTB response on an external
  reference file through the openqp-dftb adapter (OPENQP_DFTB_SIMPLE_MRSF_REF),
  i.e. the "simple-MRSF" path of openqp-dftb/tools/simple_mrsf.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
import numpy as np

from .extract import FockRecord, record_from_openqp

BOHR2ANG = 0.52917721067


def _stringify(config: dict) -> dict:
    return {sec: {k: str(v) for k, v in opts.items()} for sec, opts in config.items()}


def _geometry_text(Z, pos_bohr) -> str:
    from oqp.periodic_table import ELEMENTS_NAME  # noqa: PLC0415
    pos = np.asarray(pos_bohr, float).reshape(-1, 3) * BOHR2ANG
    return "\n".join(f"{ELEMENTS_NAME[int(z)]} {x:.10f} {y:.10f} {z_:.10f}"
                     for z, (x, y, z_) in zip(Z, pos))


def rohf_config(functional: str = "bhhlyp", basis: str = "6-31g*", charge: int = 0,
                multiplicity: int = 3, maxit: int = 100, conv: float | None = None) -> dict:
    cfg = {"input": {"system": "", "charge": charge, "method": "hf", "basis": basis,
                     "functional": functional, "runtype": "energy"},
           "scf": {"type": "rohf", "multiplicity": multiplicity, "maxit": maxit},
           "guess": {"type": "huckel"}}
    if conv is not None:
        cfg["scf"]["conv"] = conv
    return cfg


class OpenQPOracle:
    """Run the reference open-shell SCF in OpenQP for a geometry.

    A fresh Runner per geometry keeps the state simple; one ROKS/6-31G*
    water takes ~0.5 s, so this is fine for data generation.
    """

    def __init__(self, config: dict, project: str = "mlfock_oracle", workdir: str | None = None,
                 silent: int = 1):
        self.config = copy.deepcopy(config)
        self.project = project
        self.workdir = Path(workdir or ".")
        self.silent = silent
        self.shells = None

    def __call__(self, Z, pos_bohr, tag: str = "") -> FockRecord:
        from oqp.pyoqp import Runner  # noqa: PLC0415
        from oqp.library.single_point import SinglePoint  # noqa: PLC0415
        cfg = copy.deepcopy(self.config)
        cfg["input"]["system"] = _geometry_text(Z, pos_bohr)
        runner = Runner(project=self.project, input_dict=_stringify(cfg),
                        log=str(self.workdir / f"{self.project}.log"), silent=self.silent,
                        usempi=False)
        mol = runner.mol
        SinglePoint(mol).reference()
        rec = record_from_openqp(mol, tag=tag, shells=self.shells)
        self.shells = rec.shells
        rec.coords_bohr = np.asarray(pos_bohr, float).reshape(-1, 3)
        return rec


def run_reference(Z, pos_bohr, **kw) -> FockRecord:
    return OpenQPOracle(rohf_config(**kw))(Z, pos_bohr)


def run_mrsf_tddftb_with_reference(Z, pos_bohr, reference_bin, nstate: int = 3,
                                   dftb_options: dict | None = None, project: str = "mlfock_tb",
                                   workdir: str | None = None):
    """MRSF-TDDFTB state energies with an external reference file.

    Needs the openqp-dftb native library (OPENQP_DFTB_LIBRARY) and a DFTB
    parameter set; ``dftb_options`` is merged into the [dftb] section
    (e.g. {"parameter_path": ..., "response_cam_alpha": 0.5}).
    """
    from oqp.pyoqp import Runner  # noqa: PLC0415
    from oqp.utils.tb_backends import make_tb_adapter  # noqa: PLC0415
    cfg = {"input": {"system": _geometry_text(Z, pos_bohr), "charge": 0, "method": "dftb",
                     "runtype": "energy"},
           "dftb": {"type": "mrsf", **(dftb_options or {})},
           "tdhf": {"nstate": nstate}}
    old = os.environ.get("OPENQP_DFTB_SIMPLE_MRSF_REF")
    os.environ["OPENQP_DFTB_SIMPLE_MRSF_REF"] = str(reference_bin)
    try:
        runner = Runner(project=project, input_dict=_stringify(cfg),
                        log=str(Path(workdir or ".") / f"{project}.log"), silent=1, usempi=False)
        energies = make_tb_adapter(runner.mol).energy()
    finally:
        if old is None:
            os.environ.pop("OPENQP_DFTB_SIMPLE_MRSF_REF", None)
        else:
            os.environ["OPENQP_DFTB_SIMPLE_MRSF_REF"] = old
    return np.asarray(energies, float)


def dump_records(records: list[FockRecord], out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for k, rec in enumerate(records):
        rec.save(out / f"{rec.tag or 'geom'}_{k:06d}.npz")
