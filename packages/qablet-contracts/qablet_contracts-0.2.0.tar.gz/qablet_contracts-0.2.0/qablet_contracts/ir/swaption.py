"""
This module contains examples of creating timetables for rate contracts such as swaps and swaptions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd

from qablet_contracts.ir.swap import simple_swap_period
from qablet_contracts.timetable import EventsMixin


@dataclass
class Swaption(EventsMixin):
    """A **Vanilla Swaption**.
    In a Vanilla swaption the holder gets the opportunity to enter into the swap at the beginning of the first period.

    Args:
        ccy: the currency of the swap.
        dates: the period datetimes of the underlying swap, including the inception and maturity.
        strike_rate: the strike rate of the swaption (in units, i.e. 0.02 means 200 bps).
        track: an optional identifier for the contract.

    Examples:
        >>> dates = pd.bdate_range(datetime(2023, 12, 31), datetime(2024, 12, 31), freq="2QE")
        >>> tt = Swap("USD", dates, strike_rate = 0.03).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op  quantity  unit
        0  .opt 2023-12-31 00:00:00+00:00  >     1.000  .swp
        1  .swp 2023-12-31 00:00:00+00:00  +     1.000   USD
        2  .swp 2024-06-30 00:00:00+00:00  +    -1.015   USD
        3  .swp 2024-06-30 00:00:00+00:00  +     1.000   USD
        4  .swp 2024-12-31 00:00:00+00:00  +    -1.015   USD
    """

    ccy: str
    dates: List[datetime]
    strike_rate: float
    track: str = ""

    def events(self):
        # option expiration event at beginning of the swap
        events = [
            {
                "track": self.track + ".opt",
                "time": self.dates[0],
                "op": ">",
                "quantity": 1,
                "unit": self.track + ".swp",
            }
        ]
        # payment events for the underlying swap
        for start, end in zip(self.dates[0:-1], self.dates[1:]):
            events.extend(
                simple_swap_period(
                    self.ccy, start, end, self.strike_rate, self.track + ".swp"
                )
            )

        return events


@dataclass
class BermudaSwaption(EventsMixin):
    """A **Co-terminal Bermuda Swaption**.
    In a Co-terminal Bermuda swaption, the holder can exercise his option at the beginning of each swap period.
    If exercised, the holder pays and receives all remaining payments of the swap. If not exercised, there are
    no payments in the next swap period. Irrespective of the time of exercise, the swap terminates at the same date.

    Args:
        ccy: the currency of the swap.
        dates: the period datetimes of the underlying swap, including the inception and maturity.
        strike_rate: the strike rate of the swaption (in units, i.e. 0.02 means 200 bps).
        track: an optional identifier for the contract.

    Examples:
        >>> dates = pd.bdate_range(datetime(2023, 12, 31), datetime(2024, 12, 31), freq="2QE")
        >>> tt = Swap("USD", dates, strike_rate = 0.03).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op  quantity  unit
        0  .opt 2023-12-31 00:00:00+00:00  >     1.000  .swp
        1  .swp 2023-12-31 00:00:00+00:00  +     1.000   USD
        2  .swp 2024-06-30 00:00:00+00:00  +    -1.015   USD
        3  .opt 2024-06-30 00:00:00+00:00  >     1.000  .swp
        4  .swp 2024-06-30 00:00:00+00:00  +     1.000   USD
        5  .swp 2024-12-31 00:00:00+00:00  +    -1.015   USD
    """

    ccy: str
    dates: List[datetime]
    strike_rate: float
    track: str = ""

    def events(self):
        events = []
        for start, end in zip(self.dates[0:-1], self.dates[1:]):
            # option expiration event before each period
            events.append(
                {
                    "track": self.track + ".opt",
                    "time": start,
                    "op": ">",
                    "quantity": 1,
                    "unit": self.track + ".swp",
                }
            )
            # payment event for the underlying swap
            events.extend(
                simple_swap_period(
                    self.ccy, start, end, self.strike_rate, self.track + ".swp"
                )
            )

        return events


if __name__ == "__main__":
    dates = pd.bdate_range(
        datetime(2023, 12, 31),
        datetime(2024, 12, 31),
        freq="2QE",
    )
    strike_rate = 0.03

    timetable = Swaption("USD", dates, strike_rate).timetable()
    print(timetable["events"].to_pandas())

    timetable = BermudaSwaption("USD", dates, strike_rate).timetable()
    print(timetable["events"].to_pandas())
