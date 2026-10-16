"""Turn converged orbitals into AO Fock matrices, and project between bases.

The Fock matrix is reconstructed from canonical orbitals, which is exact at
convergence and needs nothing beyond what both OpenQP and openqp-dftb
already export::

    F = S C diag(eps) C^T S            (C orthonormal under S: C^T S C = 1)

For a ROKS/ROHF reference, OpenQP stores the effective (Guest-Saunders /
Roothaan) Fock eigenpairs in ``OQP::VEC_MO_A`` / ``OQP::E_MO_A``; that
effective operator is exactly what a downstream MRSF response needs, so it
is the learning target.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


# --------------------------------------------------------------------- generic
def fock_from_orbitals(C: np.ndarray, eps: np.ndarray, S: np.ndarray) -> np.ndarray:
    """AO Fock matrix from S-orthonormal MO coefficients (columns) and energies."""
    C = np.asarray(C, dtype=float)
    S = np.asarray(S, dtype=float)
    SC = S @ C
    F = SC @ (np.asarray(eps, dtype=float)[:, None] * SC.T)
    return 0.5 * (F + F.T)


def overlap_from_complete_orbitals(C: np.ndarray) -> np.ndarray:
    """S = (C C^T)^-1 when C is a complete S-orthonormal set (square)."""
    C = np.asarray(C, dtype=float)
    if C.shape[0] != C.shape[1]:
        raise ValueError("overlap recovery needs a complete (square) MO set")
    S = np.linalg.inv(C @ C.T)
    return 0.5 * (S + S.T)


def unpack_triangular(packed: np.ndarray, n: int) -> np.ndarray:
    """Lower-triangular row-major packed storage -> full symmetric matrix."""
    packed = np.asarray(packed, dtype=float).ravel()
    M = np.zeros((n, n))
    idx = np.tril_indices(n)
    M[idx] = packed[: idx[0].size]
    return M + np.tril(M, -1).T


# -------------------------------------------------------------------- records
@dataclass
class FockRecord:
    """One training geometry.  Matrices are square numpy arrays."""

    atomic_numbers: np.ndarray       # (natom,)
    coords_bohr: np.ndarray          # (natom, 3)
    F_ref: np.ndarray                # target Fock matrix in the model basis
    S: np.ndarray                    # overlap in the model basis
    F_base: np.ndarray | None = None # e.g. DFTB Hamiltonian (delta learning)
    n_occ_alpha: int = 0
    n_occ_beta: int = 0
    tag: str = ""

    def delta(self) -> np.ndarray:
        return self.F_ref if self.F_base is None else self.F_ref - self.F_base

    def save(self, path):
        np.savez_compressed(
            path, atomic_numbers=self.atomic_numbers, coords_bohr=self.coords_bohr,
            F_ref=self.F_ref, S=self.S,
            F_base=np.zeros(0) if self.F_base is None else self.F_base,
            n_occ_alpha=self.n_occ_alpha, n_occ_beta=self.n_occ_beta, tag=self.tag)

    @classmethod
    def load(cls, path) -> "FockRecord":
        d = np.load(path, allow_pickle=False)
        F_base = d["F_base"]
        return cls(
            atomic_numbers=d["atomic_numbers"], coords_bohr=d["coords_bohr"],
            F_ref=d["F_ref"], S=d["S"], F_base=None if F_base.size == 0 else F_base,
            n_occ_alpha=int(d["n_occ_alpha"]), n_occ_beta=int(d["n_occ_beta"]),
            tag=str(d["tag"]))


# -------------------------------------------------------------------- OpenQP
def fock_from_openqp(mol) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(F, S, C, eps) in the Gaussian AO basis from a converged OpenQP molecule.

    Reads ``OQP::VEC_MO_A``, ``OQP::E_MO_A`` and ``OQP::SM``.  Works after
    ``SinglePoint(mol).energy()`` or any run that leaves converged MOs.
    """
    data = mol.data
    eps = np.asarray(data["OQP::E_MO_A"], dtype=float).ravel()
    n = eps.size
    C = np.asarray(data["OQP::VEC_MO_A"], dtype=float)
    # OpenQP keeps MO coefficients Fortran-style: reshape to (nao, nmo) with
    # one MO per column.  Validate against the overlap instead of trusting
    # the reshape order.
    S = _square_overlap(mol, n)
    C = _coerce_mo_columns(C, S, n)
    F = fock_from_orbitals(C, eps, S)
    return F, S, C, eps


def _square_overlap(mol, n: int) -> np.ndarray:
    getter = getattr(mol, "get_overlap", None)
    if callable(getter):
        S = getter()
        if S is not None:
            S = np.asarray(S, dtype=float)
            if S.shape == (n, n):
                return S
    return unpack_triangular(mol.data["OQP::SM"], n)


