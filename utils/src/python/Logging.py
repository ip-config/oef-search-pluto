import logging
import functools
import colorlog
import functools

_ID_FLAG = ""


def configure(level=logging.INFO, id_flag=""):
    global _ID_FLAG
    log_format = '%(asctime)s, %(levelname)s:  - %(name)s ] %(message)s'
    bold_seq = '\033[1m'  #f'{bold_seq} '
    colorlog_format = (
        '%(log_color)s '
        f'{log_format}'
    )
    colorlog.basicConfig(format=colorlog_format, level=level)
    logging.basicConfig(format=log_format, level=level)
    _ID_FLAG = id_flag


class Logger:
    def __init__(self, global_name, local_name=None):
        self._logger = None
        self._global_name = global_name
        self._local_name = local_name
        self._set_logger()
        self._target_obj = None

    def _set_logger(self):
        name = self._global_name
        if self._local_name is not None:
            name += ": {}".format(self._local_name)
        self._logger = colorlog.getLogger(name)

    def __getattr__(self, item):
        return getattr(self._logger, item)

    def update_local_name(self, local_name):
        if local_name == self._local_name:
            return
        self._local_name = local_name
        self._set_logger()
        if self._target_obj is not None:
            self.expose_log_calls(self._target_obj)

    def expose_log_calls(self, target):
        def wrapper(func_name):
            func = getattr(self._logger, func_name)

            @functools.wraps(func)
            def inner_wrapper(*args, **kwargs):
                if len(args) > 1:
                    if isinstance(args[0], str):
                        if args[0].find("%") == -1:
                            return func(("{} "*len(args)).format(*args), **kwargs)
                    else:
                        return func(("{} " * len(args)).format(*args), **kwargs)
                return func(*args, **kwargs)
            return inner_wrapper
        for func_name in ["debug", "info", "warning", "error", "critical", "exception"]:
            setattr(target, func_name,  wrapper(func_name))
        self._target_obj = target


def has_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        name = self.__class__.__name__+_ID_FLAG
        local_name = None
        if "id" in kwargs:
            local_name = kwargs["id"]
        self.log = Logger(name, local_name)
        self.log.expose_log_calls(self)
        return func(*args, **kwargs)
    return wrapper


def get_logger(name):
    return Logger(name+_ID_FLAG)
