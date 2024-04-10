# Monte Carlo Pricer for Heston Model

from math import sqrt

import numpy as np
from numpy.random import SFC64, Generator

from qablet.base.mc import MCModel, MCStateBase
from qablet.base.utils import Forwards


# Define a class for the state of a single asset Heston MC process
class HestonStateMC(MCStateBase):
    def __init__(self, timetable, dataset):
        super().__init__(timetable, dataset)

        self.shape = dataset["MC"]["PATHS"]
        assert self.shape % 2 == 0, "Number of paths must be even"
        self.n = self.shape >> 1  # divide by 2

        # create a random number generator
        self.rng = Generator(SFC64(dataset["MC"]["SEED"]))

        self.asset = dataset["HESTON"]["ASSET"]
        self.asset_fwd = Forwards(dataset["ASSETS"][self.asset])
        self.spot = self.asset_fwd.forward(0)

        self.heston_params = (
            dataset["HESTON"]["LONG_VAR"],
            dataset["HESTON"]["VOL_OF_VAR"],
            dataset["HESTON"]["MEANREV"],
            dataset["HESTON"]["CORRELATION"],
        )

        # Initialize the arrays
        self.x_vec = np.zeros(self.shape)  # processes x (log stock)
        self.v_vec = np.full(
            self.shape, dataset["HESTON"]["INITIAL_VAR"]
        )  # processes v (variance)

        # We will reduce time spent in memory allocation by creating arrays in advance
        # and reusing them in the `advance` function which is called repeatedly.
        # though the values from one timestep are not reused in the next.
        self.tmp_vec = np.empty(self.shape, dtype=np.float64)
        self.dz1_vec = np.empty(self.shape, dtype=np.float64)
        self.dz2_vec = np.empty(self.shape, dtype=np.float64)
        self.vol_vec = np.empty(self.shape, dtype=np.float64)
        self.sv_vec = np.empty(self.shape, dtype=np.float64)
        self.cur_time = 0

    def advance(self, new_time):
        """Update x_vec, v_vec in place when we move simulation by time dt."""
        dt = new_time - self.cur_time
        if dt < 1e-10:
            return

        (
            theta,
            vol_of_variance,
            mean_reversion_speed,
            correlation,
        ) = self.heston_params
        fwd_rate = self.asset_fwd.rate(new_time, self.cur_time)

        sqrtdt = sqrt(dt)
        n = self.n

        # To improve preformance we will break up the operations into np.multiply,
        # np.add, etc. and use the `out` parameter to avoid creating temporary arrays.

        # generate the random numbers
        # we calculate dz1 = normal(0,1) * sqrtdt
        self.rng.standard_normal(
            n, out=self.dz1_vec[0:n]
        )  # not much difference using out= or not
        np.multiply(sqrtdt, self.dz1_vec[0:n], out=self.dz1_vec[0:n])
        np.negative(
            self.dz1_vec[0:n], out=self.dz1_vec[n:]
        )  # antithetic variates

        # we calculate dz2 = normal(0,1) * sqrtdt * sqrt(1 - correlation * correlation) + correlation * dz1
        self.rng.standard_normal(n, out=self.dz2_vec[0:n])
        np.multiply(
            sqrtdt * sqrt(1 - correlation * correlation),
            self.dz2_vec[0:n],
            out=self.dz2_vec[0:n],
        )
        np.negative(
            self.dz2_vec[0:n], out=self.dz2_vec[n:]
        )  # antithetic variates
        np.multiply(correlation, self.dz1_vec, out=self.tmp_vec)  # second term
        np.add(self.dz2_vec, self.tmp_vec, out=self.dz2_vec)

        # vol = sqrt(max(v, 0))
        np.maximum(0.0, self.v_vec, out=self.vol_vec)
        np.sqrt(self.vol_vec, out=self.vol_vec)

        # update the current value of x (log Stock process)
        # first term: x += (fwd_rate - vol * vol / 2.) * dt
        np.multiply(self.vol_vec, self.vol_vec, out=self.tmp_vec)
        np.divide(self.tmp_vec, 2, out=self.tmp_vec)
        np.subtract(fwd_rate, self.tmp_vec, out=self.tmp_vec)
        np.multiply(self.tmp_vec, dt, out=self.tmp_vec)
        np.add(self.x_vec, self.tmp_vec, out=self.x_vec)

        # second term: x += vol * dz1
        np.multiply(self.vol_vec, self.dz1_vec, out=self.tmp_vec)
        np.add(self.x_vec, self.tmp_vec, out=self.x_vec)

        # update the current value of v (variance process)
        # first term: v += mean_reversion_speed * (theta - v) * dt
        np.subtract(theta, self.v_vec, out=self.tmp_vec)
        np.multiply(
            self.tmp_vec, (mean_reversion_speed * dt), out=self.tmp_vec
        )
        np.add(self.v_vec, self.tmp_vec, out=self.v_vec)

        # second term: v += vol_of_variance * vol * dz2
        np.multiply(vol_of_variance, self.vol_vec, out=self.tmp_vec)
        np.multiply(self.tmp_vec, self.dz2_vec, out=self.tmp_vec)
        np.add(self.v_vec, self.tmp_vec, out=self.v_vec)

        # Millstein correction
        # third term: v += 0.25 * vol_of_variance * vol_of_variance * (dz2 ** 2 - dt)
        np.multiply(self.dz2_vec, self.dz2_vec, out=self.tmp_vec)
        np.subtract(self.tmp_vec, dt, out=self.tmp_vec)
        np.multiply(
            0.25 * vol_of_variance * vol_of_variance,
            self.tmp_vec,
            out=self.tmp_vec,
        )
        np.add(self.v_vec, self.tmp_vec, out=self.v_vec)

        self.cur_time = new_time

    def get_value(self, unit):
        """Return the value of the unit at the current time."""
        if unit == self.asset:
            return self.spot * np.exp(self.x_vec)
        else:
            return None


class HestonMCModel(MCModel):
    def state_class(self):
        return HestonStateMC
