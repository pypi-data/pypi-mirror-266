# -*- coding: utf-8 -*-
import random
import string
import importlib.resources
import json
import os
import slugify
from pygments import highlight, lexers, formatters

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
    if isinstance(value, str) and value.strip() == "":
        return None

    if isinstance(value, list):
        return [obj(v) for v in value]

    if isinstance(value, dict):
        return {k: obj(v) for k, v in value.items()}

    try:
        return obj(dict(value))
    except (TypeError, ValueError):
        return value


def obj_iter(instance):
    """Defines the conversion between instance and dictionnary
    It does not ouput unset values and convert list of Iterable to dict if possible.
    """
    for k, v in instance.__dict__.items():
        print("obj_iter", k, v, obj(v), end=" ")
        # ignore unset values
        if obj(v) is None:
            print("doesn't yield")
            continue

        # convert list of Iterable to list of dict if possible
        # used for our own classes where __iter__ is defined
        if isinstance(v, list):
            print("list 1", v, end=" ")
            v = [obj(_) for _ in v if obj(v)]
            print("list 2", v, end=" ")

        # yield the key: value pair
        print("return", obj(v))
        yield k, obj(v)


def get_schema():
    """Reads the current json schema of meta data located in `resources/schema.json`.
    and returns it as a dictionary.
    """
    f = importlib.resources.files("resources").joinpath("schema.json").open("r")
    payload = json.load(f)

    return payload


def slugify_file_name(path):
    """Slugify a file name while considering it to be a path"""

    # get basename if the file and slugify
    basename = os.path.basename(path)
    basename = ".".join([slugify.slugify(_) for _ in basename.split(".")])
    # get path
    directory_path = os.path.dirname(path)
    if not len(basename):
        basename = "r3xa"
    return os.path.join(directory_path, f"{basename}")


def highlight_json(obj):
    formatted_json = json.dumps(dict(obj), sort_keys=False, indent=4)
    return highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
