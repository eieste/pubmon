# -*- coding: utf-8 -*-
from publicmon.exporter.aws.cli import AWSExporter


__all__ = [AWSExporter]


def configure_parser(parser):

    for exporter in __all__:
        exporter.configure_parser(parser)


def handle_execute(global_config, options):
    for exporter in __all__:
        if options.exporter == exporter.exporter_name:
            exporter = AWSExporter(global_config, options)
            return exporter.handle()
