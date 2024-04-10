from qablet_contracts.equity.autocall import autocallable_timetable
from qablet_contracts.equity.barrier import ko_option_timetable
from qablet_contracts.equity.cliquet import clique_timetable
from qablet_contracts.equity.forward_start import forward_option_timetable


def test_methods():
    tt = ko_option_timetable("USD", "EQ", 100, 0.2, True, 100, "Dn/Out", 5)
    assert len(tt["events"]) == 9

    tt = autocallable_timetable("USD", "AAPL", 100, 80, 1, 102, 4, 0.092)
    assert len(tt["events"]) == 5

    tt = clique_timetable("USD", "SPX", [1.0, 2.0, 3.0], 0.01, -0.03, 0.05)
    assert len(tt["events"]) == 5

    tt = forward_option_timetable("USD", "EQ", 1.1, 1.0, 2.0, True)
    assert len(tt["events"]) == 4
