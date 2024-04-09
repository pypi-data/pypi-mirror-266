# -*- coding: utf-8 -*-

from r3xa.validation import validate
import json
import argparse


def script_validate():
    parser = argparse.ArgumentParser(
        prog="r3xa-validate",
        description="Validate a json meta data file against the schema.",
        epilog="---",
    )
    parser.add_argument(
        dest="JSON_FILE",
        type=str,
        help="Path to the metadata jsonfile you want to validate.",
    )
    # args parser
    args = parser.parse_args()
    instance = json.load(open(args.JSON_FILE, "r"))
    validate(instance)
