# -*- coding: utf-8 -*-
from publicmon.mons import MONITOR_LIST


def find_monitor_by_classname(name):
    for monitor_cls in MONITOR_LIST:
        if monitor_cls.name == name:
            return monitor_cls
