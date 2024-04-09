# -*- coding: utf-8 -*-
import random
import string
import importlib.resources
import json

#######################
# Utilitary functions #
#######################


def random_slug(n: int = 6):
    """Generates a random string  of n ascii lowercase chars.
    This function is used to generates unique identifiers.
    """
    chars = string.ascii_lowercase  # + string.digits
    return "".join([random.choice(chars) for i in range(n)])


def obj(value):
    """Convert a value as a dictionary if possible.
    This function is used in the meta data classes to convert them to json parsable objects.
    It implies that the object have their `self.__iter__` functions implemented.
    """
    if isinstance(value, list):
        return [obj(v) for v in value]

    if isinstance(value, dict):
        return {k: obj(v) for k, v in value.items()}

    try:
        return obj(dict(value))
    except (TypeError, ValueError):
        return value


def get_schema():
    """Reads the current json schema of meta data located in `resources/schema.json`.
    and returns it as a dictionary.
    """
    f = importlib.resources.files("resources").joinpath("schema.json").open("r")
    payload = json.load(f)

    return payload
