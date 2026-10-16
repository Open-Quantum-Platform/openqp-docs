"""Assemble F = Hcore + ΔF_ML, diagonalise, write the MRSF-TDDFTB reference."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import scipy.linalg
import torch

from .basis import BasisLayout
from .extract import write_simple_mrsf_reference


@dataclass
class Orbitals:
    F_eff: np.ndarray
    F_alpha: np.ndarray
    F_beta: np.ndarray
    S: np.ndarray
    C: np.ndarray            # S-orthonormal canonical MOs, one per column
    eps: np.ndarray
    uncertainty: float       # ensemble spread of ΔF (Hartree); 0 for a single model
    residual: float | None   # true SCF residual if a fock_builder was supplied

    def write_reference(self, path, layout: BasisLayout, n_alpha: int, n_beta: int):
        write_simple_mrsf_reference(path, self.S, self.C, self.eps, self.F_alpha, self.F_beta,
                                    layout, n_alpha, n_beta)


class FockPredictor:
    """One model or an ensemble.  ``fock_builder(P_alpha, P_beta) -> (F_alpha, F_beta)``
    optionally supplies a true Fock build for a self-consistency residual."""

    def __init__(self, models, fock_builder=None, device="cpu"):
        self.models = list(models) if isinstance(models, (list, tuple)) else [models]
        for m in self.models:
            m.eval().to(device)
        self.device = device
        self.fock_builder = fock_builder
        self.shells = self.models[0].shells

    @torch.no_grad()
    def delta(self, Z, pos_bohr):
        Zt = torch.as_tensor(np.asarray(Z, int), dtype=torch.long, device=self.device)
        pt = torch.as_tensor(np.asarray(pos_bohr, float), dtype=torch.get_default_dtype(),
                             device=self.device)
        preds = np.stack([m(Zt, pt).cpu().numpy() for m in self.models])
        return preds.mean(0), (float(preds.std(0).max()) if len(self.models) > 1 else 0.0)

    def predict(self, Z, pos_bohr, S, Hcore, n_alpha: int, n_beta: int) -> Orbitals:
        dF, spread = self.delta(Z, pos_bohr)
        F = dF + np.asarray(Hcore)[None]
        F = 0.5 * (F + F.transpose(0, 2, 1))
        eps, C = scipy.linalg.eigh(F[0], S)
        residual = None
        if self.fock_builder is not None:
            Pa = C[:, :n_alpha] @ C[:, :n_alpha].T
            Pb = C[:, :n_beta] @ C[:, :n_beta].T
            Fa, Fb = self.fock_builder(Pa, Pb)
            residual = max(commutator_residual(Fa, Pa, S), commutator_residual(Fb, Pb, S))
        return Orbitals(F[0], F[1], F[2], np.asarray(S), C, eps, spread, residual)


def commutator_residual(F, P, S) -> float:
    """max |FPS - SPF|, the DIIS error; zero at self-consistency."""
    E = F @ P @ S - S @ P @ F
    return float(np.abs(E).max())


def orbital_overlap_fidelity(C_ml, C_ref, S, n_occ: int) -> float:
    """Mean singular value of C_ref^T S C_ml over the first n_occ orbitals (1 = identical span)."""
    M = C_ref[:, :n_occ].T @ S @ C_ml[:, :n_occ]
    return float(np.linalg.svd(M, compute_uv=False).mean())


def subspace_fidelities(C_ml, C_ref, S, n_alpha, n_beta) -> dict:
    """Fidelity of the closed, SOMO and virtual spaces separately (MRSF needs all three)."""
    def fid(a, b):
        M = C_ref[:, a:b].T @ S @ C_ml[:, a:b]
        return float(np.linalg.svd(M, compute_uv=False).mean()) if b > a else 1.0
    n = C_ml.shape[1]
    return {"closed": fid(0, n_beta), "somo": fid(n_beta, n_alpha), "virtual": fid(n_alpha, n)}
