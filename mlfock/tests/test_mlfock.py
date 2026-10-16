"""Self-contained tests (no OpenQP): equivariance, permutation, I/O, learning, on-the-fly."""

import numpy as np
import scipy.linalg
import torch
import pytest

from mlfock.basis import BasisLayout, shell_rotation
from mlfock.extract import (FockRecord, fock_from_orbitals, overlap_from_complete_orbitals,
                            unpack_triangular, write_simple_mrsf_reference,
                            read_simple_mrsf_reference)
from mlfock.model import DeltaFockModel, assemble, extract_blocks
from mlfock.features import build_pairs, pair_frames
from mlfock.predict import FockPredictor, commutator_residual, subspace_fidelities
from mlfock.data import FockDataset
from mlfock.train import train
from tests.synthetic import SP_SHELLS, SPD_SHELLS, random_rotation, toy_molecule, toy_hamiltonian

torch.set_default_dtype(torch.float64)
torch.manual_seed(0)
np.random.seed(0)


def test_fock_roundtrip():
    n = 6
    A = np.random.randn(n, n)
    S = A @ A.T + n * np.eye(n)
    F = np.random.randn(n, n); F = F + F.T
    eps, C = scipy.linalg.eigh(F, S)
    assert np.allclose(fock_from_orbitals(C, eps, S), F)
    assert np.allclose(overlap_from_complete_orbitals(C), S)
    M = np.random.randn(4, 4); M = M + M.T
    assert np.allclose(unpack_triangular(M[np.tril_indices(4)], 4), M)


def test_shell_rotations_are_representations():
    R1, R2 = random_rotation(), random_rotation()
    for l, kind in [(0, "cart"), (1, "cart"), (1, "yzx"), (2, "cart")]:
        D1, D2, D12 = shell_rotation(l, kind, R1), shell_rotation(l, kind, R2), shell_rotation(l, kind, R1 @ R2)
        assert np.allclose(D1 @ D2, D12, atol=1e-12)
        assert np.allclose(D1 @ shell_rotation(l, kind, R1.T), np.eye(D1.shape[0]), atol=1e-12)
        if l < 2:   # s/p AOs are orthonormal within a shell -> orthogonal D; Cartesian d is not
            assert np.allclose(D1 @ D1.T, np.eye(D1.shape[0]), atol=1e-12)


@pytest.mark.parametrize("shells", [SP_SHELLS, SPD_SHELLS])
def test_toy_hamiltonian_is_equivariant(shells):
    Z, pos = toy_molecule()
    layout = BasisLayout(Z, shells=shells)
    H = toy_hamiltonian(Z, pos, layout)[0]
    R = random_rotation()
    H_rot = toy_hamiltonian(Z, pos @ R.T, layout)[0]
    D = layout.full_rotation(R)
    assert np.allclose(D @ H @ D.T, H_rot, atol=1e-10)


def test_frames_rotate_with_molecule():
    Z, pos = toy_molecule()
    pos_t = torch.as_tensor(pos)
    ii, jj = build_pairs(pos_t, 12.0)
    R = torch.as_tensor(random_rotation())
    Fr, degenerate = pair_frames(pos_t, ii, jj, 8.0, return_degenerate=True)
    Fr_rot = pair_frames(pos_t @ R.T, ii, jj, 8.0)
    err = (Fr_rot - Fr @ R.T).abs().amax(dim=(1, 2))
    # an atom with a single neighbour has an axially symmetric environment: x is arbitrary there
    assert torch.all(err[~degenerate] < 1e-8)


@pytest.mark.parametrize("shells", [SP_SHELLS, SPD_SHELLS])
def test_model_equivariance_and_permutation(shells):
    Z, pos = toy_molecule()
    model = DeltaFockModel(shells=shells, n_channels=2, max_z=8, hidden=32)
    layout = BasisLayout(Z, shells=shells)
    Zt = torch.as_tensor(Z)
    H = model(Zt, torch.as_tensor(pos)).detach().numpy()
    R = random_rotation()
    H_rot = model(Zt, torch.as_tensor(pos @ R.T)).detach().numpy()
    D = layout.full_rotation(R)
    for ch in range(2):
        assert np.allclose(H[ch], H[ch].T, atol=1e-10)
        assert np.allclose(D @ H[ch] @ D.T, H_rot[ch], atol=1e-6)
    perm = np.random.permutation(len(Z))
    H_perm = model(Zt[perm], torch.as_tensor(pos[perm])).detach().numpy()
    idx = np.concatenate([np.arange(layout.offsets[a], layout.offsets[a + 1]) for a in perm])
    assert np.allclose(H[:, idx][:, :, idx], H_perm, atol=1e-8)


