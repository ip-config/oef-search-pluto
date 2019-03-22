from dap_api.src.protos import dap_interface_pb2

class DapQueryResult:
    def __init__(self, core: bytes = None, agent: bytes = b'', pb:'dap_interface_pb2.Identifier' = None):
        self.core_id = core
        self.agent_id = agent
        self.score = -1

        if pb and pb.HasField('agent'):
            self.agent_id = pb.agent
        if pb and pb.HasField('core'):
            self.core_id = pb.core

    def __call__(self, core_agent_key_pair=False):
        if core_agent_key_pair:
            return self.core_id, self.agent_id
        else:
            return self.core_id

    def asIdentifierProto(self):
        m = dap_interface_pb2.Identifier
        if self.core_id != None:
            m.core = self.core_id
        if self.agent_id != None:
            m.agents = self.agent_id
        return m

    def printable(self):
        return "core={}, agent={}".format(
            self.core_id.decode('utf8'),
            "NONE" if self.agent_id == None else self.agent_id.decode('utf8'),
        )
