import numpy as np
from copy import deepcopy
from finesse import constants

cdef rebuild_model_settings(d) noexcept:
    s = ModelSettings()
    for k,v in d.items():
        setattr(s, k, v)
    return s


cdef class ModelSettings:
    def __init__(self):
        self.phase_config = PhaseConfig()
        self.homs_view = None

    def __reduce__(self):
        # This is all to get around that memoryviews can't be deepcopied
        d = {'homs_view': np.asarray(self.homs_view)}
        d.update(
            {
                _: deepcopy(getattr(self, _))
                for _ in dir(self) if not _.startswith('__') and _ not in d and not callable(getattr(self, _))
            }
        )
        return rebuild_model_settings, (d,)

    @property
    def homs(self):
        return np.asarray(self.homs_view)

    @homs.setter
    def homs(self, value):
        self.homs_view = value
        self.max_n = np.max(self.homs_view[:,0])
        self.max_m = np.max(self.homs_view[:,1])
        self.num_HOMs = self.homs_view.shape[0]

    def set_lambda0(self, value):
        self.lambda0 = value
        self.f0 = constants.C_LIGHT / self.lambda0
        self.k0 = 2.0 * constants.PI / self.lambda0


cdef class PhaseConfig:
    pass
