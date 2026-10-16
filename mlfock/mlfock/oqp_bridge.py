"""Glue between mlfock and OpenQP / openqp-dftb.

Nothing here is imported by the core package, so mlfock trains and predicts
without an OpenQP installation.  Three services:

* ``OpenQPOracle``        : geometry -> converged ROKS/ROHF FockRecord
                            (Gaussian basis), the on-the-fly oracle.
* ``DFTBBase``            : geometry -> (H_tb, S_tb) from the openqp-dftb
                            adapter, the delta-learning base.
* ``run_mrsf_with_orbitals`` : push ML orbitals into an OpenQP molecule,
                            optionally polish with a few SCF iterations,
                            then run the MRSF response on them.

Feeding orbitals to the *native* MRSF-TDDFTB response is not possible from
Python yet: the openqp-dftb C ABI only takes a warm-start MO file as an SCC
guess (``OPENQP_DFTB_WARMSTART_MO``) and re-converges.  ``write_dftb_orbitals``
writes the ML orbitals in a plain binary layout so a "fixed reference
orbitals" entry point on the native side can consume them; see README.
"""

from __future__ import annotations

import copy
from pathlib import Path
import numpy as np

from .extract import (FockRecord, fock_from_openqp, hamiltonian_from_dftb_result,
                      record_from_openqp, _coerce_mo_columns)


def _runner(config: dict, project: str = "mlfock", log: str | None = None):
    from oqp.pyoqp import Runner  # noqa: PLC0415
    return Runner(project=project, input_dict=copy.deepcopy(config),
                  log=log or f"{project}.log", silent=1, usempi=False)


class OpenQPOracle:
    """Run the reference open-shell SCF in OpenQP for a geometry.

    ``config`` is an OpenQP input dict (same schema as the .inp file) with
    ``scf_type=rohf`` (or ``uhf``), the functional and basis of the target
    MRSF-TDDFT level, and ``method=hf``.  One Runner is kept and its
    coordinates are updated per call.
    """

    def __init__(self, config: dict, project: str = "mlfock_oracle", polish_from_previous=True):
        self.runner = _runner(config, project)
        self.mol = self.runner.mol
        self.polish_from_previous = polish_from_previous
        self._first = True

    def __call__(self, Z, pos_bohr) -> FockRecord:
        from oqp.library.single_point import SinglePoint  # noqa: PLC0415
        pos = np.asarray(pos_bohr, dtype=float).reshape(-1, 3)
        self.mol.update_system(pos.ravel())
        sp = SinglePoint(self.mol)
        # after the first geometry, reuse the previous orbitals as the guess
        do_init = self._first or not self.polish_from_previous
        sp.reference(do_init_scf=do_init)
        self._first = False
        rec = record_from_openqp(self.mol)
        rec.coords_bohr = pos
        return rec


class DFTBBase:
    """DFTB reference Hamiltonian/overlap for a geometry via openqp-dftb."""

    def __init__(self, config: dict, project: str = "mlfock_dftb"):
        if "dftb" not in config:
            raise ValueError("config needs a [dftb] section (method=dftb, type=mrsf ...)")
        self.runner = _runner(config, project)
        self.mol = self.runner.mol

    def __call__(self, Z, pos_bohr):
        from oqp.utils.tb_backends import make_tb_adapter  # noqa: PLC0415
        self.mol.update_system(np.asarray(pos_bohr, dtype=float).ravel())
        adapter = make_tb_adapter(self.mol)
        adapter.energy()
        result = adapter._last_result if hasattr(adapter, "_last_result") else None
        if result is None or getattr(result, "mo_coefficients", None) is None:
            # fall back to the tags the adapter publishes on the molecule
            C = np.asarray(self.mol.data["OQP::VEC_MO_A"], dtype=float)
            eps = np.asarray(self.mol.data["OQP::E_MO_A"], dtype=float).ravel()
            n = eps.size
            C = C.reshape(n, n, order="F")
            from .extract import overlap_from_complete_orbitals, fock_from_orbitals
            S = overlap_from_complete_orbitals(C)
            return fock_from_orbitals(C, eps, S), S
        return hamiltonian_from_dftb_result(result)


