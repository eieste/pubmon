# -*- coding: utf-8 -*-
from publicmon.mons.ping import PingMonitor
from publicmon.mons.dns import DnsMonitor
from publicmon.mons.http import HttpMonitor

MONITOR_LIST = [PingMonitor, DnsMonitor, HttpMonitor]
