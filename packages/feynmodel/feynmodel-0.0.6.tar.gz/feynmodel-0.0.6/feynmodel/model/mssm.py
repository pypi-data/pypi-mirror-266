import ufo_mssm

from feynmodel.feyn_model import FeynModel
from feynmodel.interface.ufo import ufo_to_feynmodel


class MSSM(FeynModel):
    def __init__(self):
        FeynModel.__init__(self, "Minimal Supersymmetric Standard Model")
        ufo_to_feynmodel(ufo_mssm, self)
