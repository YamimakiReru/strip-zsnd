# coding: utf-8
from __future__ import annotations

from rich.logging import RichHandler
import logging
import threading

TRACE = 5

class LogMixin:
    """
    Subclasses may override the class constant `LOGGER_PREFIX`.

    Note:
        By default, RLogMixin does not reference the module name.
        In Python, Module names depend on how the module was imported.
    """
    LOGGER_PRFIX: str = 'r.'

    @classmethod
    def get_logger(cls):
        return LoggerRepository.get_logger(cls.LOGGER_PRFIX + cls.__name__)

class _FrameworkLogMixin(LogMixin):
    LOGGER_PRFIX = 'r.framework.'

class TraceableLoggerAdapter(logging.LoggerAdapter):
    def trace(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(TRACE):
            self.logger._log(TRACE, msg, args, **kwargs)

    def is_trace_enabled(self):
        return self.isEnabledFor(TRACE)

class LoggerRepository:
    _logger_map: dict[str, TraceableLoggerAdapter] = {}
    _lock = threading.Lock()

    @classmethod
    def clear(cls):
        with cls._lock:
            cls._logger_map.clear()

    @classmethod
    def get_logger(cls, name: str):
        with cls._lock:
            if name in cls._logger_map:
                return cls._logger_map[name]
            else:
                new_adapter = TraceableLoggerAdapter(logging.getLogger(name))
                cls._logger_map[name] = new_adapter
                return new_adapter

    @classmethod
    def _init(cls):
        if 'TRACE' in logging.getLevelNamesMapping():
            logging.addLevelName(LogMixin.LOG_LEVEL_TRACE, 'TRACE')

class LogConfigurator:
    def configure(self, verbosity: int):
        level = logging.INFO
        if 1 <= verbosity:
            level = logging.DEBUG
        if 3 <= verbosity:
            level = TRACE

        LoggerRepository.clear()
        # remove existing handlers to reconfigure
        for h in logging.root.handlers:
            logging.root.removeHandler(h)
        logging.basicConfig(level=level,
                # format="%(levelname)s: %(message)s",
                handlers=[RichHandler(markup=True, rich_tracebacks=True)])
