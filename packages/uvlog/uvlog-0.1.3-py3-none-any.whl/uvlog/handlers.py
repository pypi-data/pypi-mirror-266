"""Standard log handlers."""

import queue
import sys
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Thread
from time import sleep
from typing import BinaryIO, List, Optional, cast, no_type_check
from urllib.parse import urlparse

from uvlog.formatters import TextFormatter
from uvlog.uvlog import Formatter, Handler, LevelName, LogRecord, name_to_level

__all__ = ["StreamHandler", "QueueHandler", "QueueStreamHandler", "handle_error"]


@no_type_check
def handle_error(message: bytes, /) -> None:
    """Handle an error which occurs during an emit() call.

    This method is a loose ripoff of the standard python logging error handling mechanism.
    """
    _, exc, tb = sys.exc_info()
    try:
        sys.stderr.write("--- Logging error ---\n")
        traceback.print_exception(exc, limit=None, file=sys.stderr, value=exc, tb=tb)
        sys.stderr.write("Call stack:\n")
        frame = exc.__traceback__.tb_frame
        while frame:
            frame = frame.f_back
        if frame:
            traceback.print_stack(frame, file=sys.stderr)
        try:
            sys.stderr.write(f"Message: {message}\n")
        except RecursionError:
            raise
        except Exception:  # noqa: acceptable
            sys.stderr.write(
                "Unable to print the message and arguments"
                " - possible formatting error.\nUse the"
                " traceback above to help find the error.\n"
            )
    except OSError:
        pass
    finally:
        del exc


class StreamHandler(Handler):
    """Logging handler.

    A simple stream handler which immediately writes a log record to the write buffer. It provides the best performance.
    However, in server applications you may want to use `uvlog.QueueStreamLogger`
    to ensure your code is not blocking due to intensive logging.
    """

    terminator = b"\n"

    _level: LevelName
    _levelno: int
    _formatter: Formatter
    _dest: str
    _stream: Optional[BinaryIO]

    def __init__(self):
        """Initialize."""
        self._level = "DEBUG"
        self._levelno = name_to_level["DEBUG"]
        self._formatter = TextFormatter()
        self._dest = "stderr"
        self._stream = None

    def handle(self, record: LogRecord, /) -> None:
        """Immediately write a log record to the write buffer."""
        if record.levelno < self._levelno:
            return
        if self._stream is None:
            self.open_stream()
        record_bytes = self._formatter.format_record(record)
        try:
            cast(BinaryIO, self._stream).write(record_bytes + self.terminator)
        except Exception:  # noqa: acceptable
            handle_error(record_bytes)

    def set_level(self, level: LevelName, /) -> None:
        self._level = level
        self._levelno = name_to_level[level]

    def set_formatter(self, formatter: Formatter, /) -> None:
        self._formatter = formatter

    def set_destination(self, dest: str, /) -> None:
        """Set log destination (file stream).

        Pre-configured destinations are: 'stdout' and 'stderr'.

        Both plain and URL file formats are acceptable and normalized into a path string:

        - logs.txt - relative path
        - /logs.txt - absolute path
        - file:///logs.txt - absolute path in file URL format
        """
        self._dest = dest
        if dest not in ("stderr", "stdout"):
            _path = Path(urlparse(dest).path).absolute()
            _path.parent.mkdir(parents=True, exist_ok=True)
            _path.touch(exist_ok=True)

    def close(self) -> None:
        """Close the handler including all connections to its destination.

        This method is called automatically at exit for each added handler by the :py:func:`~uvlog.clear` function.
        """
        if self._stream and not self._stream.closed:
            self._stream.flush()
            if self._stream not in (sys.stderr.buffer, sys.stdout.buffer):
                self._stream.close()
        self._stream = None

    def open_stream(self) -> None:
        """Open a file stream."""
        if self._dest == "stderr":
            self._stream = sys.stderr.buffer
        elif self._dest == "stdout":
            self._stream = sys.stdout.buffer
        else:
            self._stream = open(self._dest, "ab")

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self._dest} / {self._formatter}>"


