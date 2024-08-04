# -*- coding: utf-8 -*-
import sys
from threading import Thread
import argparse
import logging
import pathlib
import yaml
import json
from publicmon import exporter
from concurrent.futures import ThreadPoolExecutor
from pkg_resources import resource_stream
from publicmon.contrib.monitor import find_monitor_by_classname
from jsonschema import validate
import time
from collections import namedtuple


global RUN_MONITORING
RUN_MONITORING = True

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "ERROR"

LogCollection = namedtuple("LogCollection", ("metric", "app"))

metriclog = logging.getLogger("publicmon")
appliationlog = logging.getLogger("publicmon")


log = LogCollection(metriclog, appliationlog)


def get_argparse():
    parser = argparse.ArgumentParser()
    return parser


def configure_parser(parser):
    parser.add_argument(
        "-v", "--verbose", help="Enable Verbose mode", action="append_const", const=1
    )
    parser.add_argument(
        "-q", "--quiet", help="Silence every output", action="store_true"
    )
    parser.add_argument(
        "-c", "--config", help="Path to Config file", type=pathlib.Path, required=True
    )
    parser.add_argument(
        "-t", "--tag", help="Which Tags should be Runned", type=str, action="append"
    )
    parser.add_argument(
        "-d",
        "--development",
        "--dev",
        help="Disables config Validation. used for development",
        action="store_true",
    )

    subparser = parser.add_subparsers(
        dest="module", help="Run Exporter for Metric postprocessing"
    )
    export_parser = subparser.add_parser("exporter")
    exporter.configure_parser(export_parser)
    return parser


def load_config(options):
    config_schema = json.load(resource_stream(__name__, "assets/config.schema.json"))

    with options.config.open("r") as fobj:
        config = yaml.load(fobj, yaml.SafeLoader)

    if not options.development:
        validate(instance=config, schema=config_schema)
    return config


def clean_global_config(global_config):
    default_config = {
        "check_interval": 60,
        "socket_file": "./publicmon.sock",
        "namespace": "publicmon",
    }
    default_config.update(global_config)
    return default_config


def handle(options):
    log_level = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)

    for adjustment in options.verbose or ():
        log_level = min(len(LOG_LEVELS) - 1, max(log_level - adjustment, 0))

    if options.quiet:
        log_level = -1

    log_level_name = LOG_LEVELS[log_level]
    appliationlog.setLevel(log_level_name)
    logging.basicConfig(level=getattr(logging, log_level_name))
    appliationlog.info("Set LogLevel to: " + log_level_name)

    appliationlog.info(f"Load Config from path: {options.config.absolute()}")

    config = load_config(options)
    global_config = clean_global_config(config.get("global"))

    if options.module == "exporter":
        exporter.handle_execute(global_config, options)
    else:
        schedule_handler(config, options)


def schedule_handler(config, options):
    global_config = clean_global_config(config.get("global"))

    schedule_start = -1
    with ThreadPoolExecutor(max_workers=15) as executor:
        while RUN_MONITORING:
            JOB = []
            if time.time() - schedule_start > global_config.get("check_interval", 20):
                for monitor_config in config.get("monitor", []):

                    if options.tag is None:
                        cls = find_monitor_by_classname(monitor_config.get("class"))
                        log.app.info(
                            "Add Job for {}".format(monitor_config.get("title"))
                        )
                        JOB.append(cls(log, options, monitor_config, global_config))
                    else:
                        found_at_tag = False
                        for tag in options.tag:
                            if tag in monitor_config.get("tags", []):
                                found_at_tag = True
                        if found_at_tag:
                            cls = find_monitor_by_classname(monitor_config.get("class"))
                            log.app.info(
                                "Add Job for {}".format(monitor_config.get("title"))
                            )
                            JOB.append(cls(log, options, monitor_config, global_config))

                executor.map(error_wrapper, JOB)
                schedule_start = time.time()
            else:
                time.sleep(
                    max(
                        [
                            global_config.get("check_interval", 20)
                            - (time.time() - schedule_start)
                            - 2,
                            0,
                        ]
                    )
                )


def error_wrapper(object):
    try:
        object.handle()
    except Exception as e:
        appliationlog.exception(e)
        RUN_MONITORING = False
        raise e


def main():
    parser = get_argparse()
    configure_parser(parser)
    handle(parser.parse_args())


if __name__ == "__main__":
    main()
