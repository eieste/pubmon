# -*- coding: utf-8 -*-
import threading
import socket
import json
import logging

log = logging.getLogger(__name__)


class MetricReceiver(threading.Thread):
    def __init__(self, queue, config, *args, **kwargs):
        self.queue = queue
        self.config = config
        super(MetricReceiver, self).__init__(*args, **kwargs)

    def connect(self):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(self.config.get("socket_file"))
        except Exception as e:
            log.exception(e)

        return client

    def run(self):
        self.client = self.connect()
        while True:
            try:
                data = self.client.recv(1024).decode("utf-8")
                if not data:
                    break
                for entry in data.strip().split("\n"):

                    self.queue.put(json.loads(entry))
            except Exception as e:
                log.exception(e)

        self.client.close()  # close the connection
