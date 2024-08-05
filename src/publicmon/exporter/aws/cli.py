# -*- coding: utf-8 -*-
from publicmon.exporter.metric_receiver import MetricReceiver
import socket
from publicmon.exporter.aws.aws_sender import AWSCloudWatchSender
import os, os.path
import time
from collections import deque
import queue
import logging

log = logging.getLogger(__name__)


class AWSExporter:
    exporter_name = "aws"

    @staticmethod
    def configure_parser(parser):
        parser = parser.add_subparsers(dest="exporter")
        parser.add_parser("aws", help="Send Metrics to AWS")

    def __init__(self, global_config, options):
        self.options = options
        self.global_config = global_config

    def handle(self):
        
        q = queue.Queue()
        metric_receiver = MetricReceiver(q, self.global_config)
        metric_receiver.start()

        aws_sender = AWSCloudWatchSender(q, self.global_config)
        aws_sender.start()

        while aws_sender.is_alive() and metric_receiver.is_alive():
            if q.qsize() > 0:
                log.info(f"Queue Size {q.qsize()}")
            time.sleep(0.1)

        aws_sender.join(2)
        metric_receiver.join(2)