def test_assemble_matches_extract():
    Z, pos = toy_molecule()
    layout = BasisLayout(Z, shells=SPD_SHELLS)
    H = toy_hamiltonian(Z, pos, layout, n_channels=3)
    ii, jj = build_pairs(torch.as_tensor(pos), 50.0)
    blk = extract_blocks(layout, H, ii.numpy(), jj.numpy(), layout.max_nao())
    H2 = assemble(layout, ii, jj, torch.as_tensor(blk)).numpy()
    assert np.allclose(H, H2)


def _records(Z, layout, n, n_channels=3):
    recs = []
    for k in range(n):
        pos = np.random.randn(len(Z), 3) * 1.8
        H = toy_hamiltonian(Z, pos, layout, n_channels)
        recs.append(FockRecord(Z, pos, H, np.eye(layout.nao), None, 7, 5, layout.shells, f"g{k}"))
    return recs


def test_model_learns_toy_hamiltonian():
    Z, _ = toy_molecule()
    layout = BasisLayout(Z, shells=SP_SHELLS)
    recs = _records(Z, layout, 40)
    ds, val = FockDataset(recs[:32], 12.0, layout.max_nao()), FockDataset(recs[32:], 12.0, layout.max_nao())
    model = DeltaFockModel(shells=SP_SHELLS, n_channels=3, max_z=8, hidden=64, cutoff=12.0)
    hist = train(model, ds, val, epochs=60, lr=2e-3, log_every=10 ** 9)
    assert hist[-1]["val_mse"] < 0.2 * hist[0]["val_mse"], hist[-1]
    pos = recs[0].coords_bohr
    Href = toy_hamiltonian(Z, pos, layout, 3)
    pred = FockPredictor([model], fock_builder=lambda Pa, Pb: (Href[1], Href[2]))
    orb = pred.predict(Z, pos, np.eye(layout.nao), np.zeros((layout.nao,) * 2), 7, 5)
    assert orb.C.shape == (layout.nao, layout.nao) and orb.residual is not None
    eps_ref, C_ref = scipy.linalg.eigh(Href[0], np.eye(layout.nao))
    fid = subspace_fidelities(orb.C, C_ref, np.eye(layout.nao), 7, 5)
    assert fid["closed"] > 0.9, fid


def test_record_io_and_reference_file(tmp_path):
    Z, pos = toy_molecule()
    layout = BasisLayout(Z, shells=SPD_SHELLS)
    H = toy_hamiltonian(Z, pos, layout, 3)
    rec = FockRecord(Z, pos, H, np.eye(layout.nao), 0.5 * H[0], 7, 5, layout.shells, "t", np.arange(layout.nao) * 0.1)
    rec.save(tmp_path / "r.npz")
    back = FockRecord.load(tmp_path / "r.npz")
    assert np.allclose(back.delta(), H - 0.5 * H[0][None]) and back.tag == "t"
    assert back.layout().nao == layout.nao
    eps, C = scipy.linalg.eigh(H[0], np.eye(layout.nao))
    write_simple_mrsf_reference(tmp_path / "ref.bin", np.eye(layout.nao), C, eps, H[1], H[2], layout, 7, 5)
    r = read_simple_mrsf_reference(tmp_path / "ref.bin")
    assert np.allclose(r["Ca"], C) and np.allclose(r["Fa"], H[1]) and np.allclose(r["Fb"], H[2])
    assert r["occ_a"].sum() == 7 and r["occ_b"].sum() == 5
    assert r["ao_atom"].max() == layout.natom and set(r["ao_l"]) == {0, 1, 2}


def test_onthefly_loop_calls_oracle_and_refits():
    from mlfock.onthefly import OnTheFlyLearner
    Z, _ = toy_molecule()
    layout = BasisLayout(Z, shells=SP_SHELLS)
    I = np.eye(layout.nao)

    def oracle(Z_, pos_):
        return FockRecord(Z_, pos_, toy_hamiltonian(Z_, pos_, layout, 3), I, None, 7, 5, layout.shells, "o")

    models = [DeltaFockModel(shells=SP_SHELLS, n_channels=3, max_z=8, hidden=32, cutoff=12.0) for _ in range(2)]
    learner = OnTheFlyLearner(models, oracle, tol_uncertainty=1e-9, oracle_every=10 ** 6,
                              refit_every_new=3, refit_epochs=2, log=lambda *a: None)
    learner.seed([oracle(Z, np.random.randn(len(Z), 3) * 1.8) for _ in range(8)])
    used = []
    for _ in range(4):
        orb, flag = learner.step(Z, np.random.randn(len(Z), 3) * 1.8, I, np.zeros_like(I), 7, 5)
        used.append(flag)
    learner.wait()
    assert all(used) and learner.stats["oracle_calls"] == 4 and learner.stats["refits"] >= 1
