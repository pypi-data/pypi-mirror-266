"""
This module contains examples of creating timetables for Zero Coupon Bond and related contracts.
"""

from qablet_contracts.timetable import timetable_from_dicts


def zcb_timetable(ccy: str, maturity: float, track: str = "") -> dict:
    """Create timetable for a **zero coupon bond**.

    Args:
        ccy: the currency of the bond.
        maturity: the maturity of the bond in years.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = zcb_timetable("USD", 1)
        >>> tt["events"].to_pandas()
          track  time op  quantity unit
        0         1.0  +       1.0  USD
    """
    events = [
        {
            "track": track,
            "time": maturity,
            "op": "+",
            "quantity": 1,
            "unit": ccy,
        }  # get bond notional at bond expiration
    ]
    return timetable_from_dicts(events)


def zbp_timetable(
    ccy: str,
    opt_maturity: float,
    bond_maturity: float,
    strike: float,
    track: str = "",
) -> dict:
    """Create timetable for a **zero coupon bond put**.

    Args:
        ccy: the currency of the bond.
        opt_maturity: the maturity of the option in years.
        bond_maturity: the maturity of the option in years.
        strike: the option strike.
        track: an optional identifier for the contract.

    Examples:
        >>> tt = zbp_timetable("USD", 0.5, 1.0, 0.95)
        >>> tt["events"].to_pandas()
          track  time op  quantity unit
        0         0.5  >      0.00  USD
        1         0.5  +      0.95  USD
        2         1.0  +     -1.00  USD
    """

    events = [
        {
            "track": track,
            "time": opt_maturity,
            "op": ">",
            "quantity": 0,
            "unit": ccy,
        },  # Choose greater of nothing (get 0) or exercise (continue to remaining events)
        {
            "track": track,
            "time": opt_maturity,
            "op": "+",
            "quantity": strike,
            "unit": ccy,
        },  # get strike at expiration
        {
            "track": track,
            "time": bond_maturity,
            "op": "+",
            "quantity": -1,
            "unit": ccy,
        },  # pay bond notional at bond expiration
    ]
    return timetable_from_dicts(events)


if __name__ == "__main__":
    # Create a zero coupon bond timetable
    timetable = zcb_timetable("USD", 1)
    print("zcb:\n", timetable["events"].to_pandas())

    timetable = zbp_timetable("USD", 0.5, 1.0, 0.95)
    print("zbp:\n", timetable["events"].to_pandas())
