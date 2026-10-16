"""ΔFock model whose environment features come from a pretrained backbone."""

from __future__ import annotations

import torch
import torch.nn as nn

from .model import DeltaFockModel, NMAX, _mlp
from .esen_backbone import FeatureBackbone


class ESENDeltaFockModel(DeltaFockModel):
    """Same block/frame machinery as :class:`DeltaFockModel`; the hand-built
    neighbour-sum environment network is replaced by backbone features.

    Per oriented pair (i -> j) the network sees, all rotation invariant:
      * distance RBF, element embeddings (as before)
      * backbone scalars s_i, s_j                      (C each)
      * backbone vectors in the pair frame  R v_i, R v_j (3C each)
    """

    def __init__(self, backbone: FeatureBackbone, max_z: int = 20, emb_dim: int = 32,
                 hidden: int = 128, n_env_layers: int = 2, cutoff: float = 10.0,
                 env_cutoff: float = 8.0, n_rbf: int = 24, p_order: str = "yzx",
                 shells: dict | None = None, feat_dim: int = 64):
        super().__init__(max_z, emb_dim, hidden, n_env_layers, cutoff, env_cutoff,
                         n_rbf, p_order, shells)
        # the parent's environment nets are unused; drop them to keep the
        # parameter count honest
        del self.env_net, self.env_post
        self.backbone = backbone
        C = backbone.channels
        self.scalar_proj = nn.Linear(C, feat_dim)
        self.vector_proj = nn.Linear(3 * C, feat_dim)
        fz = self.featurizer
        self.pair_net = _mlp([fz.pair_dim + 2 * emb_dim + 4 * feat_dim]
                             + [hidden] * n_env_layers + [NMAX * NMAX])
        self.hparams.update(feat_dim=feat_dim, backbone="external")

    def _predict_oriented(self, Z, pos, ii, jj):
        f = self.featurizer(Z, pos, ii, jj)
        R = f["R"]                                               # (P,3,3)
        s, v = self.backbone(Z, pos)                             # (N,C), (N,3,C)
        si, sj = self.scalar_proj(s[ii]), self.scalar_proj(s[jj])
        vi = torch.einsum("pab,pbc->pac", R, v[ii]).flatten(1)  # local-frame vectors
        vj = torch.einsum("pab,pbc->pac", R, v[jj]).flatten(1)
        vi, vj = self.vector_proj(vi), self.vector_proj(vj)
        ei, ej = self.emb(Z[ii]), self.emb(Z[jj])
        h = self.pair_net(torch.cat([f["pair"], ei, ej, si, sj, vi, vj], dim=-1))
        blk_local = h.view(-1, NMAX, NMAX) * self.out_scale + self.out_shift
        onsite = (ii == jj).unsqueeze(-1).unsqueeze(-1)
        blk_local = torch.where(onsite, 0.5 * (blk_local + blk_local.transpose(1, 2)), blk_local)
        D = self._ao_rotations(Z, R)
        Di = D * self._p_mask(Z[ii])
        Dj = D * self._p_mask(Z[jj])
        return Di.transpose(1, 2) @ blk_local @ Dj

    # ------------------------------------------------------------ persistence
    def head_state_dict(self) -> dict:
        return {k: v for k, v in self.state_dict().items() if not k.startswith("backbone.")}

    def save(self, path, extra: dict | None = None):
        bb = getattr(self.backbone, "extra_state", lambda: {})()
        trainable = {k: v for k, v in self.state_dict().items()
                     if k.startswith("backbone.") and
                     dict(self.named_parameters()).get(k, torch.empty(0)).requires_grad}
        torch.save({"hparams": self.hparams, "head": self.head_state_dict(),
                    "backbone_cfg": bb, "backbone_trainable": trainable,
                    "extra": extra or {}}, path)

    @classmethod
    def load(cls, path, backbone: FeatureBackbone | None = None, map_location="cpu"):
        ck = torch.load(path, map_location=map_location, weights_only=False)
        if backbone is None:
            from .esen_backbone import ESENBackbone  # noqa: PLC0415
            backbone = ESENBackbone(**ck["backbone_cfg"])
        hp = {k: v for k, v in ck["hparams"].items() if k != "backbone"}
        model = cls(backbone, **hp)
        model.load_state_dict(ck["head"], strict=False)
        if ck["backbone_trainable"]:
            model.load_state_dict(ck["backbone_trainable"], strict=False)
        model.eval()
        return model
