"""Self-contained tests: no OpenQP needed.

A synthetic 'DFTB-like' Hamiltonian is generated from a simple distance
dependent tight-binding rule so that exact equivariance can be checked and
the model can be shown to learn it.
"""

import numpy as np
import torch
import scipy.linalg
import pytest

from mlfock.basis import BasisLayout
from mlfock.extract import (FockRecord, fock_from_orbitals, overlap_from_complete_orbitals,
                            project_fock, unpack_triangular)
from mlfock.model import DeltaFockModel, NMAX, assemble, extract_blocks
from mlfock.features import build_pairs, pair_frames
from mlfock.predict import FockPredictor, density_matrix, commutator_residual
from mlfock.data import FockDataset
from mlfock.train import train

torch.set_default_dtype(torch.float64)
torch.manual_seed(0)
np.random.seed(0)


def random_rotation():
    q, _ = np.linalg.qr(np.random.randn(3, 3))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q


def toy_molecule(n_heavy=3, n_h=4):
    Z = np.array([6] * n_heavy + [1] * n_h)
    pos = np.random.randn(len(Z), 3) * 1.8
    pos[:n_heavy] *= 0.8
    return Z, pos


def toy_hamiltonian(Z, pos, layout: BasisLayout, p_order="yzx"):
    """Slater-Koster-like s/p Hamiltonian with correct rotational behaviour."""
    perm = {"xyz": (0, 1, 2), "yzx": (1, 2, 0)}[p_order]
    H = np.zeros((layout.nao, layout.nao))
    for i in range(layout.natom):
        bi, _ = layout.block(i, i)
        H[bi, bi] = np.diag([-0.5] + [-0.2] * (layout.atom_nao[i] - 1))
    for i in range(layout.natom):
        for j in range(i + 1, layout.natom):
            r = pos[j] - pos[i]
            d = np.linalg.norm(r)
            u = r / d
            f = np.exp(-0.6 * d)
            ni, nj = layout.atom_nao[i], layout.atom_nao[j]
            blk = np.zeros((ni, nj))
            blk[0, 0] = -1.0 * f
            if nj == 4:
                v = np.zeros(3)
                for cart, store in enumerate(perm):
                    v[store] = u[cart]
                blk[0, 1:] = 0.8 * f * v
            if ni == 4:
                v = np.zeros(3)
                for cart, store in enumerate(perm):
                    v[store] = u[cart]
                blk[1:, 0] = -0.8 * f * v
            if ni == 4 and nj == 4:
                uu = np.zeros((3, 3))
                P = np.zeros((3, 3))
                for cart, store in enumerate(perm):
                    P[store, cart] = 1
                uu = P @ np.outer(u, u) @ P.T
                blk[1:, 1:] = f * (0.5 * uu - 0.3 * (np.eye(3) - uu))
            bi, bj = layout.block(i, j)
            H[bi, bj] = blk
            H[bj, bi] = blk.T
    return H


def test_fock_roundtrip():
    n = 6
    A = np.random.randn(n, n)
    S = A @ A.T + n * np.eye(n)
    F = np.random.randn(n, n)
    F = F + F.T
    eps, C = scipy.linalg.eigh(F, S)
    assert np.allclose(fock_from_orbitals(C, eps, S), F)
    assert np.allclose(overlap_from_complete_orbitals(C), S)


def test_unpack_triangular():
    n = 4
    M = np.random.randn(n, n)
    M = M + M.T
    packed = M[np.tril_indices(n)]
    assert np.allclose(unpack_triangular(packed, n), M)


def test_projection_preserves_subspace():
    n_big, n_small = 10, 4
    A = np.random.randn(n_big, n_big)
    S_big = A @ A.T + n_big * np.eye(n_big)
    S_cross = S_big[:, :n_small]            # small basis = first 4 big functions
    F = np.random.randn(n_big, n_big)
    F = F + F.T
    Fs, Ss = project_fock(F, S_big, S_cross)
    assert np.allclose(Fs, F[:n_small, :n_small])
    assert np.allclose(Ss, S_big[:n_small, :n_small])


def test_toy_hamiltonian_is_equivariant():
    Z, pos = toy_molecule()
    layout = BasisLayout(Z)
    H = toy_hamiltonian(Z, pos, layout)
    R = random_rotation()
    H_rot = toy_hamiltonian(Z, pos @ R.T, layout)
    D = scipy.linalg.block_diag(*[layout.atom_rotation(i, R) for i in range(layout.natom)])
    assert np.allclose(D @ H @ D.T, H_rot, atol=1e-10)


def test_frames_rotate_with_molecule():
    Z, pos = toy_molecule()
    pos_t = torch.as_tensor(pos)
    ii, jj = build_pairs(pos_t, 12.0)
    R = random_rotation()
    Fr = pair_frames(pos_t, ii, jj, 8.0)
    Fr_rot = pair_frames(pos_t @ torch.as_tensor(R).T, ii, jj, 8.0)
    # rows are axes in global coords: rotated frame = frame @ R^T
    assert torch.allclose(Fr_rot, Fr @ torch.as_tensor(R).T, atol=1e-8)


