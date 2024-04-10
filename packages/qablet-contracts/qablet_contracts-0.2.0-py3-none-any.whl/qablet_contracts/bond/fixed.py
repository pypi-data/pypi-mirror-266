"""
This module contains examples of creating timetables for Fixed Rate Bonds.
"""

from math import ceil

import numpy as np
import pyarrow as pa

from qablet_contracts.timetable import EVENT_SCHEMA


def cashflow_timetable(ccy: str, times, amounts, track: str = "") -> dict:
    """Create timetable from cashflows in a single currency. This example also shows how to create a timetable from arrays
    instead of a list of dictionaries, which is more efficient.

    Args:
        ccy: the currency of cashflows.
        times: a list or ndarray of cashflows times.
        amounts: a list or ndarray of cashflows amounts.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = cashflow_timetable("USD", [0.5, 1, 1.5], [0.05, 0.05, 1.05])
        >>> tt["events"].to_pandas()
          track  time op  quantity unit
        0         0.5  +      0.05  USD
        1         1.0  +      0.05  USD
        2         1.5  +      1.05  USD
    """
    n = len(times)
    return {
        "events": pa.RecordBatch.from_arrays(
            [
                pa.DictionaryArray.from_arrays(
                    indices=np.full(n, 0, dtype=np.int64), dictionary=[track]
                ),  # tracks
                pa.array(times),
                pa.DictionaryArray.from_arrays(
                    indices=np.full(n, 0, dtype=np.int64), dictionary=["+"]
                ),  # ops
                pa.array(amounts),
                pa.DictionaryArray.from_arrays(
                    indices=np.full(n, 0, dtype=np.int64), dictionary=[ccy]
                ),  # units
            ],
            schema=EVENT_SCHEMA,
        ),
        "expressions": {},
    }


def fixed_bond_timetable(
    ccy: str, coupon: float, maturity: float, freq: int = 2, track: str = ""
) -> dict:
    """Create timetable for a fixed rate bond.

    Args:
        ccy: the currency of cashflows.
        coupon: the coupon rate per year.
        maturity: the maturity of the bond.
        freq: the number of coupon payments per year.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = fixed_bond_timetable("USD", 0.05, 2.1)
        >>> tt["events"].to_pandas()
          track  time op  quantity unit
        0         0.1  +     0.025  USD
        1         0.6  +     0.025  USD
        2         1.1  +     0.025  USD
        3         1.6  +     0.025  USD
        4         2.1  +     1.025  USD
    """
    n = ceil(maturity * freq)  # How many payments left ?
    stub = (
        maturity * freq - n + 1
    )  # The first payment may be a stub/short coupon
    times = (np.arange(n) + stub) / freq
    amounts = np.full(n, coupon / freq)
    amounts[-1] += 1  # The last payment includes the principal
    return cashflow_timetable(ccy, times, amounts, track)


if __name__ == "__main__":
    # Create a timetable from cashflows
    timetable = cashflow_timetable("USD", [0.5, 1, 1.5], [0.05, 0.05, 1.05])
    print("cf:\n", timetable["events"].to_pandas())

    # Create a fixed bond timetable
    timetable = fixed_bond_timetable("USD", 0.05, 2.1)
    print("bond:\n", timetable["events"].to_pandas())
