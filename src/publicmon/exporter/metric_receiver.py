# -*- coding: utf-8 -*-
import threading
import socket
import json
import logging
import struct
import msgpack


log = logging.getLogger(__name__)


class MetricReceiver(threading.Thread):
    def __init__(self, queue, config, *args, **kwargs):
        self._THREAD_STOP = False
        self.queue = queue
        self.config = config
        super(MetricReceiver, self).__init__(*args, **kwargs)

    def stop(self):
        self._THREAD_STOP = True

    def connect(self):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(self.config.get("socket_file"))
        except Exception as e:
            log.exception(e)

        return client

    def handle(self):

        self.client = self.connect()

        while not self._THREAD_STOP:
            data = self.client.recv(2)
            pack_len = struct.unpack("H", data)[0]
            msg = self.client.recv(pack_len)
            self.queue.put(msgpack.unpackb(msg))

        self.client.close()  # close the connection

    def run(self):
        try:
            self.handle()
        except Exception as e:
            log.exception(e)
        log.error("Thread Metric Receive Stopped!")
