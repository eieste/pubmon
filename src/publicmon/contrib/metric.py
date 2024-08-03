import enum
import json
import time
from collections import namedtuple


Dimension = namedtuple("Dimension", ("name", "value"))


class Unit(enum.Enum):
    time_ms = "milliseconds"


class LogMetricJsonEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Dimension):
            return {"name": obj.name, "value": obj.value}
        elif isinstance(obj, Unit):
            return str(obj.value)
        return super().default(obj)


def log_metric(
    namespace=None,
    metric_name=None,
    unit=None,
    value=None,
    dimensions=None,
    metric_time=None,
):
    metric = {
        "namespace": namespace,
        "name": metric_name,
        "unit": unit,
        "value": value,
    }
    if dimensions is not None:
        metric["dimensions"] = dimensions

    if metric_time is None:
        metric["time"] = time.time()
    else:
        metric["time"] = metric_time
    print(json.dumps(metric, cls=LogMetricJsonEncoder))
