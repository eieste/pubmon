# -*- coding: utf-8 -*-
import re
from publicmon.contrib.basemonitor import BaseMonitor
from dns.resolver import Resolver
from dns.exception import DNSException
from publicmon.contrib.metric import Unit, Dimension
import time


class DnsMonitor(BaseMonitor):
    name = "dns"
    default_settings = {
        "expections": list([]),
        "nameservers": [],
        "record_type": "A",
        "record_name": None,
        "timeout": 5,
    }
    
    def handle(self):
        resolve_start = time.time()
        try:
            resolver = Resolver()
            resolver.nameservers = self.setting("nameservers")
            resolver.timeout = self.setting("timeout")

            answers = resolver.resolve(
                self.setting("record_name"), self.setting("record_type")
            )
        except DNSException:
            self._failure_state = True
        resolve_duration = (time.time() - resolve_start) * 1000

        all_expectations = len(self.setting("expectations"))

        for expectitem in self.setting("expectations"):
            value = 0
            if self._failure_state or re.match(
                r"{}".format(expectitem.get("regex")), answers.rrset.to_text()
            ) is not None:
                value = 1

            all_expectations = all_expectations - value

            if self._failure_state:
                value = -1
                all_expectations = -1
                resolve_duration = -1


            self.add_metric(
                Dimension("record", expectitem["name"]),
                Dimension("record_type", self.setting("record_type")),
                Dimension("record_name", self.setting("record_name")),
                metric_name="dns_expection",
                unit=Unit.count_ones,
                value=value,
            )

        self.add_metric(
            Dimension("record_type", self.setting("record_type")),
            Dimension("record_name", self.setting("record_name")),
            metric_name="dns_unresolved_exception",
            unit=Unit.count_ones,
            value=all_expectations,
        )

        self.add_metric(
            Dimension("record_type", self.setting("record_type")),
            Dimension("record_name", self.setting("record_name")),
            metric_name="dns_resolve_time",
            unit=Unit.time_ms,
            value=resolve_duration,
        )
