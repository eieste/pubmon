# -*- coding: utf-8 -*-
import logging
import time
from publicmon.contrib.metric import MetricLogger, Dimension


class NotSet:
    pass


class BaseMonitor:
    name = None
    default_setting = {}

    def __init__(self, log, options, monitor_config, global_config):
        self.log_collection = log
        self.applog = log.app.getChild(
            self.__class__.name + "-" + monitor_config.get("id", "")
        )
        self.applog.setLevel(logging.DEBUG)
        self.options = options
        self.config = monitor_config
        self.global_config = global_config
        self._failure_state = False

    def setting(self, key, default=NotSet):
        return self.config.get("settings", {}).get(
            key, self.__class__.default_setting.get(key, default)
        )

    def add_metric(
        self,
        *dimensions,
        metric_name=None,
        unit=None,
        value=None,
        metric_time=None,
        statistic=None,
        counts=None,
        values=None
    ):
        log = MetricLogger.get_instance(self.global_config)
        if metric_name is None and isinstance(metric_name, str):
            raise RuntimeError("metric_name must have an value and must be a string")

        if unit is None:
            raise RuntimeError(
                "unit must have an value and must be a value publicmon.contrib.metric.Unit Enum"
            )

        metric_item = {
            "metric_name": metric_name,
            "unit": unit,
            "value": value,
            "dimensions": list(
                map(lambda item: Dimension(**item), self.config.get("dimensions", []))
            )
            + list(dimensions)
            + [
                Dimension("title", self.config.get("title")),
                Dimension("check_class", self.__class__.name),
            ],
        }

        if statistic is not None and values is not None and counts is not None:
            metric_item["statistic"] = statistic
            metric_item["values"] = values
            metric_item["counts"] = counts

        if metric_time is None:
            metric_item["time"] = time.time()
        else:
            metric_item["time"] = metric_time

        log.write(metric_item)
