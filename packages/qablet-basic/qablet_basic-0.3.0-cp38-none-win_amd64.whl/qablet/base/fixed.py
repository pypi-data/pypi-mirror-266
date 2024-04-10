# Define the fixed model

from .._qablet import fixed_price
from .base import Model, ModelStateBase


# Define a determinitic Model that just uses forwards
class FixedModel(Model):
    def state_class(self):
        return ModelStateBase

    def price_method(self):
        return fixed_price
