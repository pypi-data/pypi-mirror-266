# Generic MC model

from abc import abstractmethod

from .._qablet import mc_price
from .base import Model, ModelStateBase


# Define Base Class for State Object for MC Models
# Todo add the abstract methods and what else is expected from this class.
class MCStateBase(ModelStateBase):
    """Class to maintain the state of a single asset MC process."""

    def get_value(self, unit):
        """Return the value of the asset at the current time,
        if this asset is handled by the model, otherwise return None."""
        return None

    @abstractmethod
    def advance(self, new_time: float):
        ...


# Define Base Class for MC Models
class MCModel(Model):
    """Abstract base class for all Monte Carlo models where the stochastic model
    is implemented in the python class."""

    def price_method(self):
        return mc_price
