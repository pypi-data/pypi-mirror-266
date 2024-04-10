"""
Create an autocallable note timetable
"""

import numpy as np
import pyarrow as pa

from qablet_contracts.timetable import EVENT_SCHEMA


def autocallable_timetable(
    ccy: str,
    asset_name: str,
    initial_spot: float,
    strike: float,
    maturity: float,
    barrier: float,
    barrier_pts: int,
    cpn_rate: float,
    track: str = "",
) -> dict:
    """Create timetable for an **Autocallable Note**.

    Args:
        ccy: the currency of the option.
        asset_name: the name of the underlying asset.
        initial_spot: the initial spot price of the asset.
        strike: downside participation below this strike.
        maturity: the maturity of the option in years.
        barrier: the note is called above this barrier level.
        barrier_pts: the number of barrier observation points. If 0, then the note is not autocallable.
        cpn_rate: the coupon rate.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = autocallable_timetable("USD", "AAPL", 100, 80, 1, 102, 4, 0.092)
        >>> tt["events"].to_pandas()
          track  time    op    quantity     unit
        0        0.25  CALL  102.326654      USD
        1        0.50  CALL  104.707441      USD
        2        0.75  CALL  107.143621      USD
        3        1.00  CALL  109.636482      USD
        4        1.00     +    1.000000   PAYOFF
    """

    events_list = []
    # Autocall events
    if barrier_pts:
        for barrier_time in np.linspace(0, maturity, barrier_pts + 1)[1:]:
            events_list.append(
                {
                    "track": track,
                    "time": barrier_time,
                    "op": "CALL",
                    "quantity": 100 * np.exp(barrier_time * cpn_rate),
                    "unit": ccy,
                }
            )

    # payoff at maturity
    events_list.append(
        {
            "track": "",
            "time": maturity,
            "op": "+",
            "quantity": 1.0,
            "unit": "PAYOFF",
        }
    )

    # Define the autocall condition
    def ko_fn(inputs):
        [S] = inputs
        return [S > (barrier * initial_spot / 100)]

    call = {
        "type": "phrase",
        "inp": [asset_name],
        "fn": ko_fn,
    }

    # Define the final payoff
    fixed_pay = 100 * np.exp(maturity * cpn_rate)

    def payoff_fn(inputs):
        [s] = inputs
        eq_pay = s * (100 / initial_spot)
        return [np.where(eq_pay < strike, eq_pay, fixed_pay)]

    calcpay = {
        "type": "phrase",
        "inp": [asset_name],
        "fn": payoff_fn,
    }

    events_table = pa.RecordBatch.from_pylist(events_list, schema=EVENT_SCHEMA)
    return {
        "events": events_table,
        "expressions": {"PAYOFF": calcpay, "CALL": call},
    }


if __name__ == "__main__":
    # Create the option
    timetable = autocallable_timetable(
        "USD", "AAPL", 100, 80, 1, 102, 4, 0.092
    )
    print(timetable["events"].to_pandas())
