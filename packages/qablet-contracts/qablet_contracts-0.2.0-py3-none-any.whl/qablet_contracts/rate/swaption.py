"""
This module contains examples of creating timetables for rate contracts such as swaps and swaptions.
"""

from typing import Dict, List

import numpy as np

from qablet_contracts.timetable import timetable_from_dicts


def simple_swap_period(
    ccy: str, start: float, end: float, fixed_rate: float, track: str = ""
) -> list:
    """Simple representation of a swap period, paying fixed, receiving floating rate.

    Args:
        ccy: the currency of the swap.
        start: the start of the period in years.
        end: the end of the period in years.
        fixed_rate: the fixed annual rate of the swap.
        track: an optional identifier for the contract.
    """
    return [
        {
            "track": track,
            "time": start,
            "op": "+",
            "quantity": 1,
            "unit": ccy,
        },
        {
            "track": track,
            "time": end,
            "op": "+",
            "quantity": -1 - fixed_rate * (end - start),
            "unit": ccy,
        },
    ]


def swap_timetable(
    ccy: str, times: List[float], strike_rate: float, track: str = ""
) -> Dict:
    """Create timetable for a **Vanilla Swap**.

    Args:
        ccy: the currency of the swap.
        times: the period times of the swap, including the inception and maturity.
        strike_rate: the strike rate of the swaption (in units, i.e. 0.02 means 200 bps).
        track: an optional identifier for the contract.

    Examples:
        >>> tt = swap_timetable("USD", [0.5, 1.0, 1.5], 0.05)
        >>> tt["events"].to_pandas()
          track  time op  quantity  unit
        1  .swp   0.5  +     1.000   USD
        2  .swp   1.0  +    -1.025   USD
        3  .swp   1.0  +     1.000   USD
        4  .swp   1.5  +    -1.025   USD
    """
    events = []
    # payment events
    for start, end in zip(times[0:-1], times[1:]):
        events.extend(
            simple_swap_period(ccy, start, end, strike_rate, track + ".swp")
        )

    return timetable_from_dicts(events)


def swaption_timetable(
    ccy: str, times: List[float], strike_rate: float, track: str = ""
) -> Dict:
    """Create timetable for a **Vanilla Swaption**.
    In a Vanilla swaption the holder gets the opportunity to enter into the swap at the beginning of the first period.

    Args:
        ccy: the currency of the swap.
        times: the period times of the underlying swap, including the inception and maturity.
        strike_rate: the strike rate of the swaption (in units, i.e. 0.02 means 200 bps).
        track: an optional identifier for the contract.

    Examples:
        >>> tt = swaption_timetable("USD", [0.5, 1.0, 1.5], 0.05)
        >>> tt["events"].to_pandas()
          track  time op  quantity  unit
        0  .opt   0.5  >     1.000  .swp
        1  .swp   0.5  +     1.000   USD
        2  .swp   1.0  +    -1.025   USD
        3  .swp   1.0  +     1.000   USD
        4  .swp   1.5  +    -1.025   USD
    """

    # option expiration event at beginning of the swap
    events = [
        {
            "track": track + ".opt",
            "time": times[0],
            "op": ">",
            "quantity": 1,
            "unit": track + ".swp",
        }
    ]
    # payment events for the underlying swap
    for start, end in zip(times[0:-1], times[1:]):
        events.extend(
            simple_swap_period(ccy, start, end, strike_rate, track + ".swp")
        )

    return timetable_from_dicts(events)


def bermuda_swaption_timetable(
    ccy: str, times: List[float], strike_rate: float, track: str = ""
) -> Dict:
    """Create timetable for a **Co-terminal Bermuda Swaption**.
    In a Co-terminal Bermuda swaption, the holder can exercise his option at the beginning of each swap period.
    If exercised, the holder pays and receives all remaining payments of the swap. If not exercised, there are
    no payments in the next swap period. Irrespective of the time of exercise, the swap terminates at the same date.


    Args:
        ccy: the currency of the swap.
        times: the period times of the underlying swap, including the inception and maturity.
        strike_rate: the strike rate of the swaption (in units, i.e. 0.02 means 200 bps).
        track: an optional identifier for the contract.

    Examples:
        >>> tt = bermuda_swaption_timetable("USD", [0.5, 1.0, 1.5], 0.05)
        >>> tt["events"].to_pandas()
          track  time op  quantity  unit
        0  .opt   0.5  >     1.000  .swp
        1  .swp   0.5  +     1.000   USD
        2  .swp   1.0  +    -1.025   USD
        3  .opt   1.0  >     1.000  .swp
        4  .swp   1.0  +     1.000   USD
        5  .swp   1.5  +    -1.025   USD
    """

    events = []
    for start, end in zip(times[0:-1], times[1:]):
        # option expiration event before each period
        events.append(
            {
                "track": track + ".opt",
                "time": start,
                "op": ">",
                "quantity": 1,
                "unit": track + ".swp",
            }
        )
        # payment event for the underlying swap
        events.extend(
            simple_swap_period(ccy, start, end, strike_rate, track + ".swp")
        )

    return timetable_from_dicts(events)


if __name__ == "__main__":
    # Create the bermuda swaption
    times = np.linspace(
        1, 6, 6
    ).tolist()  # Start at 1 year, mature at 6 years.
    strike_rate = 0.03
    timetable = bermuda_swaption_timetable("USD", times, strike_rate)

    print(timetable["events"].to_pandas())
