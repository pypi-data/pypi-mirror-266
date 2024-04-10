from datetime import datetime

import pandas as pd

from qablet_contracts.eq.autocall import AutoCallable
from qablet_contracts.eq.barrier import OptionKO
from qablet_contracts.eq.cliquet import Accumulator
from qablet_contracts.eq.forward import ForwardOption


def test_classes():
    # Autocallable
    start = datetime(2024, 3, 31)
    maturity = datetime(2024, 9, 30)
    barrier_dates = pd.date_range(
        start, maturity, freq="ME", inclusive="right"
    )
    tt = AutoCallable(
        "USD", "AAPL", 100, 80, start, maturity, 102, barrier_dates, 0.092
    ).timetable()
    assert len(tt["events"]) == 7

    # Barrier
    start = datetime(2024, 3, 31)
    maturity = datetime(2024, 9, 30)
    barrier_dates = pd.date_range(
        start, maturity, freq="ME", inclusive="right"
    )
    tt = OptionKO(
        "USD", "EQ", 100, maturity, True, 102, "Up/Out", barrier_dates
    ).timetable()
    assert len(tt["events"]) == 9

    # Cliquet
    fix_dates = pd.bdate_range(
        datetime(2021, 12, 31), datetime(2024, 12, 31), freq="2BQE"
    )
    global_floor = 0.0
    local_floor = -0.03
    local_cap = 0.05
    tt = Accumulator(
        "USD", "SPX", fix_dates, global_floor, local_floor, local_cap
    ).timetable()
    assert len(tt["events"]) == 9

    # ForwardOption
    tt = ForwardOption(
        "USD",
        "SPX",
        1.0,
        datetime(2024, 3, 31),
        datetime(2024, 9, 30),
        True,
    ).timetable()
    assert len(tt["events"]) == 4
