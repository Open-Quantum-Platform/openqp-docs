"""ΔFock model whose environment features come from a pretrained backbone."""

from __future__ import annotations

import torch
import torch.nn as nn

from .model import DeltaFockModel, _mlp
from .esen_backbone import FeatureBackbone


class ESENDeltaFockModel(DeltaFockModel):
    """Same frames/blocks as :class:`DeltaFockModel`; the hand-built
    neighbour-sum environment network is replaced by backbone features:
    scalars s_i, s_j and vectors rotated into the pair frame R v_i, R v_j."""

    def __init__(self, backbone: FeatureBackbone, shells: dict | None = None,
                 n_channels: int = 3, max_z: int = 20, emb_dim: int = 32, hidden: int = 128,
                 n_env_layers: int = 2, cutoff: float = 10.0, env_cutoff: float = 8.0,
                 n_rbf: int = 24, feat_dim: int = 64):
        super().__init__(shells, n_channels, max_z, emb_dim, hidden, n_env_layers, cutoff,
                         env_cutoff, n_rbf)
        del self.env_net, self.env_post
        self.backbone = backbone
        C = backbone.channels
        self.scalar_proj = nn.Linear(C, feat_dim)
        self.vector_proj = nn.Linear(3 * C, feat_dim)
        fz = self.featurizer
        nout = n_channels * self.nmax * self.nmax
        self.pair_net = _mlp([fz.pair_dim + 2 * emb_dim + 4 * feat_dim]
                             + [hidden] * n_env_layers + [nout])
        self.hparams.update(feat_dim=feat_dim)

    def _predict_oriented(self, Z, pos, ii, jj):
        f = self.featurizer(Z, pos, ii, jj)
        R = f["R"]
        s, v = self.backbone(Z, pos)
        si, sj = self.scalar_proj(s[ii]), self.scalar_proj(s[jj])
        vi = self.vector_proj(torch.einsum("pab,pbc->pac", R, v[ii]).flatten(1))
        vj = self.vector_proj(torch.einsum("pab,pbc->pac", R, v[jj]).flatten(1))
        ei, ej = self.emb(Z[ii]), self.emb(Z[jj])
        h = self.pair_net(torch.cat([f["pair"], ei, ej, si, sj, vi, vj], dim=-1))
        return self._finish(Z, ii, jj, R, h)

    # ------------------------------------------------------------ persistence
    def head_state_dict(self) -> dict:
        return {k: v for k, v in self.state_dict().items() if not k.startswith("backbone.")}

    def save(self, path, extra: dict | None = None):
        bb = getattr(self.backbone, "extra_state", lambda: {})()
        params = dict(self.named_parameters())
        trainable = {k: v for k, v in self.state_dict().items()
                     if k.startswith("backbone.") and k in params and params[k].requires_grad}
        torch.save({"hparams": self.hparams, "head": self.head_state_dict(),
                    "backbone_cfg": bb, "backbone_trainable": trainable,
                    "extra": extra or {}}, path)

    @classmethod
    def load(cls, path, backbone: FeatureBackbone | None = None, map_location="cpu"):
        ck = torch.load(path, map_location=map_location, weights_only=False)
        if backbone is None:
            from .esen_backbone import ESENBackbone  # noqa: PLC0415
            backbone = ESENBackbone(**ck["backbone_cfg"])
        model = cls(backbone, **ck["hparams"])
        model.load_state_dict(ck["head"], strict=False)
        if ck["backbone_trainable"]:
            model.load_state_dict(ck["backbone_trainable"], strict=False)
        model.eval()
        return model
