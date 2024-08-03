# -*- coding: utf-8 -*-
import logging


class NotSet:
    pass


class BaseMonitor:
    default_setting = {}

    def __init__(self, log, options, config):
        self.log_collection = log
        self.applog = log.app.getChild(self.__class__.name + "-" + config.get("id", ""))
        self.applog.setLevel(logging.DEBUG)
        self.options = options
        self.config = config

    def setting(self, key):
        return self.config.get("settings", {}).get(
            key, self.__class__.default_setting.get(key, NotSet)
        )
