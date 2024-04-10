"""
This module contains examples of creating timetables for equity rainbow options.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from qablet_contracts.timetable import EventsMixin


@dataclass
class Rainbow(EventsMixin):
    """Create timetable for an **Equity Rainbow Option**.

    Args:
        ccy: the currency of the option.
        asset_names: the name of the underlying assets.
        strikes: the option strikes.
        notional: the notional of the option.
        maturity: the maturity of the option.
        is_call: true if the option is a call.
        track: an optional identifier for the contract.

    Examples:
        >>> assets = ["SPX", "FTSE", "N225"]
        >>> strikes = [5087, 7684, 39100]
        >>> tt = Rainbow("USD", assets, strikes, 100_000, datetime(2024, 3, 31), True).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op       quantity  unit
        0       2024-03-31 00:00:00+00:00  + -100000.000000   USD
        1       2024-03-31 00:00:00+00:00  >      19.657952   SPX
        2       2024-03-31 00:00:00+00:00  >      13.014055  FTSE
        3       2024-03-31 00:00:00+00:00  >       2.557545  N225
        4       2024-03-31 00:00:00+00:00  +  100000.000000   USD
    """

    ccy: str
    asset_names: List[str]
    strikes: List[float]
    notional: float
    maturity: datetime
    is_call: bool
    track: str = ""

    def events(self):
        sign = 1 if self.is_call else -1
        # Pay the initial strike
        events = [
            {
                "track": "",
                "time": self.maturity,
                "op": "+",
                "quantity": -self.notional * sign,
                "unit": self.ccy,
            },
        ]

        # Options to receive any of the assets
        for asset, strike in zip(self.asset_names, self.strikes):
            events.append(
                {
                    "track": "",
                    "time": self.maturity,
                    "op": ">",
                    "quantity": self.notional / strike * sign,
                    "unit": asset,
                }
            )

        # Otherwise receive the notional back
        events.append(
            {
                "track": "",
                "time": self.maturity,
                "op": "+",
                "quantity": self.notional * sign,
                "unit": self.ccy,
            }
        )
        return events


if __name__ == "__main__":
    # Create the rainbow option
    timetable = Rainbow(
        "USD",
        ["SPX", "FTSE", "N225"],
        [5087, 7684, 39100],
        100_000,
        datetime(2024, 3, 31),
        True,
    ).timetable()

    print(timetable["events"].to_pandas())
