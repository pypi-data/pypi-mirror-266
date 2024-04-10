"""
This module contains examples of creating timetables for equity vanilla options.
"""

from qablet_contracts.timetable import timetable_from_dicts


def _option_events(ccy, asset_name, strike, maturity, is_call, track):
    events = [
        {
            "track": track,
            "time": maturity,
            "op": ">",
            "quantity": 0,
            "unit": ccy,
        },
        {
            "track": track,
            "time": maturity,
            "op": "+",
            "quantity": -strike if is_call else strike,
            "unit": ccy,
        },
        {
            "track": track,
            "time": maturity,
            "op": "+",
            "quantity": 1 if is_call else -1,
            "unit": asset_name,
        },
    ]
    return events


def option_timetable(
    ccy: str,
    asset_name: str,
    strike: float,
    maturity: float,
    is_call: bool,
    track: str = "",
) -> dict:
    """Create timetable for an **Equity Vanilla Option**.

    Args:
        ccy: the currency of the option.
        asset_name: the name of the underlying asset.
        strike: the option strike.
        maturity: the maturity of the option in years.
        is_call: true if the option is a call.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = option_timetable("USD", "AAPL", 190, 1.0, True)  # Call
        >>> tt["events"].to_pandas()
          track  time op  quantity  unit
        0         1.0  >       0.0   USD
        1         1.0  +    -190.0   USD
        2         1.0  +       1.0  AAPL

        >>> tt = option_timetable("USD", "AAPL", 190, 1.0, False)  # Put
        >>> tt["events"].to_pandas()
          track  time op  quantity  unit
        0         1.0  >       0.0   USD
        1         1.0  +     190.0   USD
        2         1.0  +      -1.0  AAPL
    """

    events = _option_events(ccy, asset_name, strike, maturity, is_call, track)

    return timetable_from_dicts(events)


if __name__ == "__main__":
    # Create the option
    timetable = option_timetable("USD", "SPX", 2900, 0.5, True, track="ID_01")
    print(timetable["events"].to_pandas())
