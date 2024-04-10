# -*- coding: utf-8 -*-


def script_validate():
    from r3xa.validation import validate
    import json
    import argparse

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


def script_gui():
    from r3xa.gui import Window
    from PyQt5.QtWidgets import QApplication
    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="r3xa", description="Create or edit a meta data file.", epilog="---")
    parser.add_argument("--json", default=None, help="Path to the metadata jsonfile you want to edit.")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    if args.json:
        window = Window(json_file_name=args.json)
    else:
        window = Window()
    window.setGeometry(100, 100, 400, 100)
    window.show()
    sys.exit(app.exec())
