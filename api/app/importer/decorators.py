import time as pytime
from functools import wraps
from friendlylog import colored_logger as log


def time(msg):
    """ Output time consumed by function """
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
          tic = pytime.perf_counter()
          result = fn(*args, **kwargs)
          toc = pytime.perf_counter()
          log.debug(f"{msg}: {toc - tic:0.4f}s")
          return result
        return wrapper
    return decorate