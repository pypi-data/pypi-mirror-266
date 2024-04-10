"""
This module contains examples of creating timetables for Zero Coupon Bond and related contracts.
"""

from dataclasses import dataclass
from datetime import datetime

from qablet_contracts.timetable import EventsMixin


@dataclass
class Bond(EventsMixin):
    """A zero coupon bond.

    Args:
        ccy: the currency of the bond.
        maturity: the maturity of the bond in years.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = Bond("USD", datetime(2025, 3, 31)).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op  quantity unit
        0       2025-03-31 00:00:00+00:00  +       1.0  USD
    """

    ccy: str
    maturity: datetime
    track: str = ""

    def events(self):
        return [
            {
                "track": self.track,
                "time": self.maturity,
                "op": "+",
                "quantity": 1,
                "unit": self.ccy,
            }
        ]


@dataclass
class BondPut(EventsMixin):
    """Create timetable for a **zero coupon bond put**.

    Args:
        ccy: the currency of the bond.
        opt_maturity: the maturity of the option in years.
        bond_maturity: the maturity of the option in years.
        strike: the option strike.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = BondPut(
            "USD", datetime(2024, 9, 30), datetime(2025, 3, 31), 0.95
        ).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op  quantity unit
        0       2024-09-30 00:00:00+00:00  >      0.00  USD
        1       2024-09-30 00:00:00+00:00  +      0.95  USD
        2       2025-03-31 00:00:00+00:00  +     -1.00  USD
    """

    ccy: str
    opt_maturity: datetime
    bond_maturity: datetime
    strike: float
    track: str = ""

    def events(self):
        return [
            {
                "track": self.track,
                "time": self.opt_maturity,
                "op": ">",
                "quantity": 0,
                "unit": self.ccy,
            },  # Choose greater of nothing (get 0) or exercise (continue to remaining events)
            {
                "track": self.track,
                "time": self.opt_maturity,
                "op": "+",
                "quantity": self.strike,
                "unit": self.ccy,
            },  # get strike at expiration
            {
                "track": self.track,
                "time": self.bond_maturity,
                "op": "+",
                "quantity": -1,
                "unit": self.ccy,
            },  # pay bond notional at bond expiration
        ]


if __name__ == "__main__":
    # Create a zero coupon bond timetable
    timetable = Bond("USD", datetime(2025, 3, 31)).timetable()
    print("zcb:\n", timetable["events"].to_pandas())

    timetable = BondPut(
        "USD", datetime(2024, 9, 30), datetime(2025, 3, 31), 0.95
    ).timetable()
    print("zbp:\n", timetable["events"].to_pandas())
