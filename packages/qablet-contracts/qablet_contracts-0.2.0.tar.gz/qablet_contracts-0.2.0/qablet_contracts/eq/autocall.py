"""
Create an autocallable note timetable
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

from qablet_contracts.ir.dcf import dcf_30_360 as dcf
from qablet_contracts.timetable import EventsMixin


@dataclass
class AutoCallable(EventsMixin):
    """An **Autocallable Note**.

    Args:
        ccy: the currency of the option.
        asset_name: the name of the underlying asset.
        initial_spot: the initial spot price of the asset.
        strike: downside participation below this strike.
        maturity: the maturity of the option in years.
        barrier: the note is called above this barrier level.
        barrier_dates: the barrier observation points.
        cpn_rate: the coupon rate.
        track: an optional identifier for the contract.

    Examples:
        >>> start = datetime(2024, 3, 31)
        >>> maturity = datetime(2024, 9, 30)
        >>> barrier_dates = pd.date_range(start, maturity, freq="ME", inclusive="right")
        >>> tt = AutoCallable(
            "USD", "AAPL", 100, 80, start, maturity, 102, barrier_dates, 0.092
        ).timetable()
        >>> print(tt["events"].to_pandas())
          track                      time    op    quantity    unit
        0       2024-04-30 00:00:00+00:00  CALL  100.769613     USD
        1       2024-05-31 00:00:00+00:00  CALL  101.545149     USD
        2       2024-06-30 00:00:00+00:00  CALL  102.326654     USD
        3       2024-07-31 00:00:00+00:00  CALL  103.114173     USD
        4       2024-08-31 00:00:00+00:00  CALL  103.907753     USD
        5       2024-09-30 00:00:00+00:00  CALL  104.707441     USD
        6       2024-09-30 00:00:00+00:00     +    1.000000  PAYOFF
    """

    ccy: str
    asset_name: str
    initial_spot: float
    strike: float
    accrual_start: datetime
    maturity: datetime
    barrier: float
    barrier_dates: List[datetime]
    cpn_rate: float
    track: str = ""

    def events(self):
        events = []
        # Autocall events
        for barrier_date in self.barrier_dates:
            # daycount_fraction
            frac = dcf(barrier_date, self.accrual_start)
            events.append(
                {
                    "track": self.track,
                    "time": barrier_date,
                    "op": "CALL",
                    "quantity": 100 * np.exp(frac * self.cpn_rate),
                    "unit": self.ccy,
                }
            )

        # payoff at maturity
        events.append(
            {
                "track": "",
                "time": self.maturity,
                "op": "+",
                "quantity": 1.0,
                "unit": "PAYOFF",
            }
        )
        return events

    def expressions(self):
        # Define the autocall condition
        def ko_fn(inputs):
            [S] = inputs
            return [S > (self.barrier * self.initial_spot / 100)]

        call = {
            "type": "phrase",
            "inp": [self.asset_name],
            "fn": ko_fn,
        }

        # Define the final payoff
        fixed_pay = 100 * np.exp(
            dcf(self.maturity, self.accrual_start) * self.cpn_rate
        )

        def payoff_fn(inputs):
            [s] = inputs
            eq_pay = s * (100 / self.initial_spot)
            return [np.where(eq_pay < self.strike, eq_pay, fixed_pay)]

        payoff = {
            "type": "phrase",
            "inp": [self.asset_name],
            "fn": payoff_fn,
        }

        return {"PAYOFF": payoff, "CALL": call}


if __name__ == "__main__":
    # Create the option
    start = datetime(2024, 3, 31)
    maturity = datetime(2024, 9, 30)
    barrier_dates = pd.date_range(
        start, maturity, freq="ME", inclusive="right"
    )
    timetable = AutoCallable(
        "USD", "AAPL", 100, 80, start, maturity, 102, barrier_dates, 0.092
    ).timetable()
    print(timetable["events"].to_pandas())
