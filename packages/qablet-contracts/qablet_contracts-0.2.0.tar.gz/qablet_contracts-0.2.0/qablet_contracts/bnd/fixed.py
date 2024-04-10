"""
This module contains examples of creating timetables for Fixed Rate Bonds.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
import pyarrow as pa

from qablet_contracts.ir.dcf import dcf_30_360 as dcf
from qablet_contracts.timetable import TS_EVENT_SCHEMA


def _const_dict_array(n, val):
    """Create a dictionary array of length n with constant values."""
    return pa.DictionaryArray.from_arrays(
        indices=np.full(n, 0, dtype=np.int64),
        dictionary=[val],
    )


@dataclass
class FixedCashFlows:
    """Create timetable from cashflows in a single currency. This example also shows how to create a timetable from arrays
    instead of a list of dictionaries, which is more efficient.

    Args:
        ccy: the currency of cashflows.
        times: a list or ndarray of cashflows times.
        amounts: a list ndarray of cashflows amounts.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = FixedCashFlows(
            "USD",
            [
                datetime(2023, 12, 31),
                datetime(2024, 6, 30),
                datetime(2024, 12, 31),
            ],
            [0.05, 0.05, 1.05],
        ).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op  quantity unit
        0       2023-12-31 00:00:00+00:00  +      0.05  USD
        1       2024-06-30 00:00:00+00:00  +      0.05  USD
        2       2024-12-31 00:00:00+00:00  +      1.05  USD
    """

    ccy: str
    dates: List[datetime]
    amounts: List[float]
    track: str = ""

    def timetable(self):
        n = len(self.dates)
        return {
            "events": pa.RecordBatch.from_arrays(
                [
                    _const_dict_array(n, self.track),  # tracks
                    pa.array(self.dates),
                    _const_dict_array(n, "+"),  # ops
                    pa.array(self.amounts),
                    _const_dict_array(n, self.ccy),  # units
                ],
                schema=TS_EVENT_SCHEMA,
            ),
            "expressions": {},
        }


@dataclass
class FixedBond:
    """Create timetable for a fixed rate bond.

    Args:
        ccy: the currency of cashflows.
        coupon: the coupon rate per year.
        maturity: the maturity of the bond.
        freq: the number of coupon payments per year.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = FixedBond(
            "USD", 0.05, datetime(2023, 12, 31), datetime(2025, 12, 31), "2QE"
        ).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time op  quantity unit
        0       2024-06-30 00:00:00+00:00  +     0.025  USD
        1       2024-12-31 00:00:00+00:00  +     0.050  USD
        2       2025-06-30 00:00:00+00:00  +     0.075  USD
        3       2025-12-31 00:00:00+00:00  +     1.100  USD
    """

    ccy: str
    coupon: float
    accrual_start: datetime
    maturity: datetime
    freq: str = "2BQE"
    track: str = ""

    def timetable(self):
        cpn_dates = pd.bdate_range(
            self.accrual_start,
            self.maturity,
            freq=self.freq,
            inclusive="right",
        )

        amounts = [
            dcf(dt, self.accrual_start) * self.coupon for dt in cpn_dates
        ]

        amounts[-1] += 1  # The last payment includes the principal
        return FixedCashFlows(
            self.ccy, cpn_dates, amounts, self.track
        ).timetable()


if __name__ == "__main__":
    # Create a timetable from cashflows
    timetable = FixedCashFlows(
        "USD",
        [
            datetime(2023, 12, 31),
            datetime(2024, 6, 30),
            datetime(2024, 12, 31),
        ],
        [0.05, 0.05, 1.05],
    ).timetable()
    print("cf:\n", timetable["events"].to_pandas())

    # Create a fixed bond timetable
    timetable = FixedBond(
        "USD", 0.05, datetime(2023, 12, 31), datetime(2025, 12, 31), "2QE"
    ).timetable()
    print("bond:\n", timetable["events"].to_pandas())
