from math import sqrt

import numpy as np
from numpy.random import SFC64, Generator

from qablet.base.mc import MCModel, MCStateBase
from qablet.base.utils import Forwards


# Define a class for the state of a single asset BS Local Vol MC process
class LVMCState(MCStateBase):
    def __init__(self, timetable, dataset):
        super().__init__(timetable, dataset)

        # fetch the model parameters from the dataset
        self.n = dataset["MC"]["PATHS"]
        self.asset = dataset["LV"]["ASSET"]
        self.asset_fwd = Forwards(dataset["ASSETS"][self.asset])
        self.spot = self.asset_fwd.forward(0)
        self.volfn = dataset["LV"]["VOL"]

        # Initialize rng and any arrays
        self.rng = Generator(SFC64(dataset["MC"]["SEED"]))
        self.x_vec = np.zeros(self.n)  # process x (log stock)
        self.dz_vec = np.empty(self.n, dtype=np.float64)
        self.tmp = np.empty(self.n, dtype=np.float64)

        self.cur_time = 0

    def advance(self, new_time):
        """Update x_vec in place when we move simulation by time dt."""

        dt = new_time - self.cur_time
        if dt < 1e-10:
            return
        fwd_rate = self.asset_fwd.rate(new_time, self.cur_time)
        if callable(self.volfn):
            vol = self.volfn((self.cur_time, self.x_vec))
        else:
            vol = self.volfn

        # # generate the random numbers and advance the log stock process
        self.rng.standard_normal(self.n, out=self.dz_vec)
        self.dz_vec *= sqrt(dt)
        self.dz_vec *= vol

        # add drift to x_vec: (fwd_rate - vol * vol / 2.0) * dt
        np.multiply(vol, vol, out=self.tmp)
        self.tmp *= -0.5 * dt
        self.tmp += fwd_rate * dt
        self.x_vec += self.tmp
        # add the random part to x_vec
        self.x_vec += self.dz_vec

        self.cur_time = new_time

    def get_value(self, unit):
        """Return the value of the modeled asset at the current time.
        otherwise return none."""

        if unit == self.asset:
            return self.spot * np.exp(self.x_vec)


class LVMCModel(MCModel):
    def state_class(self):
        return LVMCState
