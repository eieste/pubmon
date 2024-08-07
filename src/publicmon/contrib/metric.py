# -*- coding: utf-8 -*-
from pathlib import Path
import os
import enum
import json
import time
import socket
import threading
import logging

log = logging.getLogger(__name__)


class PublicMonJsonObject:
    def to_json(self):
        raise NotImplementedError("Please implement a to_json method")


class Statistic(PublicMonJsonObject):
    def __init__(self, sample_count=None, min_val=None, max_val=None, sum_val=None):
        self.sample_count = sample_count
        self.min_val = min_val
        self.max_val = max_val
        self.sum_val = sum_val

    def to_json(self):
        return {
            "sample_count": self.sample_count,
            "sum_val": self.sum_val,
            "min_val": self.min_val,
            "max_val": self.max_val,
        }


class Dimension(PublicMonJsonObject):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_json(self):
        return {"name": self.name, "value": self.value}


class Unit(enum.Enum):
    time_ms = "milliseconds"
    count_ones = "pcs"
    ratio_percent = "percent"


class LogMetricJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PublicMonJsonObject):
            return obj.to_json()
        elif isinstance(obj, Unit):
            return str(obj.value)
        return super().default(obj)


class MetricLogger(threading.Thread):

    _instance = None

    @staticmethod
    def get_instance(global_config, *args, **kwargs):
        if MetricLogger._instance is None:
            MetricLogger._instance = MetricLogger(global_config=global_config)
            MetricLogger._thread = MetricLogger._instance.start()
        return MetricLogger._instance

    def __init__(self, global_config=None, *args, **kwargs):
        self.global_config = global_config
        self._THREAD_STOP = False
        self._client_list_lock = threading.Lock()
        self._client_list = set({})
        super(MetricLogger, self).__init__(*args, **kwargs)

    def run(
        self,
    ):

        socket_file = Path(self.global_config.get("socket_file"))
        socket_file.parent.mkdir(parents=True, exist_ok=True)

        if socket_file.exists():
            socket_file.unlink()

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        log.info("Create Socket file {}".format(self.global_config.get("socket_file")))
        server.bind(self.global_config.get("socket_file"))

        while not self._THREAD_STOP:
            server.listen(1)
            con, client_address = server.accept()

            with self._client_list_lock:
                self._client_list.add(con)

    def write(self, data):
        json_str = json.dumps(data, cls=LogMetricJsonEncoder)

        log.info(f"Send: {json_str}")

        with self._client_list_lock:
            closed_sockets = []

            for c in self._client_list:
                try:
                    c.sendall((json_str + "\n").encode("utf-8"))
                except BrokenPipeError as e:
                    closed_sockets.append(c)

            for cc in closed_sockets:

                try:
                    cc.close()
                except Exception as e:
                    log.exception(e)
                self._client_list.remove(cc)

    def stop(self):
        self._THREAD_STOP = True
        self.join(2)
