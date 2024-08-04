# -*- coding: utf-8 -*-
import json
import sys
import os


def interpret_value(raw):

    if raw.lower() in ["y", "yes", "t", "true", "1"]:
        return True
    elif raw.lower() in ["n", "no", "f", "false", "0"]:
        return False
    elif raw.match(r"^\d+$", raw.lower()):
        return int(raw)
    elif raw.match(r"^\d+\.\d$", raw.lower()):
        return int(raw)

    try:
        return json.loads(raw)
    except json.decoder.JSONDecodeError:
        return raw


def get_environment_variables():
    PREFIX = "PUBLICMON_"
    envvar = {}
    for name, value in os.environ.items():
        if name.upper().startswith(PREFIX):
            envvar[name.lower()[len(PREFIX) :]] = interpret_value(value)
    return envvar