# ------------------------------------------------------------ inject into OpenQP
def inject_orbitals(mol, C: np.ndarray, eps: np.ndarray, n_alpha: int, n_beta: int):
    """Overwrite OpenQP's MO/density tags with ML orbitals (Gaussian basis).

    The memory layout of ``OQP::VEC_MO_A`` is detected from the existing
    tag so the written array matches what the Fortran side expects.
    """
    n = eps.size
    existing = np.asarray(mol.data["OQP::VEC_MO_A"], dtype=float)
    S = _overlap(mol, n)
    probe = _coerce_mo_columns(existing, S, n)
    # find the (order, transpose) that reproduces `existing` from `probe`
    flat_existing = existing.ravel()
    layout = None
    for order in ("F", "C"):
        for transpose in (False, True):
            M = probe.T if transpose else probe
            if np.allclose(M.ravel(order=order), flat_existing[: n * n]):
                layout = (order, transpose)
    if layout is None:
        raise RuntimeError("cannot determine OQP::VEC_MO_A memory layout")
    order, transpose = layout
    M = C.T if transpose else C
    new = M.ravel(order=order).reshape(existing.shape)
    for tag in ("OQP::VEC_MO_A", "OQP::VEC_MO_B"):
        arr = mol.data[tag]
        np.asarray(arr)[...] = new.reshape(np.asarray(arr).shape)
    for tag in ("OQP::E_MO_A", "OQP::E_MO_B"):
        np.asarray(mol.data[tag])[...] = eps.reshape(np.asarray(mol.data[tag]).shape)
    from .predict import density_matrix
    Pa = C[:, :n_alpha] @ C[:, :n_alpha].T
    Pb = C[:, :n_beta] @ C[:, :n_beta].T
    for tag, P in (("OQP::DM_A", Pa), ("OQP::DM_B", Pb)):
        if tag in mol.data:
            arr = np.asarray(mol.data[tag])
            arr[...] = _pack_like(P, arr)


def run_mrsf_with_orbitals(mol, C, eps, n_alpha, n_beta, polish_iterations: int = 0):
    """ML orbitals -> (optional SCF polish) -> MRSF response.  Returns state energies.

    Mirrors ``SinglePoint.reference`` without the guess step.  With
    ``polish_iterations=0`` the SCF driver is asked for a single pass
    (maxit=1) and the response runs on the ML orbitals; with N>0 the SCF
    may take up to N steps, which converges any residual error away.
    """
    from oqp.library.single_point import SinglePoint  # noqa: PLC0415
    sp = SinglePoint(mol)
    sp._prep_guess()                       # basis, 1e integrals, placeholder guess
    inject_orbitals(mol, C, eps, n_alpha, n_beta)
    old_maxit = mol.config["scf"]["maxit"]
    mol.config["scf"]["maxit"] = max(1, int(polish_iterations))
    try:
        mol.data.set_scf_maxit(mol.config["scf"]["maxit"]) if hasattr(mol.data, "set_scf_maxit") else None
        sp._run_scf()
    finally:
        mol.config["scf"]["maxit"] = old_maxit
    ref = [mol.mol_energy.energy]
    mol.energies = ref
    return sp.excitation(ref)


def write_dftb_orbitals(path, C: np.ndarray, eps: np.ndarray, n_alpha: int, n_beta: int):
    """Plain little-endian binary: int64 nbf, noca, nocb; float64 eps[nbf];
    float64 C[nbf*nbf] column-major (one MO per column).  Intended for a
    native "fixed reference orbitals" entry in openqp-dftb."""
    n = eps.size
    with open(path, "wb") as fh:
        np.array([n, n_alpha, n_beta], dtype="<i8").tofile(fh)
        np.asarray(eps, dtype="<f8").tofile(fh)
        np.asarray(C, dtype="<f8").ravel(order="F").tofile(fh)


# ----------------------------------------------------------------- utilities
def _overlap(mol, n):
    from .extract import _square_overlap
    return _square_overlap(mol, n)


def _pack_like(M: np.ndarray, template: np.ndarray) -> np.ndarray:
    n = M.shape[0]
    if template.size == n * n:
        return M.reshape(template.shape)
    if template.size == n * (n + 1) // 2:
        return M[np.tril_indices(n)].reshape(template.shape)
    raise ValueError(f"cannot pack ({n},{n}) into template of size {template.size}")


def dump_records(records: list[FockRecord], out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for k, rec in enumerate(records):
        rec.save(out / f"{rec.tag or 'geom'}_{k:06d}.npz")
