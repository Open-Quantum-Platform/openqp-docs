"""Geometry -> pair local frames and rotation-invariant pair features (torch).

Equivariance strategy (DeepH-style local frames, no e3nn dependency):

* every atom pair (i, j), i <= j, gets an orthonormal frame R_ij whose
  z-axis is r_ij and whose x-axis comes from a smooth, cutoff-weighted sum
  of neighbour directions.  Onsite blocks (i == j) use the neighbour sum
  for z and a second, differently weighted sum for x.
* all inputs to the network are expressed in that frame, so they are
  invariant under global rotations and the network can be a plain MLP.
* the predicted block is rotated back with the AO rotation matrices
  D_i(R_ij) built in :mod:`mlfock.basis`.

When the environment is axially symmetric the x-axis is undefined; the
true block is then invariant under rotation about z, so the arbitrary
fallback choice does not matter for a correctly trained model.
"""

from __future__ import annotations

import math
import torch


def smooth_cutoff(r: torch.Tensor, rc: float) -> torch.Tensor:
    """Cosine cutoff, 1 at r=0, 0 at r>=rc, C1-continuous."""
    x = torch.clamp(r / rc, max=1.0)
    return 0.5 * (torch.cos(math.pi * x) + 1.0) * (r < rc)


def gaussian_rbf(r: torch.Tensor, n: int, rc: float, gamma: float | None = None) -> torch.Tensor:
    centers = torch.linspace(0.0, rc, n, device=r.device, dtype=r.dtype)
    gamma = gamma if gamma is not None else (n / rc) ** 2
    return torch.exp(-gamma * (r.unsqueeze(-1) - centers) ** 2)