def _coerce_mo_columns(C: np.ndarray, S: np.ndarray, n: int) -> np.ndarray:
    """Return C with MOs as columns, picking the memory order that is S-orthonormal."""
    flat = np.asarray(C, dtype=float).ravel()
    best, best_err = None, np.inf
    for order in ("F", "C"):
        for transpose in (False, True):
            M = flat[: n * n].reshape((n, n), order=order)
            if transpose:
                M = M.T
            err = np.abs(M.T @ S @ M - np.eye(n)).max()
            if err < best_err:
                best, best_err = M, err
    if best_err > 1e-4:
        raise ValueError(f"could not identify an S-orthonormal MO layout (err={best_err:.2e})")
    return best


def record_from_openqp(mol, tag: str = "") -> FockRecord:
    """Gaussian-basis record (no projection, no base).  Use ``project_record``
    to move it into the DFTB basis and attach a DFTB base Hamiltonian."""
    F, S, _, _ = fock_from_openqp(mol)
    coords = np.asarray(mol.get_system(), dtype=float).reshape(-1, 3)
    Z = np.asarray(mol.get_atoms(), dtype=int).ravel()
    nocc_a = int(mol.data.get("nelec_A", 0) or 0)
    nocc_b = int(mol.data.get("nelec_B", 0) or 0)
    return FockRecord(Z, coords, F, S, None, nocc_a, nocc_b, tag)


# ------------------------------------------------------------------- openqp-dftb
def hamiltonian_from_dftb_result(result) -> tuple[np.ndarray, np.ndarray]:
    """(H_tb, S_tb) from an openqp-dftb ``_StateResult`` / adapter export.

    ``result.mo_coefficients`` is (nbf, nbf) with one MO per column and
    ``result.mo_energies`` holds the converged reference eigenvalues
    (high-spin ROKS reference for sf/mrsf types).  The overlap follows from
    completeness, S = (C C^T)^-1, exactly as the adapter's symmetry labeler
    does.
    """
    C = np.asarray(result.mo_coefficients, dtype=float)
    eps = np.asarray(result.mo_energies, dtype=float).ravel()
    S = overlap_from_complete_orbitals(C)
    H = fock_from_orbitals(C, eps, S)
    return H, S


# ---------------------------------------------------------------- projection
def project_fock(F_big: np.ndarray, S_big: np.ndarray, S_cross: np.ndarray
                 ) -> tuple[np.ndarray, np.ndarray]:
    """Project a Fock matrix from a large basis onto a small basis.

    ``S_cross[mu, a] = <chi_mu^big | phi_a^small>``.  Each small function is
    least-squares expanded in the big basis, T = S_big^-1 S_cross, giving

        F_small = T^T F_big T,     S_small = T^T S_big T

    With the DFTB minimal basis as the small basis this is the delta-learning
    target basis.  ``S_cross`` must come from the integral code that knows
    both basis sets (OpenQP can evaluate Gaussian-Gaussian overlaps; for the
    numerical SK orbitals fit each to a few Gaussians first).
    """
    T = np.linalg.solve(S_big, S_cross)
    F_small = T.T @ F_big @ T
    S_small = T.T @ S_big @ T
    return 0.5 * (F_small + F_small.T), 0.5 * (S_small + S_small.T)


def project_record(rec: FockRecord, S_cross: np.ndarray, F_base: np.ndarray | None = None,
                   S_base: np.ndarray | None = None) -> FockRecord:
    """Project a Gaussian-basis record into the DFTB basis and attach a base.

    If ``S_base`` (the DFTB overlap) is given, the projected overlap is
    replaced by it so the whole record lives in the true DFTB metric; the
    projected Fock matrix is then re-expressed in that metric through a
    symmetric transformation that maps the projected overlap onto S_base.
    """
    F_small, S_small = project_fock(rec.F_ref, rec.S, S_cross)
    if S_base is not None:
        # X maps S_small-orthonormal vectors to S_base-orthonormal vectors.
        X = _lowdin_half(S_base) @ np.linalg.inv(_lowdin_half(S_small))
        # F transforms covariantly: F' = X^-T F X^-1.
        Xi = np.linalg.inv(X)
        F_small = Xi.T @ F_small @ Xi
        F_small = 0.5 * (F_small + F_small.T)
        S_small = S_base
    return FockRecord(rec.atomic_numbers, rec.coords_bohr, F_small, S_small, F_base,
                      rec.n_occ_alpha, rec.n_occ_beta, rec.tag)


def _lowdin_half(S: np.ndarray) -> np.ndarray:
    w, V = np.linalg.eigh(S)
    return (V * np.sqrt(np.clip(w, 1e-12, None))) @ V.T
