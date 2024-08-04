# -*- coding: utf-8 -*-
from publicmon.contrib.basemonitor import BaseMonitor
from pythonping import ping
from publicmon.contrib.metric import Unit, Dimension, Statistic
import time


class PingMonitor(BaseMonitor):
    name = "ping"
    default_settings = {"timeout": 5, "count": 5}

    def handle(self):

        ping_response = ping(
            self.setting("target"),
            timeout=self.setting("timeout"),
            count=self.setting("count"),
        )
        metric_time = time.time()

        metricarray = {}

        for response in ping_response._responses:
            if response.time_elapsed in metricarray:
                metricarray[str(response.time_elapsed)] = +1
            else:
                metricarray[str(response.time_elapsed)] = 1

        self.add_metric(
            Dimension("target", self.setting("target")),
            metric_name="rtt",
            unit=Unit.time_ms,
            # value=(ping_response.rtt_avg * 1000),
            metric_time=metric_time,
            statistic=Statistic(
                sample_count=self.setting("count"),
                min_val=(ping_response.rtt_min * 1000),
                max_val=(ping_response.rtt_max * 1000),
                sum_val=sum(
                    map(lambda obj: obj.time_elapsed, ping_response._responses)
                ),
            ),
            values=[float(item) for item in metricarray.keys()],
            counts=list(metricarray.values()),
        )

        self.add_metric(
            Dimension("target", self.setting("target")),
            metric_name="packetloss",
            unit=Unit.ratio_percent,
            value=ping_response.stats_lost_ratio,
            metric_time=metric_time,
        )