def _safe_normalize(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return v / torch.sqrt((v * v).sum(-1, keepdim=True) + eps * eps)


def _perpendicular_fallback(z: torch.Tensor) -> torch.Tensor:
    """A unit vector perpendicular to z, chosen from the least-aligned axis."""
    idx = torch.argmin(z.abs(), dim=-1)
    e = torch.nn.functional.one_hot(idx, 3).to(z.dtype)
    x = e - (e * z).sum(-1, keepdim=True) * z
    return _safe_normalize(x)


def _orthonormal_frame(z: torch.Tensor, a: torch.Tensor, M: torch.Tensor | None = None,
                       tol: float = 1e-3, return_degenerate: bool = False):
    """Rows (x, y, z) from a z direction and an auxiliary vector a.

    If a has no component perpendicular to z (e.g. a symmetric environment),
    the x axis falls back to the principal axis of the perpendicular second
    moment M (covariant), and only then to a fixed global axis.
    """
    z = _safe_normalize(z)
    a_perp = a - (a * z).sum(-1, keepdim=True) * z
    norm = torch.sqrt((a_perp * a_perp).sum(-1, keepdim=True))
    x = a_perp / torch.clamp(norm, min=1e-12)
    fallback = _perpendicular_fallback(z)
    if M is not None:
        Pz = torch.eye(3, device=z.device, dtype=z.dtype) - z.unsqueeze(-1) * z.unsqueeze(-2)
        Mp = Pz @ M @ Pz
        w, V = torch.linalg.eigh(Mp)
        v = V[..., :, -1]                                   # principal perpendicular axis
        # fix the sign covariantly with the third moment along v (falls back to +v)
        v = v * torch.where((v * a).sum(-1, keepdim=True) < 0, -1.0, 1.0)
        v = _safe_normalize(v - (v * z).sum(-1, keepdim=True) * z)
        fallback = torch.where((w[..., -1] - w[..., -2]).unsqueeze(-1) > tol, v, fallback)
    degenerate = (norm.squeeze(-1) <= tol)
    if M is not None:
        degenerate = degenerate & ((w[..., -1] - w[..., -2]) <= tol)
    x = torch.where(norm > tol, x, fallback)
    y = torch.cross(z, x, dim=-1)
    frame = torch.stack([x, y, z], dim=-2)          # (..., 3, 3)
    return (frame, degenerate) if return_degenerate else frame


def build_pairs(pos: torch.Tensor, cutoff: float) -> tuple[torch.Tensor, torch.Tensor]:
    """Index tensors (i, j) of all pairs with i <= j and |r_ij| < cutoff."""
    n = pos.shape[0]
    d = torch.cdist(pos, pos)
    ii, jj = torch.triu_indices(n, n, offset=0, device=pos.device)
    keep = d[ii, jj] < cutoff
    return ii[keep], jj[keep]


def pair_frames(pos: torch.Tensor, ii: torch.Tensor, jj: torch.Tensor, rc: float,
                return_degenerate: bool = False):
    """(P, 3, 3) rotation matrices, rows = frame axes in global coordinates.

    With ``return_degenerate`` also returns a bool mask of pairs whose
    environment is axially symmetric about z (x axis arbitrary).  The true
    block is then invariant to the x choice, so predictions of a trained
    model are unaffected; only frame-covariance tests need the mask.
    """
    n = pos.shape[0]
    rij = pos[jj] - pos[ii]                                    # (P, 3)
    # neighbour sums around both atoms, excluding the pair itself
    rel_i = pos.unsqueeze(0) - pos[ii].unsqueeze(1)            # (P, N, 3)
    rel_j = pos.unsqueeze(0) - pos[jj].unsqueeze(1)
    di = rel_i.norm(dim=-1)
    dj = rel_j.norm(dim=-1)
    k = torch.arange(n, device=pos.device)
    excl = (k.unsqueeze(0) == ii.unsqueeze(1)) | (k.unsqueeze(0) == jj.unsqueeze(1))
    wi = smooth_cutoff(di, rc) * (~excl)
    wj = smooth_cutoff(dj, rc) * (~excl)
    ui = _safe_normalize(rel_i)
    uj = _safe_normalize(rel_j)
    a1 = (wi.unsqueeze(-1) * ui).sum(1) + (wj.unsqueeze(-1) * uj).sum(1)
    a2 = ((wi * di).unsqueeze(-1) * ui).sum(1) + ((wj * dj).unsqueeze(-1) * uj).sum(1)
    M = torch.einsum("pn,pna,pnb->pab", wi, ui, ui) + torch.einsum("pn,pna,pnb->pab", wj, uj, uj)

    onsite = ii == jj
    z = torch.where(onsite.unsqueeze(-1), a1, rij)
    # onsite: if a1 vanishes (centrosymmetric site) fall back to a2, else global z
    z_norm = z.norm(dim=-1, keepdim=True)
    z = torch.where(z_norm > 1e-3, z, torch.where(
        onsite.unsqueeze(-1), a2, z))
    z_norm = z.norm(dim=-1, keepdim=True)
    ez = torch.tensor([0.0, 0.0, 1.0], device=pos.device, dtype=pos.dtype).expand_as(z)
    z = torch.where(z_norm > 1e-3, z, ez)
    a = torch.where(onsite.unsqueeze(-1), a2, a1)
    return _orthonormal_frame(z, a, M, return_degenerate=return_degenerate)


class PairFeaturizer:
    """Build invariant per-pair and per-pair-neighbour feature tensors."""

    def __init__(self, cutoff: float = 10.0, env_cutoff: float = 8.0, n_rbf: int = 24):
        self.cutoff = cutoff
        self.env_cutoff = env_cutoff
        self.n_rbf = n_rbf

    @property
    def pair_dim(self) -> int:
        return self.n_rbf + 1

    @property
    def env_dim(self) -> int:
        # rbf(d_ik), rbf(d_jk), rbf(|c_k|), unit local coords (3), weight (1)
        return 3 * self.n_rbf + 4

    def __call__(self, Z: torch.Tensor, pos: torch.Tensor, ii=None, jj=None):
        if ii is None:
            ii, jj = build_pairs(pos, self.cutoff)
        R = pair_frames(pos, ii, jj, self.env_cutoff)           # (P,3,3)
        rij = (pos[jj] - pos[ii]).norm(dim=-1)
        onsite = (ii == jj).to(pos.dtype)
        pair_feat = torch.cat([gaussian_rbf(rij, self.n_rbf, self.cutoff),
                               onsite.unsqueeze(-1)], dim=-1)

        n = pos.shape[0]
        mid = 0.5 * (pos[ii] + pos[jj])                              # (P,3)
        rel = pos.unsqueeze(0) - mid.unsqueeze(1)                    # (P,N,3)
        local = torch.einsum("pab,pnb->pna", R, rel)                 # (P,N,3)
        di = (pos.unsqueeze(0) - pos[ii].unsqueeze(1)).norm(dim=-1)
        dj = (pos.unsqueeze(0) - pos[jj].unsqueeze(1)).norm(dim=-1)
        dc = local.norm(dim=-1)
        k = torch.arange(n, device=pos.device)
        excl = (k.unsqueeze(0) == ii.unsqueeze(1)) | (k.unsqueeze(0) == jj.unsqueeze(1))
        w = smooth_cutoff(torch.minimum(di, dj), self.env_cutoff) * (~excl)
        env_feat = torch.cat([
            gaussian_rbf(di, self.n_rbf, self.env_cutoff),
            gaussian_rbf(dj, self.n_rbf, self.env_cutoff),
            gaussian_rbf(dc, self.n_rbf, self.env_cutoff),
            _safe_normalize(local),
            w.unsqueeze(-1),
        ], dim=-1)                                                   # (P,N,env_dim)
        return {"ii": ii, "jj": jj, "R": R, "pair": pair_feat,
                "env": env_feat, "env_w": w, "Z": Z}
