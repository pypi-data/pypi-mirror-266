"""
Logging utilities.

:author Johan Lanzrein:
:file logger.py:
"""
import logging
from pathlib import Path

from rich.logging import Console, RichHandler

from .colored_formatter import get_formatter


def get_default_handler(filename=None, filemode="a", stream=None):
    if not filename and not stream:
        return RichHandler()
    if filename and stream:
        raise Exception("You cannot use both a stream and filename options")

    if filename:
        formatter = get_formatter(use_color=False)
        handler = logging.FileHandler(filename, mode=filemode)
    else:
        formatter = get_formatter(use_color=True)
        handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    return handler


def get_rich_handler(filename=None, filemode="a", stream=None):
    if filename and stream:
        raise Exception("You cannot use both a stream and filename options")

    if filename:
        console = Console(file=Path(filename).open(filemode))  # noqa
    else:
        console = Console(file=stream)
    return RichHandler(console=console)


# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
    """
    A colored logger.
    """

    def __init__(
        self, name, level=logging.INFO, filename=None, filemode="a", stream=None
    ):
        """
        name        name of the logger
        filename  Specifies that a FileHandler be created, using the specified
                filename, rather than a StreamHandler.
        filemode  Specifies the mode to open the file, if filename is specified
                (if filemode is unspecified, it defaults to 'a').
        level     Set the root logger level to the specified level.
                    (Default to INFO)
        stream    Use the specified stream to initialize the StreamHandler.
                    Note that this argument is incompatible with 'filename'
                    - if both are present, 'stream' is ignored.
        """
        handler = get_default_handler(
            filename=filename, filemode=filemode, stream=stream
        )
        super().__init__(self, name, level)

        self.addHandler(handler)
        return


def set_default_logger(filename=None, filemode="a", stream=None, rich=False):
    # logging.setLoggerClass(ColoredLogger)
    # Also replace the handler for the default logger instance
    # It can be accessed using `logging.critical("hello world")`
    handler_getter = get_rich_handler if rich else get_default_handler
    handler = handler_getter(filename=filename, filemode=filemode, stream=stream)
    default_logger = logging.getLogger()
    default_logger.handlers.clear()
    default_logger.addHandler(handler)
