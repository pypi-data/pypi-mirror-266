"""
This module contains examples of creating timetables for equity vanilla options.
"""

from dataclasses import dataclass
from datetime import datetime

from qablet_contracts.timetable import EventsMixin


@dataclass
class Option(EventsMixin):
    """An **Equity Vanilla Option**.

    Args:
        ccy: the currency of the option.
        asset_name: the name of the underlying asset.
        strike: the option strike.
        maturity: the maturity of the option in years.
        is_call: true if the option is a call.
        track: an optional identifier for the contract.

    Examples:
        >>> call = Option("USD", "SPX", 2900, datetime(2024, 3, 31), True, "<SPX2900>")
        >>> call.timetable()["events"].to_pandas()
          track  time op  quantity  unit
               track                      time op  quantity unit
        0  <SPX2900> 2024-03-31 00:00:00+00:00  >       0.0  USD
        1  <SPX2900> 2024-03-31 00:00:00+00:00  +   -2900.0  USD
        2  <SPX2900> 2024-03-31 00:00:00+00:00  +       1.0  SPX

        >>> put = Option("USD", "SPX", 2900, datetime(2024, 3, 31), False, "<SPX2900>")
        >>> put.timetable()["events"].to_pandas()
          track  time op  quantity  unit
               track                      time op  quantity unit
        0  <SPX2900> 2024-03-31 00:00:00+00:00  >       0.0  USD
        1  <SPX2900> 2024-03-31 00:00:00+00:00  +    2900.0  USD
        2  <SPX2900> 2024-03-31 00:00:00+00:00  +      -1.0  SPX
    """

    ccy: str
    asset_name: str
    strike: float
    maturity: datetime
    is_call: bool
    track: str = ""

    def events(self):
        sign = 1 if self.is_call else -1
        return [
            {
                "track": self.track,
                "time": self.maturity,
                "op": ">",
                "quantity": 0,
                "unit": self.ccy,
            },
            {
                "track": self.track,
                "time": self.maturity,
                "op": "+",
                "quantity": -self.strike * sign,
                "unit": self.ccy,
            },
            {
                "track": self.track,
                "time": self.maturity,
                "op": "+",
                "quantity": sign,
                "unit": self.asset_name,
            },
        ]


if __name__ == "__main__":
    # Create the option timetable
    timetable = Option(
        "USD", "SPX", 2900, datetime(2024, 3, 31), True, "<SPX2900>"
    ).timetable()

    print(timetable["events"].to_pandas())
