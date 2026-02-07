# homegrown framework (オレオレフレームワーク)

from .log import LogMixin, LoggerRepository
from .app import App, TyperApp

# __debug__ is True when running on usual environment.
# (even when it is a release build such as a Pyinstaller exe)
# Only `python -O` makes __debug__ False at compile time.
DEBUG = __debug__

__all__ = [
    DEBUG,
    LogMixin.__name__,
    App.__name__,
    TyperApp.__name__,
]

LoggerRepository._init()
