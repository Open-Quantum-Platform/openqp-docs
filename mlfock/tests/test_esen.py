"""Tests for the backbone-feature model using a synthetic equivariant backbone.

The real eSEN checkpoint is gated on Hugging Face, so the head is validated
against a fake backbone that produces exactly equivariant scalars/vectors.
A final smoke test runs with the real backbone only if fairchem and the
checkpoint are available.
"""

import numpy as np
import scipy.linalg
import torch
import pytest

from mlfock.basis import BasisLayout
from mlfock.extract import FockRecord
from mlfock.esen_backbone import FeatureBackbone, _reorder_l1
from mlfock.esen_model import ESENDeltaFockModel
from mlfock.data import FockDataset
from mlfock.train import train
from tests.test_mlfock import toy_molecule, toy_hamiltonian, random_rotation

torch.set_default_dtype(torch.float64)


class FakeBackbone(FeatureBackbone):
    """Scalars: element one-hot + coordination; vectors: weighted neighbour sum."""

    def __init__(self, channels=16):
        super().__init__()
        self.channels = channels
        g = torch.Generator().manual_seed(1)
        self.register_buffer("W", torch.randn(20, channels, generator=g))

    def forward(self, Z, pos):
        rel = pos.unsqueeze(1) - pos.unsqueeze(0)              # (N,N,3)  r_i - r_k
        d = rel.norm(dim=-1) + torch.eye(len(Z)) * 1e9
        w = torch.exp(-0.5 * d)                                # (N,N)
        s = self.W[Z] + (w.sum(1, keepdim=True)) * self.W[Z] * 0.1
        u = rel / d.unsqueeze(-1)
        v = torch.einsum("nk,nka,kc->nac", w, u, self.W[Z])     # (N,3,C)
        return s, v


def test_fake_backbone_is_equivariant():
    Z, pos = toy_molecule()
    bb = FakeBackbone()
    R = random_rotation()
    s0, v0 = bb(torch.as_tensor(Z), torch.as_tensor(pos))
    s1, v1 = bb(torch.as_tensor(Z), torch.as_tensor(pos @ R.T))
    assert torch.allclose(s0, s1)
    assert torch.allclose(torch.einsum("ab,nbc->nac", torch.as_tensor(R), v0), v1, atol=1e-10)


def test_reorder_l1_roundtrip():
    v = torch.randn(5, 3, 2)
    assert torch.equal(_reorder_l1(v, "xyz"), v)
    assert torch.equal(_reorder_l1(v, "yzx")[:, 0], v[:, 1])


def test_esen_model_equivariance_and_permutation():
    Z, pos = toy_molecule()
    model = ESENDeltaFockModel(FakeBackbone(), max_z=8, hidden=32)
    layout = BasisLayout(Z)
    Zt = torch.as_tensor(Z)
    H = model(Zt, torch.as_tensor(pos)).detach().numpy()
    R = random_rotation()
    H_rot = model(Zt, torch.as_tensor(pos @ R.T)).detach().numpy()
    D = scipy.linalg.block_diag(*[layout.atom_rotation(i, R) for i in range(layout.natom)])
    assert np.allclose(H, H.T, atol=1e-10)
    assert np.allclose(D @ H @ D.T, H_rot, atol=1e-6)
    perm = np.random.permutation(len(Z))
    H_perm = model(Zt[perm], torch.as_tensor(pos[perm])).detach().numpy()
    idx = np.concatenate([np.arange(layout.offsets[a], layout.offsets[a + 1]) for a in perm])
    assert np.allclose(H[np.ix_(idx, idx)], H_perm, atol=1e-8)


def test_esen_model_learns_and_roundtrips(tmp_path):
    Z, _ = toy_molecule()
    layout = BasisLayout(Z)
    recs = []
    for k in range(40):
        pos = np.random.randn(len(Z), 3) * 1.8
        recs.append(FockRecord(Z, pos, toy_hamiltonian(Z, pos, layout), np.eye(layout.nao),
                               None, 7, 5, f"g{k}"))
    ds, val = FockDataset(recs[:32], 12.0), FockDataset(recs[32:], 12.0)
    model = ESENDeltaFockModel(FakeBackbone(), max_z=8, hidden=64, cutoff=12.0)
    hist = train(model, ds, val, epochs=60, lr=2e-3, log_every=10 ** 9)
    assert hist[-1]["val_mse"] < hist[0]["val_mse"] * 0.2
    # only head parameters are trainable (backbone buffers carry no grads)
    assert all(p.requires_grad for n, p in model.named_parameters() if not n.startswith("backbone."))
    model.save(tmp_path / "m.pt")
    back = ESENDeltaFockModel.load(tmp_path / "m.pt", backbone=FakeBackbone())
    pos = recs[0].coords_bohr
    a = model(torch.as_tensor(Z), torch.as_tensor(pos)).detach()
    b = back(torch.as_tensor(Z), torch.as_tensor(pos)).detach()
    assert torch.allclose(a, b)


def test_real_esen_smoke():
    pytest.importorskip("fairchem.core", reason="fairchem not installed")
    from mlfock.esen_backbone import ESENBackbone
    try:
        bb = ESENBackbone("esen-sm-direct-all-omol", charge=0, spin=3)
    except Exception as exc:  # gated checkpoint, no network, ...
        pytest.skip(f"eSEN checkpoint unavailable: {exc}")
    Z, pos = toy_molecule()
    s, v = bb(torch.as_tensor(Z), torch.as_tensor(pos))
    assert s.shape == (len(Z), bb.channels) and v.shape == (len(Z), 3, bb.channels)
    model = ESENDeltaFockModel(bb, max_z=8, hidden=32)
    H = model(torch.as_tensor(Z), torch.as_tensor(pos))
    assert H.shape == (BasisLayout(Z).nao,) * 2
