# Black Scholes model using finite difference method


from qablet.base.base import Model, ModelStateBase

from .._qablet import fd_blackscholes_price


# Define the Model Class
class BSFDModel(Model):
    __PARAM_SCHEMA_NAME__ = "BS"

    def state_class(self):
        return ModelStateBase

    def price_method(self):
        return fd_blackscholes_price
