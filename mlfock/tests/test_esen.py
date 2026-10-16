"""Backbone-feature model tests with a synthetic equivariant backbone."""

import numpy as np
import torch
import pytest

from mlfock.basis import BasisLayout
from mlfock.extract import FockRecord
from mlfock.esen_backbone import FeatureBackbone, _reorder_l1
from mlfock.esen_model import ESENDeltaFockModel
from mlfock.data import FockDataset
from mlfock.train import train
from tests.synthetic import SPD_SHELLS, random_rotation, toy_molecule, toy_hamiltonian

torch.set_default_dtype(torch.float64)


class FakeBackbone(FeatureBackbone):
    def __init__(self, channels=16):
        super().__init__()
        self.channels = channels
        g = torch.Generator().manual_seed(1)
        self.register_buffer("W", torch.randn(20, channels, generator=g))

    def forward(self, Z, pos):
        rel = pos.unsqueeze(1) - pos.unsqueeze(0)
        d = rel.norm(dim=-1) + torch.eye(len(Z)) * 1e9
        w = torch.exp(-0.5 * d)
        s = self.W[Z] * (1 + 0.1 * w.sum(1, keepdim=True))
        v = torch.einsum("nk,nka,kc->nac", w, rel / d.unsqueeze(-1), self.W[Z])
        return s, v


def test_fake_backbone_is_equivariant():
    Z, pos = toy_molecule()
    bb = FakeBackbone()
    R = torch.as_tensor(random_rotation())
    s0, v0 = bb(torch.as_tensor(Z), torch.as_tensor(pos))
    s1, v1 = bb(torch.as_tensor(Z), torch.as_tensor(pos) @ R.T)
    assert torch.allclose(s0, s1) and torch.allclose(torch.einsum("ab,nbc->nac", R, v0), v1, atol=1e-10)
    v = torch.randn(5, 3, 2)
    assert torch.equal(_reorder_l1(v, "yzx")[:, 0], v[:, 1])


def test_esen_model_equivariance_permutation_learning(tmp_path):
    Z, pos = toy_molecule()
    layout = BasisLayout(Z, shells=SPD_SHELLS)
    model = ESENDeltaFockModel(FakeBackbone(), shells=SPD_SHELLS, n_channels=3, max_z=8, hidden=32, cutoff=12.0)
    Zt = torch.as_tensor(Z)
    H = model(Zt, torch.as_tensor(pos)).detach().numpy()
    R = random_rotation()
    H_rot = model(Zt, torch.as_tensor(pos @ R.T)).detach().numpy()
    D = layout.full_rotation(R)
    for ch in range(3):
        assert np.allclose(D @ H[ch] @ D.T, H_rot[ch], atol=1e-6)
    perm = np.random.permutation(len(Z))
    H_perm = model(Zt[perm], torch.as_tensor(pos[perm])).detach().numpy()
    idx = np.concatenate([np.arange(layout.offsets[a], layout.offsets[a + 1]) for a in perm])
    assert np.allclose(H[:, idx][:, :, idx], H_perm, atol=1e-8)

    recs = [FockRecord(Z, p, toy_hamiltonian(Z, p, layout, 3), np.eye(layout.nao), None, 7, 5, layout.shells, f"g{k}")
            for k, p in enumerate(np.random.randn(40, len(Z), 3) * 1.8)]
    ds, val = FockDataset(recs[:32], 12.0, layout.max_nao()), FockDataset(recs[32:], 12.0, layout.max_nao())
    hist = train(model, ds, val, epochs=40, lr=2e-3, log_every=10 ** 9)
    assert hist[-1]["val_mse"] < 0.3 * hist[0]["val_mse"]
    model.save(tmp_path / "m.pt")
    back = ESENDeltaFockModel.load(tmp_path / "m.pt", backbone=FakeBackbone())
    p = recs[0].coords_bohr
    assert torch.allclose(model(Zt, torch.as_tensor(p)).detach(), back(Zt, torch.as_tensor(p)).detach())


def test_real_esen_smoke():
    pytest.importorskip("fairchem.core", reason="fairchem not installed")
    from mlfock.esen_backbone import ESENBackbone
    try:
        bb = ESENBackbone("esen-sm-direct-all-omol", charge=0, spin=3)
    except Exception as exc:
        pytest.skip(f"eSEN checkpoint unavailable: {exc}")
    Z, pos = toy_molecule()
    s, v = bb(torch.as_tensor(Z), torch.as_tensor(pos))
    assert s.shape == (len(Z), bb.channels) and v.shape == (len(Z), 3, bb.channels)
