"""Standard log formatters."""

import io
import traceback
from datetime import datetime
from json import dumps
from typing import Any, Collection, cast

from uvlog.uvlog import Formatter, LogRecord

__all__ = [
    "JSONFormatter",
    "TextFormatter",
]

DEFAULT_TIMESPEC = "seconds"
DEFAULT_FORMAT = "{asctime} | {level:8} | {name} | {message} | {ctx}"


def _dumps_default(obj: Any) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def _dumps_bytes(obj) -> bytes:
    # patched standard json dumps method to dump bytestring
    # in reality you'd rather want to use a faster json library like `orjson` etc.
    return dumps(obj, default=_dumps_default).encode("utf-8")


class TextFormatter(Formatter):
    """Text log formatter.

    Creates human-readable log output.

    Formatter settings can be set directly.

    .. code-block:: python

        _formatter = TextFormatter()
        _formatter.timestamp_separator = ' '

    """

    timespec: str
    """Precision for ISO timestamps,
    see `datetime.isoformat() <https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat>`_"""

    timestamp_separator: str
    """Timestamp separator for ISO timestamps,
    see `datetime.isoformat() <https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat>`_"""

    format: str
    """Log record format, a python f-string,
    the available keys can be seen in :py:class:`~uvlog.LogRecord` type
    """

    def __init__(self):
        """Initialize."""
        self.timespec = DEFAULT_TIMESPEC
        self.timestamp_separator = "T"
        self.format = DEFAULT_FORMAT

    def format_record(self, record: LogRecord, /) -> bytes:
        message = self.format.format_map(
            {
                "asctime": record.asctime.isoformat(
                    timespec=self.timespec, sep=self.timestamp_separator
                ),
                "level": record.level,
                "name": record.name,
                "message": record.message,
                "filename": record.filename,
                "func": record.func,
                "lineno": record.lineno,
                "extra": record.extra,
                "ctx": record.ctx,
            }
        )
        if record.exc_info is not None:
            exc_info = record.exc_info
            message += "\n" + self._format_exc(
                type(exc_info), exc_info, exc_info.__traceback__
            )
        return message.encode("utf-8")

    @staticmethod
    def _format_exc(error_cls, exc, stack, /) -> str:
        sio = io.StringIO()
        traceback.print_exception(error_cls, exc, stack, None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]
        return s

    def __str__(self):
        return f"<{self.__class__.__name__}>"


class JSONFormatter(Formatter):
    """JSON log formatter.

    To change the default `dumps` function assign it to the class attribute:

    .. code-block:: python

        import orjson

        JSONFormatter.serializer = orjson.dumps

    Formatter settings can be set directly.

    .. code-block:: python

        _formatter = JSONFormatter()
        _formatter.exc_pass_locals = True

    """

    serializer = _dumps_bytes
    """Serializer function - a class attribute"""

    keys: Collection[str]
    """List of serialized log record keys,
    the available keys can be seen in :py:class:`~uvlog.LogRecord` type"""

    exc_pass_locals: bool
    """Pass locals dict in exception traceback (don't use it unless you're sure your logs are secure)"""

    exc_pass_globals: bool
    """Pass globals dict in exception traceback (don't use it unless you're sure your logs are secure)"""

    def __init__(self):
        """Initialize."""
        self.exc_pass_locals = False
        self.exc_pass_globals = False
        self.keys = (
            "name",
            "level",
            "levelno",
            "asctime",
            "message",
            "exc_info",
            "args",
            "extra",
            "ctx",
            "filename",
            "lineno",
            "func",
        )

    def format_record(self, record: LogRecord, /) -> bytes:
        data = {}
        for key in self.keys:
            value = getattr(record, key, None)
            if value is not None:
                data[key] = value
        exc_info = cast(Exception, data.pop("exc_info", None))
        if exc_info:
            error_cls, exc, _ = type(exc_info), exc_info, exc_info.__traceback__
            if hasattr(exc, "serialize"):
                data["exc_info"] = exc.serialize()
            else:
                data["exc_info"] = {
                    "message": str(exc),
                    "type": error_cls.__name__,
                    "data": exc.__dict__,
                }
                if exc.__traceback__:
                    frame = exc.__traceback__.tb_frame
                    data["exc_info"]["traceback"] = tb = {
                        "lineno": frame.f_lineno,
                        "func": frame.f_code.co_name,
                    }
                    if self.exc_pass_locals:
                        tb["locals"] = frame.f_locals
                    if self.exc_pass_globals:
                        tb["globals"] = frame.f_globals

        return self.__class__.serializer(data)

    def __str__(self):
        return f"<{self.__class__.__name__}>"
