"""Atomic-orbital layout, block slicing, and rotation matrices.

Only s and p shells are needed for the DFTB minimal valence basis of H, C,
N, O, F (1 or 4 AOs per atom).  d shells are supported in the layout but
the rotation matrix for real d functions is not implemented (raises).

Two p-component orderings exist in practice:

* ``"xyz"`` : Cartesian order (px, py, pz)
* ``"yzx"`` : m-ascending real spherical order (p_{-1}=y, p_0=z, p_{+1}=x);
              this is the order the openqp-dftb native library uses.

Rotation matrices are built for the chosen ordering so a block predicted in
a local frame is rotated back consistently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

# Minimal valence shells per element (l values), DFTB-style.
DEFAULT_MINIMAL_SHELLS = {
    1: (0,),            # H : s
    2: (0,),            # He
    3: (0, 1), 4: (0, 1), 5: (0, 1), 6: (0, 1), 7: (0, 1), 8: (0, 1), 9: (0, 1),
    10: (0, 1),
    11: (0, 1), 12: (0, 1), 13: (0, 1), 14: (0, 1), 15: (0, 1), 16: (0, 1),
    17: (0, 1), 18: (0, 1),
}

_P_PERM = {"xyz": (0, 1, 2), "yzx": (1, 2, 0)}  # position of x,y,z in storage


@dataclass
class BasisLayout:
    """Per-atom shell list and AO offsets for one molecule."""

    atomic_numbers: np.ndarray
    shells: dict = field(default_factory=lambda: dict(DEFAULT_MINIMAL_SHELLS))
    p_order: str = "yzx"

    def __post_init__(self):
        self.atomic_numbers = np.asarray(self.atomic_numbers, dtype=int).ravel()
        if self.p_order not in _P_PERM:
            raise ValueError(f"unknown p_order {self.p_order!r}")
        self.atom_shells = [tuple(self.shells[int(z)]) for z in self.atomic_numbers]
        self.atom_nao = np.array([sum(2 * l + 1 for l in s) for s in self.atom_shells])
        self.offsets = np.concatenate([[0], np.cumsum(self.atom_nao)])
        self.nao = int(self.offsets[-1])
        self.natom = len(self.atomic_numbers)

    # ----------------------------------------------------------------- slicing
    def block(self, i: int, j: int) -> tuple[slice, slice]:
        return (slice(self.offsets[i], self.offsets[i + 1]),
                slice(self.offsets[j], self.offsets[j + 1]))

    def max_nao(self) -> int:
        return int(self.atom_nao.max())

    # ---------------------------------------------------------------- rotation
    def atom_rotation(self, i: int, R: np.ndarray) -> np.ndarray:
        """Block-diagonal AO rotation matrix D_i(R) for atom i.

        For a global rotation ``R`` (3x3, acting on column vectors),
        a block transforms as ``H'_ij = D_i H_ij D_j^T``.
        """
        blocks = []
        for l in self.atom_shells[i]:
            if l == 0:
                blocks.append(np.ones((1, 1)))
            elif l == 1:
                blocks.append(self._p_rotation(R))
            else:
                raise NotImplementedError("d-shell rotation not implemented")
        return _block_diag(blocks)

    def _p_rotation(self, R: np.ndarray) -> np.ndarray:
        """Rotation of real p functions in the stored component order."""
        perm = _P_PERM[self.p_order]   # storage index of (x, y, z)
        P = np.zeros((3, 3))
        for cart, store in enumerate(perm):
            P[store, cart] = 1.0           # P maps xyz-vector -> stored order
        return P @ R @ P.T

    def is_p_atom(self, i: int) -> bool:
        return 1 in self.atom_shells[i]


def _block_diag(blocks):
    n = sum(b.shape[0] for b in blocks)
    out = np.zeros((n, n))
    k = 0
    for b in blocks:
        m = b.shape[0]
        out[k:k + m, k:k + m] = b
        k += m
    return out


def layout_from_nbf(atomic_numbers, nbf: int, p_order: str = "yzx") -> BasisLayout:
    """Reconstruct the minimal layout from the exported AO count.

    Mirrors the openqp-dftb adapter's ``_dftb_shells`` heuristic: H-like
    atoms carry 1 AO, everything else 4 (s+p).  Raises if that does not add
    up to ``nbf`` so a d-shell element is never silently mislabeled.
    """
    layout = BasisLayout(atomic_numbers, p_order=p_order)
    if layout.nao != nbf:
        raise ValueError(
            f"minimal s/p layout gives {layout.nao} AOs but backend exported {nbf}; "
            "supply an explicit `shells` mapping")
    return layout
