from publicmon.contrib.basemonitor import BaseMonitor
from pythonping import ping
from publicmon.contrib.metric import log_metric, Unit, Dimension
import time


class PingMonitor(BaseMonitor):
    name = "ping"
    default_settings = {"timeout": 5, "count": 5}

    def __init__(self, log, options, config):
        super().__init__(log, options, config)

    def handle(self):

        ping_response = ping(
            self.setting("target"),
            timeout=self.setting("timeout"),
            count=self.setting("count"),
        )
        metric_time = time.time()
        log_metric(
            namespace="ping",
            metric_name="rtt_min",
            unit=Unit.time_ms,
            value=ping_response.rtt_min * 1000,
            dimensions=[Dimension("title", self.config.get("title"))],
            metric_time=metric_time,
        )

        log_metric(
            namespace="ping",
            metric_name="rtt_max",
            unit=Unit.time_ms,
            value=ping_response.rtt_min * 1000,
            dimensions=[Dimension("title", self.config.get("title"))],
            metric_time=metric_time,
        )

        log_metric(
            namespace="ping",
            metric_name="rtt_avg",
            unit=Unit.time_ms,
            value=ping_response.rtt_min * 1000,
            dimensions=[Dimension("title", self.config.get("title"))],
            metric_time=metric_time,
        )
