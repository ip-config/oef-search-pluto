from dap_api.src.protos import dap_update_pb2

class FakeAgent(object):
    def __init__(self, **kwargs):
        for k in [ 'connection_factory', 'id' ]:
            setattr(self, k, kwargs.get(k, None))

        self.connections = {}

    def connect(self, target, subject):
        self.connections[target] = self.connection_factory.create(agent=self, agent_id=id, target=target, subject=subject)
        return self.connections[target]

    def disconnect(self, target):
        if target in self.connections:
            c = self.connections[target]
            self.connections.pop(target)
            c.destroy()

    def connection_dropped(self, conn):
        keys = [ k for k,v in self.connections.items() if v == conn ]
        for k in keys:
            self.connections.pop(k)

    def kill(self):
        keys = list(self.connections.keys())
        for k in keys:
            self.connections.pop(k)
