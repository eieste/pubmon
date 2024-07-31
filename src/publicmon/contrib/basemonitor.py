import logging

class BaseMonitor:

    def __init__(self, log, options, config):
        self.log = log.getChild(self.__class__.name+"-"+config.get("id", ""))
        self.log.setLevel(logging.DEBUG)
        self.options = options
        self.config = config
