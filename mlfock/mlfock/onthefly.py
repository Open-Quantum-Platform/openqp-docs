"""Residual-gated active learning during dynamics.

Loop per MD step::

    orbitals = learner.step(Z, pos, S, F_base)
       -> ML prediction; if uncertainty > tol (or every `oracle_every` steps)
          call the oracle (full SCF), use its orbitals, store the record,
          and refit in a background thread with a replay buffer.

The oracle is any callable ``(Z, pos_bohr) -> FockRecord``; the OpenQP
bridge provides one.  Retraining uses a copy of the model so the MD thread
never sees half-updated weights.
"""

from __future__ import annotations

import copy
import threading
import time
import numpy as np
import torch

from .data import FockDataset
from .extract import FockRecord
from .model import DeltaFockModel
from .predict import FockPredictor, Orbitals
from .train import train


class OnTheFlyLearner:
    def __init__(self, models, oracle, tol_uncertainty: float = 2e-3,
                 tol_residual: float | None = None, oracle_every: int = 50,
                 buffer_size: int = 2000, refit_every_new: int = 10,
                 refit_epochs: int = 20, lr: float = 3e-4, fock_builder=None,
                 cutoff: float | None = None, log=print):
        self.models = list(models) if isinstance(models, (list, tuple)) else [models]
        self.predictor = FockPredictor(self.models, fock_builder=fock_builder)
        self.oracle = oracle
        self.tol_u = tol_uncertainty
        self.tol_r = tol_residual
        self.oracle_every = oracle_every
        self.buffer: list[FockRecord] = []
        self.buffer_size = buffer_size
        self.refit_every_new = refit_every_new
        self.refit_epochs = refit_epochs
        self.lr = lr
        self.cutoff = cutoff or self.models[0].hparams["cutoff"]
        self.log = log
        self._new_since_fit = 0
        self._fit_thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.stats = {"steps": 0, "oracle_calls": 0, "refits": 0}

    # ---------------------------------------------------------------- public
    def seed(self, records: list[FockRecord]):
        self.buffer.extend(records)
        self.buffer = self.buffer[-self.buffer_size:]

    def step(self, Z, pos_bohr, S, Hcore, n_alpha: int, n_beta: int) -> tuple[Orbitals, bool]:
        """Return (orbitals, used_oracle).  S and Hcore are the cheap one-electron
        matrices for this geometry (OpenQP set_basis + ints_1e)."""
        self.stats["steps"] += 1
        with self._lock:
            orb = self.predictor.predict(Z, pos_bohr, S, Hcore, n_alpha, n_beta)
        trigger = orb.uncertainty > self.tol_u
        if self.tol_r is not None and orb.residual is not None:
            trigger |= orb.residual > self.tol_r
        trigger |= (self.stats["steps"] % self.oracle_every == 0)
        if not trigger:
            return orb, False

        rec = self.oracle(Z, pos_bohr)
        self.stats["oracle_calls"] += 1
        self.log(f"[mlfock] step {self.stats['steps']}: oracle call "
                 f"(uncert {orb.uncertainty:.2e}, resid {orb.residual})")
        self.buffer.append(rec)
        self.buffer = self.buffer[-self.buffer_size:]
        self._new_since_fit += 1
        if self._new_since_fit >= self.refit_every_new:
            self._launch_refit()
        import scipy.linalg
        eps, C = scipy.linalg.eigh(rec.F_ref[0], rec.S)
        return Orbitals(rec.F_ref[0], rec.F_ref[1], rec.F_ref[2], rec.S, C, eps, 0.0, 0.0), True

    def wait(self):
        if self._fit_thread is not None:
            self._fit_thread.join()

    # --------------------------------------------------------------- private
    def _launch_refit(self):
        if self._fit_thread is not None and self._fit_thread.is_alive():
            return  # a refit is still running; data will be picked up next time
        self._new_since_fit = 0
        records = list(self.buffer)
        self._fit_thread = threading.Thread(target=self._refit, args=(records,), daemon=True)
        self._fit_thread.start()

    def _refit(self, records):
        t0 = time.time()
        ds = FockDataset(records, self.cutoff, self.models[0].nmax)
        new_models = []
        for m in self.models:
            mc = copy.deepcopy(m)
            train(mc, ds, epochs=self.refit_epochs, lr=self.lr, log_every=10 ** 9)
            new_models.append(mc)
        with self._lock:
            for m, mc in zip(self.models, new_models):
                m.load_state_dict(mc.state_dict())
                m.eval()
        self.stats["refits"] += 1
        self.log(f"[mlfock] refit on {len(records)} records in {time.time()-t0:.0f}s")
