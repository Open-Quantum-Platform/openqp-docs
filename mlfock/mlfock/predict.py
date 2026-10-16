"""Assemble F = F_base + ΔF_ML, diagonalise, and estimate uncertainty."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import scipy.linalg
import torch

from .basis import BasisLayout
from .model import DeltaFockModel


@dataclass
class Orbitals:
    F: np.ndarray            # AO Fock matrix used
    S: np.ndarray
    C: np.ndarray            # S-orthonormal MO coefficients, one MO per column
    eps: np.ndarray
    uncertainty: float       # ensemble spread of ΔF (Hartree), 0 if single model
    residual: float | None   # ||FPS - SPF|| if a Fock builder was supplied


class FockPredictor:
    """Wraps one model or an ensemble.

    Parameters
    ----------
    models : list of DeltaFockModel (an ensemble gives an uncertainty estimate)
    fock_builder : optional callable ``(density_matrix) -> F`` from the
        reference method (one DFT Fock build).  When given, ``predict`` also
        returns the true self-consistency residual.  This costs one SCF
        iteration, so use it only for the on-the-fly oracle gate.
    """

    def __init__(self, models, fock_builder=None, device="cpu"):
        self.models = list(models) if isinstance(models, (list, tuple)) else [models]
        for m in self.models:
            m.eval().to(device)
        self.device = device
        self.fock_builder = fock_builder
        self.layout_kwargs = self.models[0].layout_kwargs

    @torch.no_grad()
    def delta(self, Z: np.ndarray, pos_bohr: np.ndarray) -> tuple[np.ndarray, float]:
        Zt = torch.as_tensor(np.asarray(Z, dtype=int), dtype=torch.long, device=self.device)
        pt = torch.as_tensor(np.asarray(pos_bohr, dtype=float), dtype=torch.get_default_dtype(),
                             device=self.device)
        preds = np.stack([m(Zt, pt).cpu().numpy() for m in self.models])
        mean = preds.mean(0)
        spread = float(preds.std(0).max()) if len(self.models) > 1 else 0.0
        return mean, spread

    def predict(self, Z, pos_bohr, S, F_base=None, n_occ_alpha=None, n_occ_beta=None
                ) -> Orbitals:
        dF, spread = self.delta(Z, pos_bohr)
        F = dF if F_base is None else np.asarray(F_base) + dF
        F = 0.5 * (F + F.T)
        eps, C = scipy.linalg.eigh(F, S)
        residual = None
        if self.fock_builder is not None and n_occ_alpha is not None:
            nb = n_occ_alpha if n_occ_beta is None else n_occ_beta
            P = density_matrix(C, n_occ_alpha, nb)
            F_true = self.fock_builder(P)
            residual = commutator_residual(F_true, P, S)
        return Orbitals(F, S, C, eps, spread, residual)


def density_matrix(C: np.ndarray, n_alpha: int, n_beta: int) -> np.ndarray:
    """Total (alpha + beta) density from the lowest orbitals."""
    Ca = C[:, :n_alpha]
    Cb = C[:, :n_beta]
    return Ca @ Ca.T + Cb @ Cb.T


def commutator_residual(F: np.ndarray, P: np.ndarray, S: np.ndarray) -> float:
    """max |FPS - SPF|: zero at self-consistency, the DIIS error measure."""
    E = F @ P @ S - S @ P @ F
    return float(np.abs(E).max())


def orbital_overlap_fidelity(C_ml: np.ndarray, C_ref: np.ndarray, S: np.ndarray,
                             n_occ: int) -> float:
    """Occupied-space fidelity: mean singular value of C_ref^T S C_ml over occ."""
    M = C_ref[:, :n_occ].T @ S @ C_ml[:, :n_occ]
    return float(np.linalg.svd(M, compute_uv=False).mean())
