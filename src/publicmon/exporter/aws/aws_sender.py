# -*- coding: utf-8 -*-
import threading
import boto3
import datetime


class AWSCloudWatchSender(threading.Thread):
    def __init__(self, queue, global_config, *args, **kwargs):
        self.queue = queue
        self.global_config = global_config
        self.client = boto3.client("cloudwatch")

        super(AWSCloudWatchSender, self).__init__(*args, **kwargs)

    @staticmethod
    def unit_convert(unit):
        # 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None',
        if unit == "pcs":
            return "Count"
        if unit == "percent":
            return "Percent"
        if unit == "milliseconds":
            return "Milliseconds"

    def run(self):
        buffer = []
        while True:
            item = self.queue.get()

            metric_data = {
                "MetricName": item.get("metric_name"),
                "Dimensions": list(
                    map(
                        lambda dimension: {
                            "Name": dimension["name"],
                            "Value": dimension["value"],
                        },
                        item.get("dimensions", []),
                    )
                ),
                "Timestamp": datetime.datetime.fromtimestamp(int(item.get("time"))),
                "Unit": AWSCloudWatchSender.unit_convert(item.get("unit")),
            }
            if item.get("statistic"):
                stat = item.get("statistic")
                metric_data["StatisticValues"] = {
                    "SampleCount": stat["sample_count"],
                    "Sum": stat["sum_val"],
                    "Minimum": stat["min_val"],
                    "Maximum": stat["max_val"],
                }
                metric_data["Values"] = item.get("values")
                metric_data["Counts"] = item.get("counts")
            else:
                metric_data["Value"] = item["value"]

            if len(buffer) >= 20:
                print(buffer)
                response = self.client.put_metric_data(
                    Namespace=self.global_config.get("namespace"), MetricData=buffer
                )
                buffer = []
            else:
                buffer.append(metric_data)
            self.queue.task_done()
