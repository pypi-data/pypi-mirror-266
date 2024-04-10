"""
This module contains examples of creating timetables for equity cliquet contracts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

from qablet_contracts.timetable import EventsMixin


@dataclass
class Accumulator(EventsMixin):
    """An **Accumulator Cliquet**.

    Args:
        ccy: the currency of the bond.
        asset_name: the name of the underlying asset.
        fix_dates: the fixing times of the cliquet.
        global_floor: the global floor of the cliquet.
        local_floor: the local floor of the cliquet.
        local_cap: the local cap of the cliquet.
        track: an optional identifier for the contract.

    Examples:
        >>> fix_dates = pd.bdate_range(datetime(2021, 12, 31), datetime(2024, 12, 31), freq="2BQE")
        >>> tt = Accumulator("USD", "SPX", fix_dates, 0.0, -0.03, 0.05).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time   op  quantity     unit
        0   NaN 2021-12-31 00:00:00+00:00  NaN       0.0     INIT
        1   NaN 2022-06-30 00:00:00+00:00  NaN       0.0  CALCFIX
        2   NaN 2022-12-30 00:00:00+00:00  NaN       0.0  CALCFIX
        3   NaN 2023-06-30 00:00:00+00:00  NaN       0.0  CALCFIX
        4   NaN 2023-12-29 00:00:00+00:00  NaN       0.0  CALCFIX
        5   NaN 2024-06-28 00:00:00+00:00  NaN       0.0  CALCFIX
        6   NaN 2024-12-31 00:00:00+00:00  NaN       0.0  CALCFIX
        7       2024-12-31 00:00:00+00:00    >       0.0      USD
        8       2024-12-31 00:00:00+00:00    +       1.0      ACC
    """

    ccy: str
    asset_name: str
    fix_dates: List[datetime]
    global_floor: float
    local_floor: float
    local_cap: float
    track: str = ""
    state: dict = field(default_factory=dict)

    def events(self):
        maturity = self.fix_dates[-1]

        events = [
            {
                "track": None,
                "time": self.fix_dates[0],
                "op": None,
                "quantity": 0,
                "unit": "INIT",  # initialize accumulator
            }
        ]
        for fixing_time in self.fix_dates[1:]:
            events.append(
                {
                    "track": None,
                    "time": fixing_time,
                    "op": None,
                    "quantity": 0,
                    "unit": "CALCFIX",  # update accumulator
                }
            )
        events.append(
            {
                "track": self.track,
                "time": maturity,
                "op": ">",  # global floor
                "quantity": self.global_floor,
                "unit": self.ccy,
            }
        )
        events.append(
            {
                "track": self.track,
                "time": maturity,
                "op": "+",  # pay the accumulated amount
                "quantity": 1,
                "unit": "ACC",
            }
        )
        return events

    def expressions(self):
        last_acc = self.state.get("ACC", 0.0)

        if "S_PREV" in self.state:

            def accumulator_init_fn(inputs):
                [s] = inputs
                return [last_acc, self.state["S_PREV"]]  # [ACC, S_PREV]
        else:

            def accumulator_init_fn(inputs):
                [s] = inputs
                return [last_acc, s]  # [ACC, S_PREV]

        def accumulator_update_fn(inputs):
            [s, s_prev, a] = inputs

            ret = s / s_prev - 1.0  # ret = S / S_PREV - 1
            ret = np.maximum(self.local_floor, ret)
            ret = np.minimum(self.local_cap, ret)

            return [a + ret, s]  # [ACC, S_PREV]

        return {
            "INIT": {
                "type": "snapper",
                "inp": [self.asset_name],
                "fn": accumulator_init_fn,
                "out": ["ACC", "S_PREV"],
            },
            "CALCFIX": {
                "type": "snapper",
                "inp": [self.asset_name, "S_PREV", "ACC"],
                "fn": accumulator_update_fn,
                "out": ["ACC", "S_PREV"],
            },
        }


if __name__ == "__main__":
    # Create the cliquet
    fix_dates = pd.bdate_range(
        datetime(2021, 12, 31), datetime(2024, 12, 31), freq="2BQE"
    )

    global_floor = 0.0
    local_floor = -0.03
    local_cap = 0.05
    timetable = Accumulator(
        "USD",
        "SPX",
        fix_dates,
        global_floor,
        local_floor,
        local_cap,
        state={"S_PREV": 1.0},
    ).timetable()

    print(timetable["events"].to_pandas())