def test_model_equivariance_untrained():
    Z, pos = toy_molecule()
    model = DeltaFockModel(max_z=8, hidden=32)
    layout = BasisLayout(Z)
    Zt = torch.as_tensor(Z)
    H = model(Zt, torch.as_tensor(pos)).detach().numpy()
    R = random_rotation()
    H_rot = model(Zt, torch.as_tensor(pos @ R.T)).detach().numpy()
    D = scipy.linalg.block_diag(*[layout.atom_rotation(i, R) for i in range(layout.natom)])
    assert np.allclose(H, H.T, atol=1e-10)
    assert np.allclose(D @ H @ D.T, H_rot, atol=1e-6)
    # permutation of atoms
    perm = np.random.permutation(len(Z))
    H_perm = model(Zt[perm], torch.as_tensor(pos[perm])).detach().numpy()
    lp = BasisLayout(Z[perm])
    idx = np.concatenate([np.arange(layout.offsets[a], layout.offsets[a + 1]) for a in perm])
    assert np.allclose(H[np.ix_(idx, idx)], H_perm, atol=1e-8)


def test_assemble_matches_extract():
    Z, pos = toy_molecule()
    layout = BasisLayout(Z)
    H = toy_hamiltonian(Z, pos, layout)
    ii, jj = build_pairs(torch.as_tensor(pos), 50.0)
    blk = extract_blocks(layout, H, ii.numpy(), jj.numpy())
    H2 = assemble(layout, ii, jj, torch.as_tensor(blk)).numpy()
    assert np.allclose(H, H2)


def test_model_learns_toy_hamiltonian():
    Z, _ = toy_molecule()
    layout = BasisLayout(Z)
    records = []
    for k in range(40):
        pos = np.random.randn(len(Z), 3) * 1.8
        H = toy_hamiltonian(Z, pos, layout)
        records.append(FockRecord(Z, pos, H, np.eye(layout.nao), None, 7, 5, f"g{k}"))
    ds = FockDataset(records[:32], cutoff=12.0)
    val = FockDataset(records[32:], cutoff=12.0)
    model = DeltaFockModel(max_z=8, hidden=64, cutoff=12.0, env_cutoff=8.0)
    hist = train(model, ds, val, epochs=60, lr=2e-3, log_every=1000)
    _, std = ds.block_statistics()
    rel = hist[-1]["val_mse"] ** 0.5 / float(std.mean())
    assert hist[-1]["val_mse"] < hist[0]["val_mse"] * 0.2, hist[-1]
    assert rel < 0.5

    # prediction pathway + eigen-solve + residual API
    pred = FockPredictor([model], fock_builder=lambda P: toy_hamiltonian(Z, pos, layout))
    orb = pred.predict(Z, pos, np.eye(layout.nao), None, 7, 5)
    assert orb.C.shape == (layout.nao, layout.nao)
    assert orb.residual is not None
    P = density_matrix(orb.C, 7, 5)
    assert commutator_residual(orb.F, P, orb.S) < 1e-10


def test_record_io(tmp_path):
    Z, pos = toy_molecule()
    layout = BasisLayout(Z)
    H = toy_hamiltonian(Z, pos, layout)
    rec = FockRecord(Z, pos, H, np.eye(layout.nao), 0.5 * H, 3, 2, "t")
    rec.save(tmp_path / "r.npz")
    back = FockRecord.load(tmp_path / "r.npz")
    assert np.allclose(back.delta(), 0.5 * H)
    assert back.tag == "t"


def test_onthefly_loop_calls_oracle_and_refits():
    from mlfock.onthefly import OnTheFlyLearner
    Z, _ = toy_molecule()
    layout = BasisLayout(Z)

    def oracle(Z_, pos_):
        return FockRecord(Z_, pos_, toy_hamiltonian(Z_, pos_, layout), np.eye(layout.nao),
                          None, 7, 5, "oracle")

    seeds = [oracle(Z, np.random.randn(len(Z), 3) * 1.8) for _ in range(8)]
    models = [DeltaFockModel(max_z=8, hidden=32, cutoff=12.0) for _ in range(2)]
    learner = OnTheFlyLearner(models, oracle, tol_uncertainty=1e-9, oracle_every=10 ** 6,
                              refit_every_new=3, refit_epochs=2, log=lambda *a: None)
    learner.seed(seeds)
    used = []
    for _ in range(4):
        pos = np.random.randn(len(Z), 3) * 1.8
        orb, flag = learner.step(Z, pos, np.eye(layout.nao), None, 7, 5)
        used.append(flag)
        assert orb.C.shape == (layout.nao, layout.nao)
    learner.wait()
    assert all(used)                      # untrained ensemble disagrees -> oracle every step
    assert learner.stats["oracle_calls"] == 4
    assert learner.stats["refits"] >= 1
    assert len(learner.buffer) == 12
