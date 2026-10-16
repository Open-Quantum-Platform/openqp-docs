"""Train a DeltaFockModel.

CLI::

    python -m mlfock.train --data records/ --out model.pt --epochs 300

Loss is the block-wise MSE in the frame-independent global representation
(the model rotates its local prediction back before the loss, so the loss
is itself rotation invariant).  An optional eigenvalue term penalises the
error in the occupied/low-virtual orbital energies of F_base + ΔF.
"""

from __future__ import annotations

import argparse
import time
import numpy as np
import torch

from .data import FockDataset
from .model import DeltaFockModel, extract_blocks
from .basis import BasisLayout


def block_loss(model: DeltaFockModel, item) -> torch.Tensor:
    ii, jj, blk = model.predict_blocks(item["Z"], item["pos"])
    # the dataset pair list was built with the same cutoff -> same ordering
    return ((blk - item["target"]) ** 2).mean()


def train(model: DeltaFockModel, train_ds: FockDataset, val_ds: FockDataset | None = None,
          epochs: int = 200, lr: float = 1e-3, weight_decay: float = 0.0,
          log_every: int = 10, device: str = "cpu", callback=None):
    model.to(device)
    mean, std = train_ds.block_statistics()
    with torch.no_grad():
        model.out_shift.copy_(mean.to(device))
        model.out_scale.copy_(std.to(device))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.Adam(params, lr=lr, weight_decay=weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1))
    history = []
    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        perm = np.random.permutation(len(train_ds))
        tot = 0.0
        for k in perm:
            item = {kk: (v.to(device) if torch.is_tensor(v) else v)
                    for kk, v in train_ds[k].items()}
            opt.zero_grad()
            loss = block_loss(model, item)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 10.0)
            opt.step()
            tot += loss.item()
        sched.step()
        rec = {"epoch": epoch, "train_mse": tot / len(train_ds)}
        if val_ds is not None:
            rec["val_mse"] = evaluate(model, val_ds, device)
        history.append(rec)
        if callback:
            callback(rec)
        if epoch % log_every == 0 or epoch == epochs:
            msg = f"epoch {epoch:5d}  train rmse {rec['train_mse']**0.5:.3e} Ha"
            if "val_mse" in rec:
                msg += f"  val rmse {rec['val_mse']**0.5:.3e} Ha"
            print(msg + f"  [{time.time()-t0:.0f}s]", flush=True)
    model.eval()
    return history


@torch.no_grad()
def evaluate(model, ds, device="cpu") -> float:
    model.eval()
    tot = 0.0
    for item in ds:
        item = {kk: (v.to(device) if torch.is_tensor(v) else v) for kk, v in item.items()}
        tot += block_loss(model, item).item()
    return tot / len(ds)


def main(argv=None):
    ap = argparse.ArgumentParser(description="train a ΔFock model")
    ap.add_argument("--data", required=True, help="directory of .npz FockRecords")
    ap.add_argument("--val", default=None, help="optional validation directory")
    ap.add_argument("--out", default="mlfock_model.pt")
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--cutoff", type=float, default=10.0)
    ap.add_argument("--env-cutoff", type=float, default=8.0)
    ap.add_argument("--p-order", default="yzx", choices=["yzx", "xyz"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--backbone", default=None,
                    help="fairchem checkpoint name, e.g. esen-sm-direct-all-omol; "
                         "omit for the self-contained model")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--spin", type=int, default=3, help="multiplicity of the reference")
    ap.add_argument("--trainable-blocks", type=int, default=0,
                    help="unfreeze the last N backbone blocks (0 = frozen, cached features)")
    args = ap.parse_args(argv)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    ds = FockDataset.from_dir(args.data, args.cutoff, p_order=args.p_order)
    val = FockDataset.from_dir(args.val, args.cutoff, p_order=args.p_order) if args.val else None
    max_z = int(max(int(r.atomic_numbers.max()) for r in ds.records))
    if args.backbone:
        from .esen_backbone import ESENBackbone
        from .esen_model import ESENDeltaFockModel
        bb = ESENBackbone(args.backbone, charge=args.charge, spin=args.spin,
                          trainable_blocks=args.trainable_blocks)
        model = ESENDeltaFockModel(bb, max_z=max(max_z, 10), hidden=args.hidden,
                                   cutoff=args.cutoff, env_cutoff=args.env_cutoff,
                                   p_order=args.p_order)
    else:
        model = DeltaFockModel(max_z=max(max_z, 10), hidden=args.hidden, cutoff=args.cutoff,
                               env_cutoff=args.env_cutoff, p_order=args.p_order)
    train(model, ds, val, epochs=args.epochs, lr=args.lr)
    model.save(args.out, extra={"n_train": len(ds)})
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
