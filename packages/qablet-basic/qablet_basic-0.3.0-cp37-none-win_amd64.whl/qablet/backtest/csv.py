# Define class for Backtesting
from qablet.base.base import ModelStateBase

from .._qablet import backtest_csv


class BackTest:
    def backtest_cf(self, timetable, filename, base):
        model_state = ModelStateBase(None, None)
        backtest_csv(
            timetable["events"],
            model_state,
            filename,
            base,
            timetable["expressions"],
        )

        return model_state.stats["CASHFLOW"]