class QueueHandler(Handler, ABC):
    """Logging handler with an internal queue.

    The handler uses a separate thread to write logs to the buffer via the :py:meth:`~uvlog.QueueHandler.write`
    method. Note that this handler doesn't use any internal locks,
    because it's expected by design that each handler has its own destination.
    """

    _sentinel = None

    queue_size: int
    """Log queue size, infinite by default"""

    batch_size: int
    """Maximum number of log records to concatenate and write at once,
    consider setting it so an average batch would be ~ tens of KBs"""

    _level: LevelName
    _levelno: int
    _write_queue: queue.Queue
    _thread: Optional[Thread]
    _formatter: Formatter

    def __init__(self):
        """Initialize."""
        self.queue_size = -1
        self.batch_size = 50
        self._level = "DEBUG"
        self._levelno = name_to_level["DEBUG"]
        self._write_queue = queue.Queue()
        self._thread = None
        self._formatter = TextFormatter()

    @abstractmethod
    def open_stream(self) -> None:
        """Open a stream and prepare for sending logs there."""
        # self._stream = ...

    @abstractmethod
    def close_stream(self) -> None:
        """Close the stream if opened."""
        # self._stream = None
        # ...

    @abstractmethod
    def write_records(self, formatted_records: List[bytes], /) -> None: ...

    def __post_init__(self):
        self._levelno = name_to_level[self._level]
        self._write_queue.maxsize = self.queue_size

    def set_level(self, level: LevelName, /) -> None:
        self._level = level
        self._levelno = name_to_level[level]

    def set_formatter(self, formatter: Formatter, /) -> None:
        self._formatter = formatter

    def handle(self, record: LogRecord, /) -> None:
        """Put a log record to the write queue."""
        if record.levelno < self._levelno:
            return
        if self._thread is None:
            self._thread = self._open_thread()
        self._write_queue.put(record)

    def write(self) -> None:
        """Write logs from the queue to the stream.

        This method is executed in a separate thread.
        """
        _queue = self._write_queue
        _queue.maxsize = self.queue_size
        _sentinel = self._sentinel
        _formatter = self._formatter
        _batch_size = self.batch_size
        _formatted_records: List[bytes] = []
        _exit = False
        self.open_stream()

        while not _exit:
            if _queue.qsize():
                _record = _queue.get(block=True)
                if _record is _sentinel:
                    break
                _formatted_records.append(_formatter.format_record(_record))
                _queue.task_done()
            else:
                for _ in range(min(_batch_size, _queue.qsize())):
                    _record = _queue.get_nowait()
                    if _record is _sentinel:
                        _exit = True
                    _formatted_records.append(_formatter.format_record(_record))
                    _queue.task_done()

            if _formatted_records:
                try:
                    self.write_records(_formatted_records)
                except Exception:  # noqa
                    handle_error(_formatted_records[0])
                _formatted_records.clear()

            sleep(0)

    def close(self) -> None:
        """Close the handler including all connections to its destination.

        This method is called automatically at exit for each added handler by the :py:func:`~uvlog.clear` function.
        """
        self._write_queue.put(self._sentinel)
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        # just in case the stream is not closed, however it should be closed when existing the `_write` method
        self.close_stream()

    def _open_thread(self) -> Thread:
        self._write_queue.maxsize = self.queue_size
        thread = Thread(target=self.write, name=f"{self} _write", args=(), daemon=True)
        thread.start()
        return thread


class QueueStreamHandler(QueueHandler, StreamHandler):
    """Logging handler with an internal queue.

    This handler uses a queue and a separate thread providing at least some concurrency during intensive logging
    workload. It has a worse overall performance than :py:class:`~uvlog.StreamHandler` but may be beneficial if you have
    concurrent code such as a server application.

    You may want to set :py:attr:`~uvlog.QueueHandler.queue_size`
    to some reasonable value considering your application workload.
    """

    queue_size: int
    """Log queue size, infinite by default"""

    batch_size: int
    """Maximum number of log records to concatenate and write at once,
    consider setting it so an average batch would be ~ tens of KBs"""

    def __init__(self):
        """Initialize."""
        QueueHandler.__init__(self)
        StreamHandler.__init__(self)

    def open_stream(self) -> None:
        StreamHandler.open_stream(self)

    def close_stream(self) -> None:
        StreamHandler.close(self)

    def write_records(self, formatted_records: List[bytes], /) -> None:
        formatted_records.append(b"")
        cast(BinaryIO, self._stream).write(
            self.terminator.join(formatted_records) + b""
        )
