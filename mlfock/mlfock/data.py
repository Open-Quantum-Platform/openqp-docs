"""Dataset of FockRecords -> per-pair block targets."""

from __future__ import annotations

from pathlib import Path
import torch

from .extract import FockRecord
from .features import build_pairs
from .model import extract_blocks


class FockDataset(torch.utils.data.Dataset):
    """One item = one geometry.  ``shells`` and ``nmax`` must match the model."""

    def __init__(self, records: list[FockRecord], cutoff: float, nmax: int):
        self.records = records
        self.cutoff = cutoff
        self.nmax = nmax
        self.shells = records[0].shells
        self.items = [self._prepare(r) for r in records]

    def _prepare(self, rec: FockRecord):
        Z = torch.as_tensor(rec.atomic_numbers, dtype=torch.long)
        pos = torch.as_tensor(rec.coords_bohr, dtype=torch.get_default_dtype())
        layout = rec.layout()
        ii, jj = build_pairs(pos, self.cutoff)
        target = extract_blocks(layout, rec.delta(), ii.numpy(), jj.numpy(), self.nmax)
        return {"Z": Z, "pos": pos, "ii": ii, "jj": jj,
                "target": torch.as_tensor(target, dtype=pos.dtype), "tag": rec.tag}

    def __len__(self):
        return len(self.items)

    def __getitem__(self, k):
        return self.items[k]

    def block_statistics(self):
        t = torch.cat([it["target"] for it in self.items], 0)
        return t.mean(0), t.std(0).clamp(min=1e-4)

    @classmethod
    def from_dir(cls, path, cutoff: float, nmax: int) -> "FockDataset":
        files = sorted(Path(path).glob("*.npz"))
        if not files:
            raise FileNotFoundError(f"no .npz records under {path}")
        return cls([FockRecord.load(f) for f in files], cutoff, nmax)
