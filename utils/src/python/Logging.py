import logging
import functools


def configure(level=logging.INFO):
    logging.basicConfig(format='%(asctime)s, %(levelname)s:  - %(name)s ] %(message)s', level=level)


def has_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = args[0].__class__.__name__
        args[0].log = logging.getLogger(name)
        return func(*args, **kwargs)
    return wrapper


def get_logger(name):
    return logging.getLogger(name)
