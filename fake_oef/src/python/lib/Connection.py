import functools
import abc


class Connection(object):
    def __init__(self, source_endpoint, target_endpoint):
        self._source = source_endpoint
        self._target = target_endpoint
        self._target.register_connection(source_endpoint)
        self._connected = True

    def __getattr__(self, item):
        if not self._connected:
            return None
        if hasattr(self._target, item):
            func = getattr(self._target, item)
            return func
        else:
            raise AttributeError("Attribute {} not found!".format(item))

    def disconnect(self):
        self._connected = False
        self._target.unregister_connection(self._source)
        self._source = None
        self._target = None
