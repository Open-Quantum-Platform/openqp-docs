"""Use a pretrained Meta FAIR eSEN / UMA backbone as the feature extractor.

The backbone (``fairchem.core.models.uma.escn_md.eSCNMDBackbone``, which is
what both eSEN and UMA checkpoints wrap) returns per-atom SO(3)-equivariant
node embeddings of shape ``(N, (lmax+1)^2, C)`` ordered by l.  We take

* l = 0  ->  scalar features   (N, C)
* l = 1  ->  vector features   (N, 3, C)

and hand them to :class:`mlfock.esen_model.ESENDeltaFockModel`, which rotates
the vectors into each pair's local frame (making them invariant) and predicts
the Fock block exactly as the plain model does.  Everything downstream
(assembly, eigen-solve, on-the-fly loop) is unchanged.

Checkpoints: ``esen-sm-direct-all-omol``, ``esen-md-direct-all-omol``,
``uma-s-1p1`` ... (gated on Hugging Face; ``huggingface-cli login`` first).
``fairchem-core`` and ``ase`` must be installed.

The backbone was trained on OMol25 (ωB97M-V/def2-TZVPD, Angstrom) and knows
the system's charge and spin multiplicity.  For the MRSF reference pass
``spin=3`` (triplet) and the molecular charge.
"""

from __future__ import annotations

import hashlib
import numpy as np
import torch
import torch.nn as nn

BOHR2ANG = 0.52917721067


class FeatureBackbone(nn.Module):
    """Interface: ``forward(Z, pos_bohr) -> (scalars (N,C), vectors (N,3,C))``.

    Vectors must transform as Cartesian (x, y, z) vectors under rotation.
    """

    channels: int = 0

    def forward(self, Z: torch.Tensor, pos_bohr: torch.Tensor):  # pragma: no cover
        raise NotImplementedError


class ESENBackbone(FeatureBackbone):
    def __init__(self, model_name: str = "esen-sm-direct-all-omol", device: str = "cpu",
                 charge: int = 0, spin: int = 3, task_name: str = "omol",
                 radius: float = 6.0, max_neigh: int = 300, trainable_blocks: int = 0,
                 l1_order: str | None = None, cache: bool = True):
        super().__init__()
        from fairchem.core import pretrained_mlip  # noqa: PLC0415

        pu = pretrained_mlip.get_predict_unit(model_name, device=device,
                                              inference_settings="batch")
        self.backbone = pu.model.module.backbone
        self.backbone.eval()
        self.model_name = model_name
        self.device = device
        self.charge = int(charge)
        self.spin = int(spin)
        self.task_name = task_name
        self.radius = radius
        self.max_neigh = max_neigh
        self.channels = int(self.backbone.sphere_channels)
        self.trainable_blocks = int(trainable_blocks)
        self._set_trainable(self.trainable_blocks)
        self._cache: dict | None = {} if (cache and self.trainable_blocks == 0) else None
        # l=1 component order inside the backbone's spherical basis.
        self.l1_order = l1_order or detect_l1_order(self)

    # -------------------------------------------------------------- training
    def _set_trainable(self, k: int):
        for p in self.backbone.parameters():
            p.requires_grad_(False)
        if k > 0:
            blocks = list(self.backbone.blocks)[-k:]
            for b in blocks:
                for p in b.parameters():
                    p.requires_grad_(True)
                b.train()

    # --------------------------------------------------------------- forward
    def _atomic_data(self, Z: torch.Tensor, pos_bohr: torch.Tensor):
        import ase  # noqa: PLC0415
        from fairchem.core.datasets.atomic_data import AtomicData, atomicdata_list_to_batch  # noqa: PLC0415

        atoms = ase.Atoms(numbers=Z.detach().cpu().numpy(),
                          positions=pos_bohr.detach().cpu().numpy() * BOHR2ANG)
        atoms.info["charge"] = self.charge
        atoms.info["spin"] = self.spin
        data = AtomicData.from_ase(atoms, r_edges=True, radius=self.radius,
                                   max_neigh=self.max_neigh, task_name=self.task_name,
                                   r_data_keys=["charge", "spin"], r_energy=False,
                                   r_forces=False, r_stress=False)
        batch = atomicdata_list_to_batch([data])
        return batch.to(self.device)

    def _raw_embedding(self, Z, pos_bohr) -> torch.Tensor:
        data = self._atomic_data(Z, pos_bohr)
        out = self.backbone(data)
        return out["node_embedding"]                       # (N, S, C)

    def forward(self, Z: torch.Tensor, pos_bohr: torch.Tensor):
        key = None
        if self._cache is not None:
            key = _geom_key(Z, pos_bohr)
            if key in self._cache:
                s, v = self._cache[key]
                return s.to(pos_bohr.device), v.to(pos_bohr.device)
        ctx = torch.no_grad() if self.trainable_blocks == 0 else torch.enable_grad()
        with ctx:
            emb = self._raw_embedding(Z, pos_bohr)
        s = emb[:, 0, :].to(pos_bohr.dtype)
        v = _reorder_l1(emb[:, 1:4, :], self.l1_order).to(pos_bohr.dtype)
        if key is not None:
            self._cache[key] = (s.detach().cpu(), v.detach().cpu())
        return s, v

    def extra_state(self) -> dict:
        return dict(model_name=self.model_name, charge=self.charge, spin=self.spin,
                    task_name=self.task_name, radius=self.radius, max_neigh=self.max_neigh,
                    trainable_blocks=self.trainable_blocks, l1_order=self.l1_order)


