"""
Utils for creating forward starting options timetable
"""

import pyarrow as pa

from qablet_contracts.timetable import EVENT_SCHEMA


def forward_option_timetable(
    ccy: str,
    asset_name: str,
    strike_rate: float,
    strike_time: float,
    maturity: float,
    is_call: bool,
    track: str = "",
) -> dict:
    """Create timetable for a **Forward Starting Option**.

    Args:
        ccy: the currency of the option.
        asset_name: the name of the underlying asset.
        strike_rate: the option strike in percent of fixing.
        strike_time: the time at which the strike is fixed.
        maturity: the maturity of the option in years.
        is_call: true if the option is a call.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = forward_option_timetable("USD", "EQ", 1.1, 1.0, 2.0, True)
        >>> tt["events"].to_pandas()
          track  time   op  quantity unit
        0   NaN   1.0  NaN       0.0  FIX
        1         2.0    >       0.0  USD
        2         2.0    +      -1.1   .K
        3         2.0    +       1.0   EQ
    """
    strike_snap = track + ".K"
    events = [
        {
            "track": None,
            "time": strike_time,
            "op": None,
            "quantity": 0,
            "unit": "FIX",  # set the strike
        },
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
            "quantity": -strike_rate if is_call else strike_rate,
            "unit": strike_snap,
        },
        {
            "track": track,
            "time": maturity,
            "op": "+",
            "quantity": 1 if is_call else -1,
            "unit": asset_name,
        },
    ]

    # Define the strike expression, return the spot itself.
    def strike_fn(inputs):
        return inputs

    fix = {
        "type": "snapper",
        "inp": [asset_name],
        "fn": strike_fn,
        "out": [strike_snap],
    }

    events_table = pa.RecordBatch.from_pylist(events, schema=EVENT_SCHEMA)
    return {"events": events_table, "expressions": {"FIX": fix}}


if __name__ == "__main__":
    # Create the option
    timetable = forward_option_timetable("USD", "EQ", 1.1, 1.0, 2.0, True)
    print(timetable["events"].to_pandas())
