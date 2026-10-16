"""Block-wise Fock (delta) model with local-frame equivariance."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from .basis import BasisLayout
from .features import PairFeaturizer, build_pairs

NMAX = 4  # s + p block size; padded for H atoms


def _mlp(dims, act=nn.SiLU):
    layers = []
    for a, b in zip(dims[:-1], dims[1:]):
        layers += [nn.Linear(a, b), act()]
    return nn.Sequential(*layers[:-1])


class DeltaFockModel(nn.Module):
    """Predict ΔF_ij blocks (NMAX x NMAX) for every pair i <= j.

    Parameters
    ----------
    max_z : largest atomic number in the element embedding table.
    layout_kwargs : forwarded to :class:`BasisLayout` (``p_order``, ``shells``).
    """

    def __init__(self, max_z: int = 20, emb_dim: int = 32, hidden: int = 128,
                 n_env_layers: int = 2, cutoff: float = 10.0, env_cutoff: float = 8.0,
                 n_rbf: int = 24, p_order: str = "yzx", shells: dict | None = None):
        super().__init__()
        self.featurizer = PairFeaturizer(cutoff, env_cutoff, n_rbf)
        self.layout_kwargs = {"p_order": p_order}
        if shells is not None:
            self.layout_kwargs["shells"] = shells
        self.emb = nn.Embedding(max_z + 1, emb_dim)
        fz = self.featurizer
        self.env_net = _mlp([fz.env_dim + 3 * emb_dim, hidden, hidden])
        self.env_post = _mlp([hidden, hidden])
        self.pair_net = _mlp([fz.pair_dim + 2 * emb_dim + hidden] + [hidden] * n_env_layers
                             + [NMAX * NMAX])
        # per-element-pair output scale/shift, learned on top of data normalisation
        self.register_buffer("out_scale", torch.ones(NMAX, NMAX))
        self.register_buffer("out_shift", torch.zeros(NMAX, NMAX))
        self.hparams = dict(max_z=max_z, emb_dim=emb_dim, hidden=hidden,
                            n_env_layers=n_env_layers, cutoff=cutoff, env_cutoff=env_cutoff,
                            n_rbf=n_rbf, p_order=p_order, shells=shells)

    # ------------------------------------------------------------------ core
    def predict_blocks(self, Z: torch.Tensor, pos: torch.Tensor):
        """Return (ii, jj, blocks_global) with blocks (P, NMAX, NMAX), i <= j.

        Every off-diagonal pair is evaluated in both orientations (i->j and
        j->i, each with its own local frame) and the two predictions are
        averaged as H_ij = (f(i,j) + f(j,i)^T)/2.  This makes the result
        exactly invariant to atom permutation, which a single orientation
        is not (the frame z-axis flips with the pair order).
        """
        ii0, jj0 = build_pairs(pos, self.featurizer.cutoff)
        off = ii0 != jj0
        ii = torch.cat([ii0, jj0[off]])
        jj = torch.cat([jj0, ii0[off]])
        blk = self._predict_oriented(Z, pos, ii, jj)
        n0 = ii0.shape[0]
        out = blk[:n0].clone()
        out[off] = 0.5 * (blk[:n0][off] + blk[n0:].transpose(1, 2))
        return ii0, jj0, out

    def _predict_oriented(self, Z, pos, ii, jj):
        f = self.featurizer(Z, pos, ii, jj)
        R = f["R"]
        ei, ej = self.emb(Z[ii]), self.emb(Z[jj])
        ek = self.emb(Z).unsqueeze(0).expand(ii.shape[0], -1, -1)     # (P,N,E)
        env_in = torch.cat([f["env"], ei.unsqueeze(1).expand_as(ek),
                            ej.unsqueeze(1).expand_as(ek), ek], dim=-1)
        msg = self.env_net(env_in) * f["env_w"].unsqueeze(-1)
        env = self.env_post(msg.sum(1))                                # (P,H)
        h = self.pair_net(torch.cat([f["pair"], ei, ej, env], dim=-1))
        blk_local = h.view(-1, NMAX, NMAX) * self.out_scale + self.out_shift
        onsite = (ii == jj).unsqueeze(-1).unsqueeze(-1)
        blk_local = torch.where(onsite, 0.5 * (blk_local + blk_local.transpose(1, 2)), blk_local)
        D = self._ao_rotations(Z, R)                                   # (P,4,4) for frame
        Di = D * self._p_mask(Z[ii])
        Dj = D * self._p_mask(Z[jj])
        # local -> global: H_glob = D^T H_loc D   (D = D(R_frame))
        return Di.transpose(1, 2) @ blk_local @ Dj

    def forward(self, Z: torch.Tensor, pos: torch.Tensor) -> torch.Tensor:
        """Full symmetric (nao x nao) ΔF matrix for one molecule."""
        layout = BasisLayout(Z.detach().cpu().numpy(), **self.layout_kwargs)
        ii, jj, blk = self.predict_blocks(Z, pos)
        return assemble(layout, ii, jj, blk)

    # --------------------------------------------------------------- helpers
    def _p_mask(self, Zs: torch.Tensor) -> torch.Tensor:
        """(P,4,4) mask keeping only the AO rows/cols the element actually has."""
        layout_shells = self.layout_kwargs.get("shells")
        from .basis import DEFAULT_MINIMAL_SHELLS
        table = layout_shells or DEFAULT_MINIMAL_SHELLS
        has_p = torch.tensor([1 in table[int(z)] for z in Zs.tolist()],
                             device=Zs.device)
        m = torch.zeros(Zs.shape[0], NMAX, NMAX, device=Zs.device)
        m[:, 0, 0] = 1.0
        m[has_p] = 1.0
        return m

    def _ao_rotations(self, Z: torch.Tensor, R: torch.Tensor) -> torch.Tensor:
        """D(R) = blockdiag(1, P R P^T) in the stored p order, (P,4,4)."""
        perm = {"xyz": (0, 1, 2), "yzx": (1, 2, 0)}[self.layout_kwargs["p_order"]]
        Pm = torch.zeros(3, 3, device=R.device, dtype=R.dtype)
        for cart, store in enumerate(perm):
            Pm[store, cart] = 1.0
        Rp = Pm @ R @ Pm.T
        D = torch.zeros(R.shape[0], NMAX, NMAX, device=R.device, dtype=R.dtype)
        D[:, 0, 0] = 1.0
        D[:, 1:, 1:] = Rp
        return D

    # ------------------------------------------------------------ persistence
    def save(self, path, extra: dict | None = None):
        torch.save({"hparams": self.hparams, "state_dict": self.state_dict(),
                    "extra": extra or {}}, path)

    @classmethod
    def load(cls, path, map_location="cpu") -> "DeltaFockModel":
        ck = torch.load(path, map_location=map_location, weights_only=False)
        model = cls(**ck["hparams"])
        model.load_state_dict(ck["state_dict"])
        model.eval()
        return model


def assemble(layout: BasisLayout, ii: torch.Tensor, jj: torch.Tensor,
             blk: torch.Tensor) -> torch.Tensor:
    """Scatter (P, NMAX, NMAX) blocks into a symmetric (nao, nao) matrix."""
    nao = layout.nao
    F = torch.zeros(nao, nao, device=blk.device, dtype=blk.dtype)
    off = torch.as_tensor(layout.offsets, device=blk.device)
    nao_atom = torch.as_tensor(layout.atom_nao, device=blk.device)
    # vectorised scatter via index grids
    rows = off[ii].unsqueeze(-1) + torch.arange(NMAX, device=blk.device)     # (P,4)
    cols = off[jj].unsqueeze(-1) + torch.arange(NMAX, device=blk.device)
    rmask = torch.arange(NMAX, device=blk.device).unsqueeze(0) < nao_atom[ii].unsqueeze(-1)
    cmask = torch.arange(NMAX, device=blk.device).unsqueeze(0) < nao_atom[jj].unsqueeze(-1)
    mask = rmask.unsqueeze(-1) & cmask.unsqueeze(1)                           # (P,4,4)
    r = rows.unsqueeze(-1).expand(-1, -1, NMAX)[mask]
    c = cols.unsqueeze(1).expand(-1, NMAX, -1)[mask]
    v = blk[mask]
    F = F.index_put((r, c), v, accumulate=True)
    F = F.index_put((c, r), v, accumulate=True)
    # diagonal blocks were added twice
    diag = ii == jj
    if diag.any():
        rd = rows[diag].unsqueeze(-1).expand(-1, -1, NMAX)[mask[diag]]
        cd = cols[diag].unsqueeze(1).expand(-1, NMAX, -1)[mask[diag]]
        F = F.index_put((rd, cd), -blk[diag][mask[diag]], accumulate=True)
    return F


def extract_blocks(layout: BasisLayout, M: np.ndarray, ii: np.ndarray, jj: np.ndarray
                   ) -> np.ndarray:
    """Target blocks (P, NMAX, NMAX), zero-padded, for the given pair list."""
    out = np.zeros((len(ii), NMAX, NMAX))
    for p, (i, j) in enumerate(zip(ii, jj)):
        bi, bj = layout.block(i, j)
        sub = M[bi, bj]
        out[p, : sub.shape[0], : sub.shape[1]] = sub
    return out
