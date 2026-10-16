"""Atomic-orbital layout, block slicing, and AO rotation matrices.

Supports the shells OpenQP uses (verified against OpenQP overlap matrices of
rotated molecules, see tests/test_openqp.py):

* s                      : 1 component
* p, Cartesian order     : (x, y, z)                       -> rotates as R
* d, Cartesian order     : (xx, yy, zz, xy, xz, yz), with the cross terms
                           normalised by sqrt(3) relative to xx (GAMESS
                           convention)                     -> 6x6 rep of R
* p, DFTB (openqp-dftb)  : m-ascending real spherical (y, z, x)

A layout is a per-atom list of shells; the same element always carries the
same shells for a given basis, so a ``shells`` table {Z: [(l, kind), ...]}
describes every molecule.  ``kind`` is "cart" or, for p only, "yzx".
"""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

# Minimal valence shells per element (openqp-dftb SK basis).
DFTB_SHELLS = {z: ((0, "cart"),) for z in (1, 2)}
DFTB_SHELLS.update({z: ((0, "cart"), (1, "yzx")) for z in range(3, 19)})

_P_PERM = {"cart": (0, 1, 2), "xyz": (0, 1, 2), "yzx": (1, 2, 0)}
_D_MONO = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]
_D_NORM = np.array([1.0, 1.0, 1.0, np.sqrt(3.0), np.sqrt(3.0), np.sqrt(3.0)])


def shell_size(l: int, kind: str) -> int:
    if kind == "cart" or l <= 1:
        return (l + 1) * (l + 2) // 2
    return 2 * l + 1


def shells_from_openqp(mol) -> dict:
    """Per-element shell table from a live OpenQP molecule (after set_basis).

    OpenQP's ``get_basis`` gives one entry per shell with its centre atom
    and angular momentum; the AO layout is Cartesian and shell-ordered.
    """
    b = mol.data.get_basis()
    centers = np.asarray(b["centers"]).astype(int)
    angs = np.asarray(b["angs"]).astype(int)
    Z = np.asarray(mol.get_atoms()).astype(int).ravel()
    table = {}
    for atom in range(len(Z)):
        shells = tuple((int(l), "cart") for c, l in zip(centers, angs) if c == atom)
        prev = table.setdefault(int(Z[atom]), shells)
        if prev != shells:
            raise ValueError(f"element {Z[atom]} carries different shells on different atoms")
    nbf = sum(shell_size(l, k) for atom in range(len(Z)) for l, k in table[int(Z[atom])])
    if nbf != int(b["nbf"]):
        raise ValueError(f"Cartesian layout gives {nbf} AOs but OpenQP reports {b['nbf']}; "
                         "spherical shells are not supported yet")
    return table


@dataclass
class BasisLayout:
    """Per-atom shells and AO offsets for one molecule."""

    atomic_numbers: np.ndarray
    shells: dict = field(default_factory=lambda: dict(DFTB_SHELLS))

    def __post_init__(self):
        self.atomic_numbers = np.asarray(self.atomic_numbers, dtype=int).ravel()
        self.shells = {int(z): tuple((int(l), str(k)) for l, k in v) for z, v in self.shells.items()}
        self.atom_shells = [self.shells[int(z)] for z in self.atomic_numbers]
        self.atom_nao = np.array([sum(shell_size(l, k) for l, k in s) for s in self.atom_shells])
        self.offsets = np.concatenate([[0], np.cumsum(self.atom_nao)])
        self.nao = int(self.offsets[-1])
        self.natom = len(self.atomic_numbers)

    # ----------------------------------------------------------------- slicing
    def block(self, i: int, j: int) -> tuple[slice, slice]:
        return (slice(self.offsets[i], self.offsets[i + 1]),
                slice(self.offsets[j], self.offsets[j + 1]))

    def max_nao(self) -> int:
        return int(max(sum(shell_size(l, k) for l, k in s) for s in self.shells.values()))

    def ao_atom(self) -> np.ndarray:
        """1-based atom index per AO (openqp-dftb reference-file convention)."""
        return np.concatenate([np.full(n, i + 1) for i, n in enumerate(self.atom_nao)]).astype(np.int64)

    def ao_l(self) -> np.ndarray:
        out = []
        for s in self.atom_shells:
            for l, k in s:
                out += [l] * shell_size(l, k)
        return np.asarray(out, dtype=np.int64)

    # ---------------------------------------------------------------- rotation
    def atom_rotation(self, i: int, R: np.ndarray) -> np.ndarray:
        """Block-diagonal AO rotation D_i(R): a block transforms as D_i H_ij D_j^T."""
        return _block_diag([shell_rotation(l, k, R) for l, k in self.atom_shells[i]])

    def full_rotation(self, R: np.ndarray) -> np.ndarray:
        return _block_diag([self.atom_rotation(i, R) for i in range(self.natom)])


def shell_rotation(l: int, kind: str, R: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    if l == 0:
        return np.ones((1, 1))
    if l == 1:
        perm = _P_PERM[kind]
        P = np.zeros((3, 3))
        for cart, store in enumerate(perm):
            P[store, cart] = 1.0
        return P @ R @ P.T
    if l == 2 and kind == "cart":
        T = np.zeros((6, 6))
        for i, (a, b) in enumerate(_D_MONO):
            for j, (c, d) in enumerate(_D_MONO):
                T[i, j] = R[a, c] * R[b, c] if c == d else R[a, c] * R[b, d] + R[a, d] * R[b, c]
        return np.diag(_D_NORM) @ T @ np.diag(1.0 / _D_NORM)
    raise NotImplementedError(f"rotation for l={l} kind={kind} not implemented")


def _block_diag(blocks):
    n = sum(b.shape[0] for b in blocks)
    out = np.zeros((n, n))
    k = 0
    for b in blocks:
        m = b.shape[0]
        out[k:k + m, k:k + m] = b
        k += m
    return out


def layout_from_nbf(atomic_numbers, nbf: int) -> BasisLayout:
    """DFTB minimal layout, checked against the exported AO count."""
    layout = BasisLayout(atomic_numbers, shells=DFTB_SHELLS)
    if layout.nao != nbf:
        raise ValueError(f"minimal s/p layout gives {layout.nao} AOs but backend exported {nbf}")
    return layout
