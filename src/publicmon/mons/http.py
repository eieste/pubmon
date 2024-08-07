# -*- coding: utf-8 -*-
import re
from publicmon.contrib.environment import get_environment_variables
from publicmon.contrib.basemonitor import BaseMonitor
import requests
import logging
from publicmon.contrib.metric import Unit, Dimension
import time
from string import Template


log = logging.getLogger(__name__)


class HttpMonitor(BaseMonitor):
    name = "http"
    default_settings = {}

    def handle(self):
        http_request_setting = self.setting("http_request", {})
        env_var = get_environment_variables()
        method_name = str(http_request_setting.get("method", "GET")).lower()
        http_call = getattr(requests, method_name)
        response = None
        request_header = {}

        for name, value in http_request_setting.get("header", {}).items():
            value_tpl = Template(value)
            request_header[name] = value_tpl.safe_substitute(**env_var)

        request_start = time.time()
        try:
            response = http_call(
                self.setting("url"),
                headers=request_header,
                data=http_request_setting.get("body", None),
                allow_redirects=http_request_setting.get("allow_redirects", False),
                timeout=http_request_setting.get("timeout", 5),
            )
            status_code = response.status_code
        except requests.exceptions.ConnectionError:
            self._failure_state = True
            status_code = -1
            http_duration = -1
        http_duration = (time.time() - request_start) * 1000

        self.add_metric(
            Dimension("url", self.setting("url")),
            Dimension("method", http_request_setting.get("method")),
            metric_name="http_statuscode",
            unit=Unit.count_ones,
            value=status_code,
        )

        if self._failure_state:
            http_duration = -1


        self.add_metric(
            Dimension("url", self.setting("url")),
            Dimension("method", http_request_setting.get("method")),
            metric_name="http_full_request",
            unit=Unit.time_ms,
            value=http_duration,
        )

        self.evaluate_headers(response)
        self.evaluate_body(response)

    def evaluate_body(self, response):
        http_request_setting = self.setting("http_request", {})

        expected_body_match_count = len(self.setting("expected_body"))

        for expected_body in self.setting("expected_body"):

            value = 0
            if self._failure_state or (
                re.match(r"{}".format(expected_body.get("regex")), response.text)
                is not None
            ):
                value = 1

            expected_body_match_count = expected_body_match_count - value

            if self._failure_state:
                value = -1

            self.add_metric(
                Dimension("body_name", expected_body["name"]),
                Dimension("url", self.setting("url")),
                Dimension("method", http_request_setting.get("method")),
                metric_name="http_body",
                unit=Unit.count_ones,
                value=value,
            )

        if self._failure_state:
            expected_body_match_count = -1

        self.add_metric(
            Dimension("url", self.setting("url")),
            Dimension("method", http_request_setting.get("method")),
            metric_name="http_body",
            unit=Unit.count_ones,
            value=expected_body_match_count,
        )

    def evaluate_headers(self, response):
        http_request_setting = self.setting("http_request", {})

        matched_header_count = len(self.setting("expected_header"))

        for expected_header in self.setting("expected_header"):
            try:
                value = 0
                if (
                    self._failure_state or
                    re.match(r"{}".format(expected_header.get("regex")), response.headers[expected_header.get("name")])
                    is not None
                ):
                    value = 1

                matched_header_count = matched_header_count - value

            except KeyError:
                value = -1
            
            if self._failure_state:
                value = -1

            self.add_metric(
                Dimension("header_name", expected_header["name"]),
                Dimension("url", self.setting("url")),
                Dimension("method", http_request_setting.get("method")),
                metric_name="http_header",
                unit=Unit.count_ones,
                value=value,
            )


        if self._failure_state:
            matched_header_count = -1
            
        self.add_metric(
            Dimension("url", self.setting("url")),
            Dimension("method", http_request_setting.get("method")),
            metric_name="http_header",
            unit=Unit.count_ones,
            value=matched_header_count,
        )
