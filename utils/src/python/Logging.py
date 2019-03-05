import logging
import functools
import colorlog


def configure(level=logging.INFO):
    log_format = '%(asctime)s, %(levelname)s:  - %(name)s ] %(message)s'
    bold_seq = '\033[1m'  #f'{bold_seq} '
    colorlog_format = (
        '%(log_color)s '
        f'{log_format}'
    )
    colorlog.basicConfig(format=colorlog_format, level=level)
    logging.basicConfig(format=log_format, level=level)


def has_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        name = self.__class__.__name__
        if "id" in kwargs:
            name += ": {}".format(kwargs["id"])
        self.log = logging.getLogger(name)
        return func(*args, **kwargs)
    return wrapper


def get_logger(name):
    return colorlog.getLogger(name)
