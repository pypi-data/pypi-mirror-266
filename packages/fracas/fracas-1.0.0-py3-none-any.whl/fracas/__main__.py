#!/usr/bin/env python3
import argparse
from importlib.metadata import version

from . import journal


def formatter(prog):
    return argparse.HelpFormatter(prog, max_help_position=52)


parser = argparse.ArgumentParser(
    formatter_class=formatter,
    prog="fracas",
    description="Command line journal",
    usage="%(prog)s [options]",
)
parser.add_argument(
    dest="search_terms",
    metavar="search-terms",
    nargs="*",
    help="words or tags to search for",
)
parser.add_argument("--edit", "-e", action="store_true", help="edit entries")
parser.add_argument(
    "--from-date",
    action="store",
    help="get entries from this date",
)
parser.add_argument("-n", type=int, help="get last N entries")
parser.add_argument("--tags", "-t", action="store_true", help="list tags")
parser.add_argument("--to-date", action="store", help="get entries to this date")
parser.add_argument(
    "-v", "--version", action="version", version="fracas version " + version("fracas")
)


def main():
    args = parser.parse_args()
    journal.main(args)
