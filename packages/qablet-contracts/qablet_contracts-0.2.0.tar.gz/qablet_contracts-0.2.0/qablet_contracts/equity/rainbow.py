"""
This module contains examples of creating timetables for equity rainbow options.
"""

from typing import List

from qablet_contracts.timetable import timetable_from_dicts


def rainbow_timetable(
    ccy: str,
    asset_names: List[str],
    strikes: List[float],
    notional: float,
    maturity: float,
    is_call: bool,
    track: str = "",
) -> dict:
    """Create timetable for an **Equity Rainbow Option**.

    Args:
        ccy: the currency of the option.
        asset_names: the name of the underlying assets.
        strikes: the option strikes.
        notional: the notional of the option.
        maturity: the maturity of the option in years.
        is_call: true if the option is a call.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = rainbow_timetable(
        >>>     "USD",
        >>>     ["SPX", "FTSE", "N225"],
        >>>     [5087, 7684, 39100],
        >>>     100_000,
        >>>     0.5,
        >>>     True
        >>> )
        >>> tt["events"].to_pandas()  # Call
          track  time op       quantity  unit
        0         0.5  + -100000.000000   USD
        1         0.5  >      19.657952   SPX
        2         0.5  >      13.014055  FTSE
        3         0.5  >       2.557545  N225
        4         0.5  +  100000.000000   USD

        >>> tt = rainbow_timetable(
        >>>     "USD",
        >>>     ["SPX", "FTSE", "N225"],
        >>>     [5087, 7684, 39100],
        >>>     100_000,
        >>>     0.5,
        >>>     False
        >>> )
        >>> tt["events"].to_pandas()  # Put
          track  time op       quantity  unit
        0         0.5  +  100000.000000   USD
        1         0.5  >     -19.657952   SPX
        2         0.5  >     -13.014055  FTSE
        3         0.5  >      -2.557545  N225
        4         0.5  + -100000.000000   USD
    """

    sign = 1 if is_call else -1
    # Pay the initial strike
    events = [
        {
            "track": "",
            "time": maturity,
            "op": "+",
            "quantity": -notional * sign,
            "unit": ccy,
        },
    ]

    # Options to receive any of the assets
    for asset, strike in zip(asset_names, strikes):
        events.append(
            {
                "track": "",
                "time": maturity,
                "op": ">",
                "quantity": notional / strike * sign,
                "unit": asset,
            }
        )

    # Otherwise receive the notional back
    events.append(
        {
            "track": "",
            "time": maturity,
            "op": "+",
            "quantity": notional * sign,
            "unit": ccy,
        }
    )
    return timetable_from_dicts(events)


if __name__ == "__main__":
    # Create the rainbow option
    timetable = rainbow_timetable(
        "USD",
        ["SPX", "FTSE", "N225"],
        [5087, 7684, 39100],
        100_000,
        0.5,
        True,
    )
    print(timetable["events"].to_pandas())
