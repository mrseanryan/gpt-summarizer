"""
main_cli.py
Author: Sean Ryan

Use an LLM to summarize text of PDF files.
"""

import sys
from optparse import OptionParser

from . import summarizer
from . import config
from . import util_version


# usage() - prints out the usage text, from the top of this file :-)
def usage(parser):
    print(__doc__)
    parser.print_help()


# optparse - parse the args
parser = OptionParser(
    usage="%prog <path to input file or input directory or URL> [options]",
    version=util_version.VERSION,
)
parser.add_option(
    "-l",
    "--language",
    dest="target_language",
    default=config.TARGET_LANGUAGE,
    help="the target output language. The default is set in config.py. Example: English.",
)
parser.add_option(
    "-o",
    "--output",
    dest="output_dir",
    default=None,
    help="the output directory. By default is None, so output is to stdout (no files are output).",
)

(options, args) = parser.parse_args()
if len(args) != 1:
    usage(parser)
    sys.exit(2)

path_to_input_file_or_dir_or_url = sys.argv[1]
target_language = options.target_language
path_to_output_dir = None
if options.output_dir:
    path_to_output_dir = options.output_dir

summarizer.summarize_file_or_dir_or_url(
    path_to_input_file_or_dir_or_url, path_to_output_dir, target_language
)
