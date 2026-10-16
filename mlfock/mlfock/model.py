"""Block-wise Fock (delta) model with local-frame equivariance.

Output has ``n_channels`` matrices per geometry (default 3: the ROKS
effective Fock whose eigenvectors are the canonical orbitals, and the
alpha and beta Fock matrices the MRSF response needs).
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from .basis import BasisLayout, DFTB_SHELLS, shell_size, _P_PERM, _D_MONO, _D_NORM
from .features import PairFeaturizer, build_pairs


def _mlp(dims, act=nn.SiLU):
    layers = []
    for a, b in zip(dims[:-1], dims[1:]):
        layers += [nn.Linear(a, b), act()]
    return nn.Sequential(*layers[:-1])


class DeltaFockModel(nn.Module):
    """Predict ΔF_ij blocks (n_channels x NMAX x NMAX) for every pair i <= j."""

    def __init__(self, shells: dict | None = None, n_channels: int = 3, max_z: int = 20,
                 emb_dim: int = 32, hidden: int = 128, n_env_layers: int = 2,
                 cutoff: float = 10.0, env_cutoff: float = 8.0, n_rbf: int = 24):
        super().__init__()
        self.shells = {int(z): tuple((int(l), str(k)) for l, k in v)
                       for z, v in (shells or DFTB_SHELLS).items()}
        self.n_channels = n_channels
        self.nmax = max(sum(shell_size(l, k) for l, k in s) for s in self.shells.values())
        self.featurizer = PairFeaturizer(cutoff, env_cutoff, n_rbf)
        self.emb = nn.Embedding(max_z + 1, emb_dim)
        fz = self.featurizer
        self.env_net = _mlp([fz.env_dim + 3 * emb_dim, hidden, hidden])
        self.env_post = _mlp([hidden, hidden])
        nout = n_channels * self.nmax * self.nmax
        self.pair_net = _mlp([fz.pair_dim + 2 * emb_dim + hidden] + [hidden] * n_env_layers + [nout])
        self.register_buffer("out_scale", torch.ones(n_channels, self.nmax, self.nmax))
        self.register_buffer("out_shift", torch.zeros(n_channels, self.nmax, self.nmax))
        self.hparams = dict(shells={z: list(v) for z, v in self.shells.items()},
                            n_channels=n_channels, max_z=max_z, emb_dim=emb_dim, hidden=hidden,
                            n_env_layers=n_env_layers, cutoff=cutoff, env_cutoff=env_cutoff,
                            n_rbf=n_rbf)

    # ------------------------------------------------------------------ core
    def layout(self, Z: torch.Tensor) -> BasisLayout:
        return BasisLayout(Z.detach().cpu().numpy(), shells=self.shells)

    def predict_blocks(self, Z: torch.Tensor, pos: torch.Tensor):
        """(ii, jj, blocks) with blocks (P, C, NMAX, NMAX) in the global frame, i <= j.

        Every off-diagonal pair is evaluated in both orientations and the two
        predictions averaged as H_ij = (f(i,j) + f(j,i)^T)/2, which makes the
        result exactly invariant to atom permutation.
        """
        ii0, jj0 = build_pairs(pos, self.featurizer.cutoff)
        off = ii0 != jj0
        ii = torch.cat([ii0, jj0[off]])
        jj = torch.cat([jj0, ii0[off]])
        blk = self._predict_oriented(Z, pos, ii, jj)
        n0 = ii0.shape[0]
        out = blk[:n0].clone()
        out[off] = 0.5 * (blk[:n0][off] + blk[n0:].transpose(-1, -2))
        return ii0, jj0, out

    def _predict_oriented(self, Z, pos, ii, jj):
        f = self.featurizer(Z, pos, ii, jj)
        R = f["R"]
        ei, ej = self.emb(Z[ii]), self.emb(Z[jj])
        ek = self.emb(Z).unsqueeze(0).expand(ii.shape[0], -1, -1)
        env_in = torch.cat([f["env"], ei.unsqueeze(1).expand_as(ek),
                            ej.unsqueeze(1).expand_as(ek), ek], dim=-1)
        msg = self.env_net(env_in) * f["env_w"].unsqueeze(-1)
        env = self.env_post(msg.sum(1))
        h = self.pair_net(torch.cat([f["pair"], ei, ej, env], dim=-1))
        return self._finish(Z, ii, jj, R, h)

    def _finish(self, Z, ii, jj, R, h):
        """Shared tail: local block -> symmetrise onsite -> rotate to global."""
        blk_local = h.view(-1, self.n_channels, self.nmax, self.nmax) * self.out_scale + self.out_shift
        onsite = (ii == jj).view(-1, 1, 1, 1)
        blk_local = torch.where(onsite, 0.5 * (blk_local + blk_local.transpose(-1, -2)), blk_local)
        # Local-frame functions are phi_loc = D(R) phi_glob, so H_loc = D H_glob D^T and
        # H_glob = D^-1 H_loc D^-T.  D^-1 = D(R^T) because D is a representation; it is
        # NOT D^T for Cartesian d shells (xx, yy, zz are not mutually orthogonal).
        Rinv = R.transpose(-1, -2)
        Di = self.atom_rotations(Z[ii], Rinv).unsqueeze(1)              # (P,1,NMAX,NMAX)
        Dj = self.atom_rotations(Z[jj], Rinv).unsqueeze(1)
        return Di @ blk_local @ Dj.transpose(-1, -2)

    def forward(self, Z: torch.Tensor, pos: torch.Tensor) -> torch.Tensor:
        """(n_channels, nao, nao) symmetric ΔF matrices for one molecule."""
        layout = self.layout(Z)
        ii, jj, blk = self.predict_blocks(Z, pos)
        return assemble(layout, ii, jj, blk)

    # --------------------------------------------------------------- rotation
    def atom_rotations(self, Zs: torch.Tensor, R: torch.Tensor) -> torch.Tensor:
        """(P, NMAX, NMAX) AO rotation D(R) for the element of each pair member,
        zero beyond the atom's AO count so padding never leaks."""
        P = R.shape[0]
        D = torch.zeros(P, self.nmax, self.nmax, device=R.device, dtype=R.dtype)
        Zs = Zs.tolist()
        # group pairs by element so each element's shell structure is applied once
        for z in set(Zs):
            sel = torch.tensor([k for k, zz in enumerate(Zs) if zz == z], device=R.device)
            off = 0
            for l, kind in self.shells[int(z)]:
                n = shell_size(l, kind)
                D[sel, off:off + n, off:off + n] = _shell_rotation_torch(l, kind, R[sel])
                off += n
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


