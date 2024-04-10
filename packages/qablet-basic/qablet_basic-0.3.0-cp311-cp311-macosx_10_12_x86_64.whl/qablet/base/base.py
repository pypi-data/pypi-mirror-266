# Define Base Class for Models
from abc import ABC, abstractmethod
from datetime import datetime

import pyarrow as pa
from qablet_contracts.timetable import TS_EVENT_SCHEMA, py_to_ts


def convert_time_to_ts(timetable, base_ts):
    """Convert events of timetable in place, changing time column into timestamp column.
    This function is used convert timetables created by legacy methods that use floating point
    for time into timetables with timestamp for time."""
    events = timetable["events"]

    if events["time"].type == pa.float64():
        ts_list = [
            base_ts + t.as_py() * 31_536_000_000 for t in events["time"]
        ]

        timetable["events"] = pa.RecordBatch.from_arrays(
            [
                events["track"],
                ts_list,
                events["op"],
                events["quantity"],
                events["unit"],
            ],
            schema=TS_EVENT_SCHEMA,
        )


# Define Base Class for State Object for all Models
class ModelStateBase(ABC):
    """Class to maintain the state during a model execution."""

    def __init__(self, timetable, dataset):
        self.stats = {}

    def set_stat(self, key: str, val):
        self.stats[key] = val


class Model(ABC):
    """Base class for all models."""

    @abstractmethod
    def state_class(self):
        """The class that maintains state for this model."""
        ...

    @abstractmethod
    def price_method(self):
        """The method that calculates price."""
        ...

    def price(self, timetable, dataset):
        """Calculate price of contract.

        Parameters:
            timetable (dict): timetable for the contract.
            dataset (dict): dataset for the model.

        Returns:
            price (float): price of contract
            stats (dict): stats such as standard error

        """

        if "PRICING_TS" not in dataset:
            dataset["PRICING_TS"] = py_to_ts(datetime(2023, 12, 31)).value
        convert_time_to_ts(timetable, dataset["PRICING_TS"])

        model_state = (self.state_class())(timetable, dataset)
        price = self.price_method()(
            timetable["events"], model_state, dataset, timetable["expressions"]
        )

        return price, model_state.stats
