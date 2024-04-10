"""
Utils for creating barrier options timetable
"""

import numpy as np
import pyarrow as pa

from qablet_contracts.equity.vanilla import _option_events
from qablet_contracts.timetable import EVENT_SCHEMA


def ko_option_timetable(
    ccy: str,
    asset_name: str,
    strike: float,
    maturity: float,
    is_call: bool,
    barrier: float,
    barrier_type: str,
    barrier_pts: int,
    rebate: float = 0,
    track: str = "",
) -> dict:
    """Create timetable for a **Knock Out Option**.

    Args:
        ccy: the currency of the option.
        asset_name: the name of the underlying asset.
        strike: the option strike.
        maturity: the maturity of the option in years.
        is_call: true if the option is a call.
        barrier: the barrier level.
        barrier_type: the type of barrier option, e.g "Dn/Out" or "Up/Out".
        barrier_pts: the number of barrier observation points.
        rebate: the rebate amount.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = ko_option_timetable("USD", "EQ", 100, 0.2, True, 100, "Dn/Out", 5)
        >>> tt["events"].to_pandas()
          track  time  op  quantity unit
        0        0.00  KO       0.0  USD
        1        0.04  KO       0.0  USD
        2        0.08  KO       0.0  USD
        3        0.12  KO       0.0  USD
        4        0.16  KO       0.0  USD
        5        0.20  KO       0.0  USD
        6        0.20   >       0.0  USD
        7        0.20   +    -100.0  USD
        8        0.20   +       1.0   EQ
    """

    events = []
    for barrier_time in np.linspace(0, maturity, barrier_pts + 1):
        events.append(
            {
                "track": track,
                "time": barrier_time,
                "op": "KO",
                "quantity": rebate,
                "unit": ccy,
            }
        )

    vanilla_events = _option_events(
        ccy, asset_name, strike, maturity, is_call, track
    )

    events.extend(vanilla_events)

    # Define the knockout expression (KO)
    if barrier_type == "Dn/Out":

        def ko_fn(inputs):
            [S] = inputs
            return [S < barrier]
    elif barrier_type == "Up/Out":

        def ko_fn(inputs):
            [S] = inputs
            return [S > barrier]
    else:
        raise ValueError(f"Unknown barrier type: {barrier_type}")

    ko = {
        "type": "phrase",
        "inp": [asset_name],
        "fn": ko_fn,
    }

    events_table = pa.RecordBatch.from_pylist(events, schema=EVENT_SCHEMA)
    return {"events": events_table, "expressions": {"KO": ko}}


if __name__ == "__main__":
    # Create the option
    timetable = ko_option_timetable(
        "USD", "EQ", 100, 0.2, True, 100, "Dn/Out", 5
    )
    print(timetable["events"].to_pandas())
