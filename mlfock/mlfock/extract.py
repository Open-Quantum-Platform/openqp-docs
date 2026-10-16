"""Converged OpenQP data -> training records; reference-file writer for openqp-dftb.

Record contents (all in the Gaussian AO basis OpenQP uses, Cartesian layout):

* ``F_ref``  : (3, nao, nao)  [F_eff, F_alpha, F_beta]
    - F_eff   = S C diag(eps) C^T S, the ROKS effective Fock whose generalized
                eigenvectors are the canonical orbitals (OQP::VEC_MO_A/E_MO_A)
    - F_alpha, F_beta = OQP::FOCK_A / OQP::FOCK_B, what the MRSF-TDDFTB
                response consumes as hamiltonian_alpha/beta
* ``F_base`` : (nao, nao) Hcore (OQP::Hcore).  ΔF = F_ref - Hcore is the
               two-electron part, which is what the model learns.
* ``S``      : overlap (OQP::SM)

The openqp-dftb "simple-MRSF" loader (OPENQP_DFTB_SIMPLE_MRSF_REF) takes
exactly S, C, eps, occupations, AO->atom/l maps and F_alpha/F_beta, so a
predicted record turns into an MRSF-TDDFTB reference with no projection.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .basis import BasisLayout, shells_from_openqp

CHANNELS = ("F_eff", "F_alpha", "F_beta")


# --------------------------------------------------------------------- generic
def fock_from_orbitals(C: np.ndarray, eps: np.ndarray, S: np.ndarray) -> np.ndarray:
    """AO Fock matrix from S-orthonormal MO coefficients (columns) and energies."""
    SC = np.asarray(S, float) @ np.asarray(C, float)
    F = SC @ (np.asarray(eps, float)[:, None] * SC.T)
    return 0.5 * (F + F.T)


def overlap_from_complete_orbitals(C: np.ndarray) -> np.ndarray:
    """S = (C C^T)^-1 for a complete S-orthonormal MO set (square C)."""
    C = np.asarray(C, float)
    if C.shape[0] != C.shape[1]:
        raise ValueError("overlap recovery needs a complete (square) MO set")
    S = np.linalg.inv(C @ C.T)
    return 0.5 * (S + S.T)


def unpack_triangular(packed, n: int) -> np.ndarray:
    """Lower-triangular row-major packed storage -> full symmetric matrix."""
    M = np.zeros((n, n))
    idx = np.tril_indices(n)
    M[idx] = np.asarray(packed, float).ravel()[: idx[0].size]
    return M + np.tril(M, -1).T


# --------------------------------------------------------------------- records
@dataclass
class FockRecord:
    atomic_numbers: np.ndarray       # (natom,)
    coords_bohr: np.ndarray          # (natom, 3)
    F_ref: np.ndarray                # (C, nao, nao)
    S: np.ndarray                    # (nao, nao)
    F_base: np.ndarray | None        # (nao, nao) or None
    n_occ_alpha: int
    n_occ_beta: int
    shells: dict                     # {Z: [(l, kind), ...]}
    tag: str = ""
    eps: np.ndarray | None = None    # reference orbital energies (diagnostics)

    def delta(self) -> np.ndarray:
        if self.F_base is None:
            return self.F_ref
        return self.F_ref - self.F_base[None]

    def layout(self) -> BasisLayout:
        return BasisLayout(self.atomic_numbers, shells=self.shells)

    def save(self, path):
        import json
        np.savez_compressed(
            path, atomic_numbers=self.atomic_numbers, coords_bohr=self.coords_bohr,
            F_ref=self.F_ref, S=self.S,
            F_base=np.zeros(0) if self.F_base is None else self.F_base,
            n_occ_alpha=self.n_occ_alpha, n_occ_beta=self.n_occ_beta,
            shells=json.dumps({int(z): list(v) for z, v in self.shells.items()}), tag=self.tag,
            eps=np.zeros(0) if self.eps is None else self.eps)

    @classmethod
    def load(cls, path) -> "FockRecord":
        import json
        d = np.load(path, allow_pickle=False)
        F_base = d["F_base"]
        eps = d["eps"]
        shells = {int(z): [tuple(x) for x in v] for z, v in json.loads(str(d["shells"])).items()}
        return cls(d["atomic_numbers"], d["coords_bohr"], d["F_ref"], d["S"],
                   None if F_base.size == 0 else F_base, int(d["n_occ_alpha"]),
                   int(d["n_occ_beta"]), shells, str(d["tag"]), None if eps.size == 0 else eps)


# ---------------------------------------------------------------------- OpenQP
def mo_columns(mol, S: np.ndarray | None = None) -> np.ndarray:
    """OQP::VEC_MO_A as (nao, nmo) with one MO per column.

    OpenQP stores the array MO-major (shape (nmo, nao)); the layout is
    verified against the overlap rather than assumed.
    """
    C = np.asarray(mol.data["OQP::VEC_MO_A"], float)
    n = C.shape[0]
    S = square_overlap(mol, n) if S is None else S
    for M in (C.T, C):
        if np.abs(M.T @ S @ M - np.eye(n)).max() < 1e-5:
            return M.copy()
    raise ValueError("OQP::VEC_MO_A is not S-orthonormal in either layout")


def square_overlap(mol, n: int) -> np.ndarray:
    return unpack_triangular(mol.data["OQP::SM"], n)


def record_from_openqp(mol, tag: str = "", shells: dict | None = None) -> FockRecord:
    """Build a record from a converged ROHF/ROKS OpenQP molecule."""
    d = mol.data
    eps = np.asarray(d["OQP::E_MO_A"], float).ravel()
    n = eps.size
    S = square_overlap(mol, n)
    C = mo_columns(mol, S)
    F_eff = fock_from_orbitals(C, eps, S)
    Fa = unpack_triangular(d["OQP::FOCK_A"], n)
    Fb = unpack_triangular(d["OQP::FOCK_B"], n)
    H = unpack_triangular(d["OQP::Hcore"], n)
    Z = np.asarray(mol.get_atoms(), int).ravel()
    pos = np.asarray(mol.get_system(), float).reshape(-1, 3)
    na = int(np.asarray(d["nelec_A"]).ravel()[0])
    nb = int(np.asarray(d["nelec_B"]).ravel()[0])
    shells = shells or shells_from_openqp(mol)
    rec = FockRecord(Z, pos, np.stack([F_eff, Fa, Fb]), S, H, na, nb, shells, tag, eps)
    if rec.layout().nao != n:
        raise ValueError("shell table does not reproduce OpenQP's AO count")
    return rec


# ------------------------------------------------------------------ openqp-dftb
def hamiltonian_from_dftb_result(result) -> tuple[np.ndarray, np.ndarray]:
    """(H_tb, S_tb) from an openqp-dftb adapter result (complete MO set)."""
    C = np.asarray(result.mo_coefficients, float)
    eps = np.asarray(result.mo_energies, float).ravel()
    S = overlap_from_complete_orbitals(C)
    return fock_from_orbitals(C, eps, S), S


def write_simple_mrsf_reference(path, S, C, eps, Fa, Fb, layout: BasisLayout,
                                n_alpha: int, n_beta: int):
    """Write the binary that openqp-dftb reads from OPENQP_DFTB_SIMPLE_MRSF_REF.

    Format (little-endian stream, Fortran column-major matrices), identical to
    openqp-dftb/tools/simple_mrsf/extract_ref.py: int64 nbf,nmo,natoms,nsites;
    S; C_alpha; C_beta; eps_alpha; eps_beta; occ_alpha; occ_beta;
    int64 ao_atom; ao_l; ao_spin_site; spin_site_atom; F_alpha; F_beta.
    alpha == beta == the ROKS canonical set (as DFTB MRSF fills them).
    """
    nbf = S.shape[0]
    nmo = C.shape[1]
    natoms = layout.natom
    occ_a = np.zeros(nmo); occ_a[:n_alpha] = 1.0
    occ_b = np.zeros(nmo); occ_b[:n_beta] = 1.0
    ao_atom = layout.ao_atom()
    with open(path, "wb") as fh:
        np.array([nbf, nmo, natoms, natoms], dtype="<i8").tofile(fh)
        for M in (S, C, C):
            np.asarray(M, "<f8").ravel(order="F").tofile(fh)
        for v in (eps, eps, occ_a, occ_b):
            np.asarray(v, "<f8").tofile(fh)
        ao_atom.astype("<i8").tofile(fh)
        layout.ao_l().astype("<i8").tofile(fh)
        ao_atom.astype("<i8").tofile(fh)
        np.arange(1, natoms + 1, dtype="<i8").tofile(fh)
        for M in (Fa, Fb):
            np.asarray(M, "<f8").ravel(order="F").tofile(fh)


def read_simple_mrsf_reference(path) -> dict:
    """Inverse of :func:`write_simple_mrsf_reference` (for tests)."""
    with open(path, "rb") as fh:
        nbf, nmo, natoms, nsites = np.fromfile(fh, "<i8", 4)
        mat = lambda r, c: np.fromfile(fh, "<f8", r * c).reshape((r, c), order="F")
        S, Ca, Cb = mat(nbf, nbf), mat(nbf, nmo), mat(nbf, nmo)
        ea, eb, oa, ob = (np.fromfile(fh, "<f8", nmo) for _ in range(4))
        ao_atom, ao_l, ao_site = (np.fromfile(fh, "<i8", nbf) for _ in range(3))
        site_atom = np.fromfile(fh, "<i8", nsites)
        Fa, Fb = mat(nbf, nbf), mat(nbf, nbf)
    return dict(S=S, Ca=Ca, Cb=Cb, eps_a=ea, eps_b=eb, occ_a=oa, occ_b=ob, ao_atom=ao_atom,
                ao_l=ao_l, ao_site=ao_site, site_atom=site_atom, Fa=Fa, Fb=Fb)
