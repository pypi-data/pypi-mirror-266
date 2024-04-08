import sys

help_doc_str = """\
usage: quant-fb <command> [options]

Commands:
    help
"""


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) >= 1:
        command, *args = args
    else:
        command, *args = ["--help"]

    args = ["--help"] if len(args) == 0 else args

    if command == "help":
        print(help_doc_str)
    else:
        print(help_doc_str)

    return 0