def _shell_rotation_torch(l: int, kind: str, R: torch.Tensor) -> torch.Tensor:
    """(P, n, n) rotation matrices for one shell type."""
    P = R.shape[0]
    if l == 0:
        return torch.ones(P, 1, 1, device=R.device, dtype=R.dtype)
    if l == 1:
        perm = _P_PERM[kind]
        Pm = torch.zeros(3, 3, device=R.device, dtype=R.dtype)
        for cart, store in enumerate(perm):
            Pm[store, cart] = 1.0
        return Pm @ R @ Pm.T
    if l == 2 and kind == "cart":
        T = torch.zeros(P, 6, 6, device=R.device, dtype=R.dtype)
        for i, (a, b) in enumerate(_D_MONO):
            for j, (c, d) in enumerate(_D_MONO):
                if c == d:
                    T[:, i, j] = R[:, a, c] * R[:, b, c]
                else:
                    T[:, i, j] = R[:, a, c] * R[:, b, d] + R[:, a, d] * R[:, b, c]
        nrm = torch.as_tensor(_D_NORM, device=R.device, dtype=R.dtype)
        return nrm.view(1, 6, 1) * T / nrm.view(1, 1, 6)
    raise NotImplementedError(f"l={l} kind={kind}")


def assemble(layout: BasisLayout, ii: torch.Tensor, jj: torch.Tensor,
             blk: torch.Tensor) -> torch.Tensor:
    """Scatter (P, C, NMAX, NMAX) blocks into symmetric (C, nao, nao) matrices."""
    nC, nmax = blk.shape[1], blk.shape[2]
    nao = layout.nao
    F = torch.zeros(nC, nao, nao, device=blk.device, dtype=blk.dtype)
    off = torch.as_tensor(layout.offsets, device=blk.device)
    nao_atom = torch.as_tensor(layout.atom_nao, device=blk.device)
    ar = torch.arange(nmax, device=blk.device)
    rows = off[ii].unsqueeze(-1) + ar
    cols = off[jj].unsqueeze(-1) + ar
    rmask = ar.unsqueeze(0) < nao_atom[ii].unsqueeze(-1)
    cmask = ar.unsqueeze(0) < nao_atom[jj].unsqueeze(-1)
    mask = rmask.unsqueeze(-1) & cmask.unsqueeze(1)                        # (P, nmax, nmax)
    r = rows.unsqueeze(-1).expand(-1, -1, nmax)[mask]
    c = cols.unsqueeze(1).expand(-1, nmax, -1)[mask]
    for ch in range(nC):
        v = blk[:, ch][mask]
        F[ch] = F[ch].index_put((r, c), v, accumulate=True)
        F[ch] = F[ch].index_put((c, r), v, accumulate=True)
    diag = ii == jj
    if diag.any():
        md = mask[diag]
        rd = rows[diag].unsqueeze(-1).expand(-1, -1, nmax)[md]
        cd = cols[diag].unsqueeze(1).expand(-1, nmax, -1)[md]
        for ch in range(nC):
            F[ch] = F[ch].index_put((rd, cd), -blk[diag][:, ch][md], accumulate=True)
    return F


def extract_blocks(layout: BasisLayout, M: np.ndarray, ii, jj, nmax: int) -> np.ndarray:
    """Target blocks (P, C, nmax, nmax), zero padded, from (C, nao, nao) matrices."""
    M = np.asarray(M)
    if M.ndim == 2:
        M = M[None]
    out = np.zeros((len(ii), M.shape[0], nmax, nmax))
    for p, (i, j) in enumerate(zip(ii, jj)):
        bi, bj = layout.block(int(i), int(j))
        sub = M[:, bi, bj]
        out[p, :, : sub.shape[1], : sub.shape[2]] = sub
    return out
