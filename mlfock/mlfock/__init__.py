"""mlfock: learn the Fock/KS matrix (or a delta on top of DFTB) from geometry.

Pipeline
--------
1. ``extract``  : pull converged AO Fock matrices out of OpenQP (DFT side)
                  and the DFTB Hamiltonian out of the openqp-dftb adapter.
2. ``project``  : optionally project the DFT Fock matrix into the minimal
                  valence (DFTB) basis so the delta lives in one basis.
3. ``model``    : SE(3)-equivariant block model (pair local frames) that
                  maps geometry -> Fock blocks.  Target = F_ref - F_base.
4. ``predict``  : assemble the full matrix, diagonalize with the overlap,
                  and report a self-consistency residual.
5. ``onthefly`` : residual-gated active learning during dynamics.
"""

from .basis import BasisLayout
from .model import DeltaFockModel
from .predict import FockPredictor
from .onthefly import OnTheFlyLearner

try:  # optional: pretrained Meta FAIR backbone
    from .esen_model import ESENDeltaFockModel
except ImportError:  # pragma: no cover
    ESENDeltaFockModel = None

__all__ = ["BasisLayout", "DeltaFockModel", "ESENDeltaFockModel", "FockPredictor",
           "OnTheFlyLearner"]
__version__ = "0.1.0"
