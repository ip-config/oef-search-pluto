from fake_oef.src.python.lib import Connection
from utils.src.python.Logging import has_logger
import abc
from fake_oef.src.python.lib import Connection


class Endpoint:
    def __init__(self, target, target_id, source_id):
        if not isinstance(target, SupportsConnectionInterface):
            raise TypeError("Creating endpoint for object which doesn't implement the SuppportConnectionInterface not permitted!")
        self._target = target
        self._source_id = source_id
        self._target_id = target_id
        self.id = target_id

    def __getattr__(self, item):
        return getattr(self._target, item)


class SupportsConnectionInterface(abc.ABC):
    @property
    @abc.abstractmethod
    def connection(self):
        pass

    @connection.setter
    @abc.abstractmethod
    def connection(self, value):
        pass

    def register_connection(self, endpoint: Endpoint):
        self.connection[endpoint.id] = endpoint

    def unregister_connection(self, endpoint: Endpoint):
        if endpoint.id in self.connection:
            self.connection.pop(endpoint.id)

    def kill(self):
        conns = [c for c in self.connection.values() if isinstance(c, Connection.Connection)]
        self.connection = {}
        for c in conns:
            c.disconnect()


class ConnectionFactory(object):
    @has_logger
    def __init__(self):
        self._obj_store = {}

    def add_obj(self, obj_id, obj):
        if obj_id in self._obj_store and obj != self._obj_store[obj_id]:
            print(self._obj_store)
            print(obj_id)
            raise KeyError("Different object in the store with the same id: {}".format(obj_id))
        self._obj_store[obj_id] = obj

    def clear(self, what = None):
        keys = self._obj_store.keys()
        if what is not None:
            keys = [k for k in keys if k.find(what) != -1]
        for key in keys:
            self._obj_store.pop(key)

    def remove(self, obj_id):
        self._obj_store.pop(obj_id, None)

    def create(self, target, source):
        if target in self._obj_store:
            target_endpoint = Endpoint(self._obj_store[target], target, source)
        else:
            self.log.error("NO TARGET: {}".format(target))
            return None
        if source in self._obj_store:
            source_endpoint = Endpoint(self._obj_store[source], source, target)
        else:
            self.log.error("NO SOURCE: {}".format(source))
            return None
        return Connection.Connection(source_endpoint, target_endpoint)
