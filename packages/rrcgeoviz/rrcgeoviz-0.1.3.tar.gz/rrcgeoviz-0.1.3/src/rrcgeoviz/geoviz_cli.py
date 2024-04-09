import json
import subprocess
import argparse
import sys
import pandas as pd
from pandas.errors import EmptyDataError

from rrcgeoviz.arguments import Arguments

from rrcgeoviz.JsonCreator import main_javacreator


# https://docs.python.org/3/library/argparse.html#action

PARSER_ARGUMENTS = [
    {
        "name": "data",
        "metavar": "csvfilepath",
        "help": "File path to CSV file to be analyzed",
        "type": argparse.FileType("r", encoding="UTF-8"),
    },
    {
        "name": "options",
        "metavar": "jsonfilepath",
        "help": "File path to the JSON configuration folder",
        "type": argparse.FileType("r", encoding="UTF-8"),
    },
    {
        "name": "--test",
        "metavar": "setTestMode",
        "help": "Disables starting Panel server for testing",
        "action": argparse.BooleanOptionalAction,
    },
]


def addParserArguments(parser: argparse.ArgumentParser):
    for argument in PARSER_ARGUMENTS:
        if "type" in argument:
            parser.add_argument(
                argument["name"],
                metavar=argument["metavar"],
                help=argument["help"],
                type=argument["type"],
            )
        elif "action" in argument:
            parser.add_argument(
                argument["name"],
                metavar=argument["metavar"],
                help=argument["help"],
                action=argument["action"],
            )
    return parser


def main(argv=None):
    if (argv is not None and "--init" in argv) or "--init" in sys.argv:
        main_javacreator()
        sys.exit()

    """argv is an array of strings, simulating command line arguments"""
    parser = argparse.ArgumentParser(
        description="Command-Line Interface for GeoViz Project"
    )
    parser = addParserArguments(parser)
    args = parser.parse_args(argv)
    arguments = Arguments(args.data, args.options)

    if args.test:
        print("Testing mode enabled")

    from rrcgeoviz.GeneratedData import GeneratedData

    arguments.generated_data = GeneratedData(arguments)
    from rrcgeoviz.GeoVizPanelDashboard import GeoVizPanelDashboard

    dashboard = GeoVizPanelDashboard(args=arguments, test=args.test)

    if not args.test:
        dashboard.render()


if __name__ == "__main__":
    sys.exit(main())
