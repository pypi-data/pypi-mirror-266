"""
See
https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output

:author: Guillaume Algis
"""
import logging

# Use ANSI escape code to color the console:
# https://en.wikipedia.org/wiki/ANSI_escape_code
# try:
# import colorist  => python >= 3.10
# from colorist import BgColor, Color, Effect
from colorama import Back as BgColor
from colorama import Fore as Color
from colorama import Style


def mk_formatter(*codes):
    fmt = "{start}{{}}{end}".format(start="".join(codes), end=Style.RESET_ALL)
    return lambda msg: fmt.format(msg)


COLORS = {
    "WARNING": mk_formatter(Color.YELLOW),
    "INFO": mk_formatter(Color.GREEN),
    "DEBUG": mk_formatter(Color.BLUE),
    "CRITICAL": mk_formatter(),
    "ERROR": mk_formatter(BgColor.RED, Style.BRIGHT, Color.BLACK),
}


def colorize_loglevel(loglevel):
    f = COLORS.get(loglevel)
    if f:
        loglevel = f(loglevel)
    return loglevel


DEFAULT_FORMAT = (
    "[{BOLD}%(name)-20s{RESET}] %(asctime)s [%(levelname)-18s] "
    "%(message)s ({BOLD}%(filename)s{RESET}:%(lineno)d)"
)


def formatter_message(format=DEFAULT_FORMAT, use_color=True):
    """
    See Format a message to replace the codes $RESET and $BOLD where necessary.

    :param message: the message to format
    :param use_color: if you want ot add color.
    :return: An ansi formatted log message
    """
    bold, reset = (Style.BRIGHT, Style.RESET_ALL) if use_color else ("", "")
    return format.format(BOLD=bold, RESET=reset)


class ColoredFormatter(logging.Formatter):
    """
    A colored formatted.
    """

    def __init__(self, format=DEFAULT_FORMAT):
        format = formatter_message(format, use_color=True)
        logging.Formatter.__init__(self, format)

    def format(self, record):
        """
        Format the given record.

        :param record:
        :return: a logging formater
        """
        record.levelname = colorize_loglevel(record.levelname)
        return logging.Formatter.format(self, record)


def get_formatter(format=DEFAULT_FORMAT, use_color=True):
    if use_color:
        return ColoredFormatter(format)
    format = formatter_message(format, use_color=False)
    return logging.Formatter(format)
