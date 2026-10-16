"""Dataset of FockRecords -> per-pair block targets."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import torch

from .basis import BasisLayout
from .extract import FockRecord
from .features import build_pairs
from .model import NMAX, extract_blocks


class FockDataset(torch.utils.data.Dataset):
    """Holds whole molecules; one item = one geometry."""

    def __init__(self, records: list[FockRecord], cutoff: float, p_order: str = "yzx",
                 shells: dict | None = None):
        self.records = records
        self.cutoff = cutoff
        self.layout_kwargs = {"p_order": p_order}
        if shells is not None:
            self.layout_kwargs["shells"] = shells
        self.items = [self._prepare(r) for r in records]

    def _prepare(self, rec: FockRecord):
        Z = torch.as_tensor(rec.atomic_numbers, dtype=torch.long)
        pos = torch.as_tensor(rec.coords_bohr, dtype=torch.get_default_dtype())
        layout = BasisLayout(rec.atomic_numbers, **self.layout_kwargs)
        if layout.nao != rec.F_ref.shape[0]:
            raise ValueError(f"record {rec.tag}: layout nao {layout.nao} != matrix {rec.F_ref.shape[0]}")
        ii, jj = build_pairs(pos, self.cutoff)
        target = extract_blocks(layout, rec.delta(), ii.numpy(), jj.numpy())
        return {"Z": Z, "pos": pos, "ii": ii, "jj": jj,
                "target": torch.as_tensor(target, dtype=pos.dtype), "tag": rec.tag}

    def __len__(self):
        return len(self.items)

    def __getitem__(self, k):
        return self.items[k]

    def block_statistics(self):
        """Mean/std of target blocks (for out_scale / out_shift initialisation)."""
        t = torch.cat([it["target"] for it in self.items], 0)
        return t.mean(0), t.std(0).clamp(min=1e-4)

    @classmethod
    def from_dir(cls, path, cutoff: float, **kw) -> "FockDataset":
        files = sorted(Path(path).glob("*.npz"))
        if not files:
            raise FileNotFoundError(f"no .npz records under {path}")
        return cls([FockRecord.load(f) for f in files], cutoff, **kw)
