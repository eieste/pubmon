from publicmon.contrib.basemonitor import BaseMonitor
from pythonping import ping


class PingMonitor(BaseMonitor):
    name = "ping"

    def __init__(self, log, options, config):
        super().__init__(log, options, config)

    def handle(self):
        ping_response = ping("8.8.8.8", timeout=1, verbose=True, count=2)
        print(ping_response.rtt_min)
        print(ping_response.rtt_avg)
        print(ping_response.rtt_max)