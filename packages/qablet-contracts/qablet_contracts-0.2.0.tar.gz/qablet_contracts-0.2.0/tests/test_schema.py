from qablet_contracts.timetable import EVENT_SCHEMA, TS_EVENT_SCHEMA


def test_old_schema():
    assert EVENT_SCHEMA.names == ["track", "time", "op", "quantity", "unit"]
    assert TS_EVENT_SCHEMA.names == ["track", "time", "op", "quantity", "unit"]
