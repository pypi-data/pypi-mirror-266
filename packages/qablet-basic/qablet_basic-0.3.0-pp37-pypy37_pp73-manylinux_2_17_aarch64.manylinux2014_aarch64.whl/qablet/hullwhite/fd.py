# Hullwhite model using finite difference method


from qablet.base.base import Model, ModelStateBase

from .._qablet import fd_hullwhite_price


# Define the Model Class
class HWFDModel(Model):
    __PARAM_SCHEMA_NAME__ = "HW"

    def state_class(self):
        return ModelStateBase

    def price_method(self):
        return fd_hullwhite_price
