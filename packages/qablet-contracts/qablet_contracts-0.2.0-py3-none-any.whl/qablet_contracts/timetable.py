# Define the timetable schema

from abc import ABC, abstractmethod
from typing import Dict, List

import pyarrow as pa

DICT_TYPE = pa.dictionary(pa.int64(), pa.string())

# Event Schema for the timetable, using floating point for time,
# now being deprecated
EVENT_SCHEMA = pa.schema(
    [
        pa.field("track", DICT_TYPE),
        pa.field("time", pa.float64()),
        pa.field("op", DICT_TYPE),
        pa.field("quantity", pa.float64()),
        pa.field("unit", DICT_TYPE),
    ]
)

# Event Schema for the timetable, using timestamp for time
TS_TYPE = pa.timestamp("ms", tz="UTC")
TS_EVENT_SCHEMA = pa.schema(
    [
        pa.field("track", DICT_TYPE),
        pa.field("time", TS_TYPE),
        pa.field("op", DICT_TYPE),
        pa.field("quantity", pa.float64()),
        pa.field("unit", DICT_TYPE),
    ]
)


def timetable_from_dicts(events: List[Dict]) -> Dict:
    """Create timetable from a list of dicts.

    Args:
        events: a list of dicts with the following fields:

            - track: string
            - time: float
            - op: string
            - quantity: float
            - unit: string

    Returns:
        a timetable dictionary with the following fields:

            - events: a pyarrow record batch
            - expressions: a dict for expressions, batches, and snappers

    """
    return {
        "events": pa.RecordBatch.from_pylist(events, schema=EVENT_SCHEMA),
        "expressions": {},
    }


def py_to_ts(py_dt):
    """Convert a python datetime to a pyarrow timestamp (milliseconds)."""
    return pa.scalar(py_dt, type=TS_TYPE)


class EventsMixin(ABC):
    """A mixin class for contracts that generates a timetable from events list."""

    @abstractmethod
    def events(self) -> List[Dict]: ...

    def expressions(self) -> Dict:
        return {}

    def timetable(self):
        return {
            "events": pa.RecordBatch.from_pylist(
                self.events(), schema=TS_EVENT_SCHEMA
            ),
            "expressions": self.expressions(),
        }


def convert_time_to_ts(timetable, base_ts):
    """Convert events of timetable in place, changing time column into timestamp column.
    This function is used convert timetables created by legacy methods that use floating point
    for time into timetables with timestamp for time."""
    events = timetable["events"]

    if events["time"].type == pa.float64():
        ts_list = [
            base_ts + t.as_py() * 31_536_000_000 for t in events["time"]
        ]

        timetable["events"] = pa.RecordBatch.from_arrays(
            [
                events["track"],
                ts_list,
                events["op"],
                events["quantity"],
                events["unit"],
            ],
            schema=EVENT_SCHEMA,
        )
