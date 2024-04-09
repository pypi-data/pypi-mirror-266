"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = imgdataconvertcodegen.interface_cmd:run


"""

import argparse
import sys

from imgdataconvertcodegen import __version__


def parse_args(args):
    parser = argparse.ArgumentParser(description="Automatically generating conversion code for in-memory"
                                                 " representations of images using a knowledge graph of data types")
    parser.add_argument(
        "--version",
        action="version",
        version=f"ImgDataConvertCodeGen {__version__}",
    )
    return parser.parse_args(args)


def main(args):
    parse_args(args)


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m imgdataconvertcodegen.interface_cmd
    #
    run()
