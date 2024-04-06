"""This module defines decorators.
"""
import logging
import time

from utilities import dictutils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def timing(screen=False, verbose=False):
    """For a decorated method, write two log statements recording (a) when the method was called
    and optionally its input arguments (if verbose==True), and (b) when the method finished and
    the total duration in seconds. If optional <<screen>> is True, output is directed to stdout
    instead of the log.

    Usage:

        @timing()
        def decorated_method():
            [do things...]

        @timing(verbose=True)
        def decorated_method(a, b, c=None):
            [do things...]

    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            name = f"Function {func.__name__}"
            started_at = f"started at {time.strftime('%H:%M:%S')}."

            if verbose:
                started_at += (
                    f"\n\t{name} input arguments:\n\t\t\t"
                    f"{dictutils.get_string(locals())}."
                )

            msg = f"{name} {started_at}"
            if screen:
                print(msg)
            else:
                logger.info(msg)

            clock_start = time.time()
            result = func(*args, **kwargs)
            clock_end = time.time()

            finished_at = f"finished at {time.strftime('%H:%M:%S')}"
            with_duration = f"with duration {(clock_end - clock_start):.3f} seconds"

            msg = f"{name} {finished_at} {with_duration}."

            if screen:
                print(msg)
            else:
                logger.info(msg)

            return result

        return wrapper

    return decorator
