"""logging module patching"""

from __future__ import absolute_import


import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, Union, Any, Optional, Literal
from vxutils import __vxutils__

try:
    import colorama
except ImportError:
    pass
else:
    colorama.init()

__all__ = (
    "loggerConfig",
    "VXColoredFormatter",
    "VXLogRecord",
)


# Returns escape codes from format codes
def esc(*x: str) -> str:
    """escape codes from format codes"""
    return "\033[" + ";".join(x) + "m"


# The initial list of escape codes
escape_codes = {
    "reset": esc("0"),
    "bold": esc("01"),
}

# The color names
COLORS = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]

PREFIXES = [
    # Foreground without prefix
    ("3", ""),
    ("01;3", "bold_"),
    # Foreground with fg_ prefix
    ("3", "fg_"),
    ("01;3", "fg_bold_"),
    # Background with bg_ prefix - bold/light works differently
    ("4", "bg_"),
    ("10", "bg_bold_"),
]

for prefix, prefix_name in PREFIXES:
    for code, name in enumerate(COLORS):
        escape_codes[prefix_name + name] = esc(prefix + str(code))


def parse_colors(sequence: str) -> str:
    """Return escape codes from a color sequence."""
    return "".join(escape_codes[n] for n in sequence.split(",") if n)


# The default colors to use for the debug levels
default_log_colors = {
    "DEBUG": "bold_green",
    "INFO": "white",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

# The default format to use for each style
default_formats = {
    "%": "%(log_color)s%(levelname)s:%(name)s:%(message)s",
    "{": "{log_color}{levelname}:{name}:{message}",
    "$": "${log_color}${levelname}:${name}:${message}",
}


class _dict(Dict[str, Any]):

    def __missing__(self, key: str) -> Any:
        try:
            return parse_colors(key)
        except Exception as err:
            raise KeyError(
                f"{key} is not a valid record attribute or color sequence"
            ) from err


class VXLogRecord(logging.LogRecord):
    """
    A wrapper class around the LogRecord class.

    1. 增加颜色字段: %(log_color)s
    2. 增加自定义事件字段 %(quanttime)s --用于自定义日志时间

    """

    def __init__(self, record: logging.LogRecord) -> None:
        self.__dict__ = _dict()
        self.__dict__.update(record.__dict__)
        self.__record = record

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__record, name)


class VXFormatter(logging.Formatter):
    pass


class VXColoredFormatter(VXFormatter):
    """
    A formatter that allows colors to be placed in the format string.

    Intended to help in creating more readable logging output.
    """

    def __init__(
        self,
        fmt: str = "",
        datefmt: str = "",
        style: Literal["%", "{", "$"] = "%",
        log_colors: Optional[Dict[str, str]] = None,
        reset: bool = True,
        secondary_log_colors: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Set the format and colors the ColoredFormatter will use.

        The ``fmt``, ``datefmt`` and ``style`` args are passed on to the
        ``logging.Formatter`` constructor.

        :Parameters:
        - fmt (str): The format string to use
        - datefmt (str): A format string for the date
        - log_colors (dict):
            A mapping of log level names to color names
        - reset (bool):
            Implictly append a color reset to all records unless False
        - style ('%' or '{' or '$'):
            The format style to use.
        """
        if fmt is None:
            fmt = default_formats[style]

        super().__init__(fmt, datefmt, style)
        self.log_colors = log_colors if log_colors is not None else default_log_colors
        self.secondary_log_colors = secondary_log_colors
        self.reset = reset

    def color(self, log_colors: Dict[str, str], name: str) -> str:
        """Return escape codes from a ``log_colors`` dict."""
        return parse_colors(log_colors.get(name, ""))

    def format(self, old_record: logging.LogRecord) -> str:
        """Format a message from a record object."""
        record = VXLogRecord(old_record)
        record.log_color = self.color(self.log_colors, record.levelname)
        # record.quanttime = self.__quanttime_func__().strftime(
        #    self.datefmt or "%Y-%m-%d %H:%M:%S.%f"
        # )
        message = super().format(record)
        # Add a reset code to the end of the message
        # (if it wasn't explicitly added in format str)
        if self.reset and not message.endswith(escape_codes["reset"]):
            message += escape_codes["reset"]

        return message


__COLOR_BASIC_FORMAT__ = (
    "%(log_color)s%(asctime)s [%(process)s:%(threadName)s - %(funcName)s@%(filename)s:%(lineno)d]"
    " %(levelname)s: %(message)s%(reset)s"
)

__BASIC_FORMAT__ = (
    "%(asctime)s [%(process)s:%(threadName)s - %(funcName)s@%(filename)s:%(lineno)d]"
    " %(levelname)s: %(message)s"
)


def loggerConfig(
    level: Union[str, int] = "INFO",
    format: Optional[str] = None,
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    *,
    force: bool = False,
    colored: bool = True,
    filename: Union[str, Path] = "",
    encoding: Optional[str] = None,
    logger: Optional[Union[str, logging.Logger]] = None,
) -> logging.Logger:
    """为logging模块打补丁"""
    if logger is None:
        logger = logging.root

    if isinstance(logger, str):
        logger = logging.getLogger(logger)

    if force:
        logger.handlers = []

    if logger.handlers:
        return logger

    if format is None:
        format = __COLOR_BASIC_FORMAT__ if colored else __BASIC_FORMAT__

    if colored:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(VXColoredFormatter(fmt=format, datefmt=datefmt))
        console_handler.setLevel(level=level)
        logger.addHandler(console_handler)

    if filename:
        format = format.replace("%(log_color)s", "").replace("%(reset)s", "")
        log_file = Path(filename)
        log_dir = log_file.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            log_file, when="D", interval=1, backupCount=7, encoding=encoding
        )
        file_handler.setFormatter(VXFormatter(fmt=format, datefmt=datefmt))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # logging.basicConfig(
    #    level=level,
    #    format=format,
    #    datefmt=datefmt,
    #    handlers=handlers,
    # )
    return logger


if __name__ == "__main__":

    loggerConfig(
        level="DEBUG",
        force=True,
        colored=True,
        filename="log/message.log",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug("debug")
    logging.info("hello")
    logging.warning("warning")
    logging.error("error")
    logging.critical("critical")
    logging.info("info")
    logging.info("info2")
    logging.info("info3")
