"""Synthetic Slater-Koster-like Hamiltonians for arbitrary Cartesian s/p/d shells."""

import numpy as np
from mlfock.basis import BasisLayout, shell_rotation, shell_size

SP_SHELLS = {1: [(0, "cart")], 6: [(0, "cart"), (1, "cart")], 8: [(0, "cart"), (1, "cart")]}
SPD_SHELLS = {1: [(0, "cart"), (0, "cart")],
              6: [(0, "cart"), (0, "cart"), (1, "cart"), (0, "cart"), (1, "cart"), (2, "cart")],
              8: [(0, "cart"), (0, "cart"), (1, "cart"), (0, "cart"), (1, "cart"), (2, "cart")]}


def random_rotation(rng=np.random):
    q, _ = np.linalg.qr(rng.randn(3, 3))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q


def toy_molecule(n_heavy=3, n_h=4, rng=np.random):
    Z = np.array([6] * n_heavy + [1] * n_h)
    pos = rng.randn(len(Z), 3) * 1.8
    return Z, pos


def _pair_block(layout, i, j, u, f):
    """Equivariant block built from the unit vector u = r_ij/|r_ij| (frame-free construction)."""
    ni, nj = layout.atom_nao[i], layout.atom_nao[j]
    # Build the block in a frame where u is the z axis, then rotate: block(u) = D_i(Rz->u) B0 D_j^T
    z = u / np.linalg.norm(u)
    x = np.cross(z, [0.3, -0.2, 0.9]); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.stack([x, y, z]).T         # columns = frame axes; maps frame coords -> global
    B0 = np.zeros((ni, nj))
    # deterministic, shell-structured pattern along z (axial symmetry about z)
    oi = 0
    for li, ki in layout.atom_shells[i]:
        oj = 0
        for lj, kj in layout.atom_shells[j]:
            si, sj = shell_size(li, ki), shell_size(lj, kj)
            sub = np.zeros((si, sj))
            # only m=0-like components couple along the axis: s(0), pz(index 2), dzz(index 2)
            ax = {0: 0, 1: 2, 2: 2}
            sub[ax[li], ax[lj]] = f * (0.8 ** (li + lj)) * (-1) ** (li + lj)
            if li == 1 and lj == 1:
                sub[0, 0] = sub[1, 1] = 0.3 * f       # pi coupling
            B0[oi:oi + si, oj:oj + sj] = sub
            oj += sj
        oi += si
    Di = layout.atom_rotation(i, R)
    Dj = layout.atom_rotation(j, R)
    return Di @ B0 @ Dj.T


def toy_hamiltonian(Z, pos, layout: BasisLayout, n_channels=1):
    """Rotationally equivariant, permutation covariant toy Hamiltonian(s)."""
    H = np.zeros((n_channels, layout.nao, layout.nao))
    for ch in range(n_channels):
        scale = 1.0 + 0.5 * ch
        for i in range(layout.natom):
            bi, _ = layout.block(i, i)
            # invariant onsite operator = constant x intra-shell metric (identity for s/p,
            # the Cartesian-d Gram matrix with <xx|yy> = 1/3 for d)
            blocks = []
            for l, k in layout.atom_shells[i]:
                n = shell_size(l, k)
                G = np.eye(n)
                if l == 2 and k == "cart":
                    G[:3, :3] = np.full((3, 3), 1.0 / 3.0) + np.eye(3) * (2.0 / 3.0)
                blocks.append(-0.5 * scale / (l + 1) * G)
            from mlfock.basis import _block_diag
            H[ch][bi, bi] = _block_diag(blocks)
        for i in range(layout.natom):
            for j in range(i + 1, layout.natom):
                r = pos[j] - pos[i]
                d = np.linalg.norm(r)
                blk = _pair_block(layout, i, j, r / d, scale * np.exp(-0.6 * d))
                bi, bj = layout.block(i, j)
                H[ch][bi, bj] = blk
                H[ch][bj, bi] = blk.T
    return H
