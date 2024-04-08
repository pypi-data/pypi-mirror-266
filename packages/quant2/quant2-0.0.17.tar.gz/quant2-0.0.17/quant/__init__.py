"""A collection of useful tools!"""
import sys

__version__ = "0.0.17"

help_doc_str = """\
usage: quant [--version] [--help]

shell command:
    quant -h

command-line interface:
    python -m quant -h
"""


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) >= 1:
        command, *args = args
    else:
        command, *args = ["--help"]

    args = ["--help"] if len(args) == 0 else args

    if command == "--version":
        print(f"quant version {__version__}")
    else:
        print(help_doc_str)

    return 0
