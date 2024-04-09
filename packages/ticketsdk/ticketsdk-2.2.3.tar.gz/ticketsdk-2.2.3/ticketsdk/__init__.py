import platform
import logging

__version__ = "2.2.2"
Version = __version__

try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


UserAgent = "ticketSDK/{} Python/{} {}/{}".format(
    __version__,
    platform.python_version(),
    platform.system(),
    platform.release(),
)

log = logging.getLogger("ticketsdk")

if not log.handlers:
    log.addHandler(NullHandler())


def get_version():
    return __version__