# ------------------------------------------------------------------ helpers
_L1_PERMS = {"xyz": (0, 1, 2), "yzx": (1, 2, 0), "zxy": (2, 0, 1), "xzy": (0, 2, 1),
             "yxz": (1, 0, 2), "zyx": (2, 1, 0)}


def _reorder_l1(v: torch.Tensor, order: str) -> torch.Tensor:
    """(N,3,C) stored in ``order`` -> Cartesian (x,y,z)."""
    perm = _L1_PERMS[order]          # perm[cart] = stored index
    return v[:, list(perm), :]


def detect_l1_order(backbone: ESENBackbone, n_trials: int = 2) -> str:
    """Empirically find how the backbone's l=1 components map onto (x, y, z).

    Rotates a small random molecule and picks the component order under
    which the l=1 features transform as Cartesian vectors.  Robust to any
    spherical-harmonic sign/order convention of the checkpoint.
    """
    gen = torch.Generator().manual_seed(0)
    Z = torch.tensor([6, 6, 8, 1, 1, 1, 1])
    best, best_err = "xyz", float("inf")
    for _ in range(n_trials):
        pos = torch.randn(len(Z), 3, generator=gen, dtype=torch.float64) * 2.0
        q, _ = torch.linalg.qr(torch.randn(3, 3, generator=gen, dtype=torch.float64))
        if torch.det(q) < 0:
            q[:, 0] *= -1
        with torch.no_grad():
            e0 = backbone._raw_embedding(Z, pos)[:, 1:4, :].double()
            e1 = backbone._raw_embedding(Z, pos @ q.T)[:, 1:4, :].double()
        for name in _L1_PERMS:
            v0 = _reorder_l1(e0, name)
            v1 = _reorder_l1(e1, name)
            err = (torch.einsum("ab,nbc->nac", q, v0) - v1).abs().max().item()
            scale = v0.abs().max().item() + 1e-12
            if err / scale < best_err:
                best, best_err = name, err / scale
    if best_err > 1e-2:
        raise RuntimeError(f"no l=1 ordering is equivariant (rel err {best_err:.2e}); "
                           "check backbone precision or pass l1_order explicitly")
    return best


def _geom_key(Z: torch.Tensor, pos: torch.Tensor) -> str:
    h = hashlib.sha1()
    h.update(Z.detach().cpu().numpy().astype(np.int64).tobytes())
    h.update(np.round(pos.detach().cpu().numpy().astype(np.float64), 8).tobytes())
    return h.hexdigest()
