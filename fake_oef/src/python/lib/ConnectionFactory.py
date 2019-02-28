from fake_oef.src.python.lib import Connection

class ConnectionFactory(object):
    def __init__(self, **kwargs):
        self.cores = {}

    def addCore(self, id, core):
        self.cores[id] = core

    def create(self, **kwargs):
        target = kwargs.get('target', None)
        if target in self.cores:
            core = self.cores[target]
            return Connection.Connection(core=core, **kwargs)
        else:
            print("NO TARGET:", target)
