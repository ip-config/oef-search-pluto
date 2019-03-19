

class DapQueryResult:
    def __init__(self, core: bytes, agent: bytes = b''):
        self.key = core
        self.agent_id = agent
        self.score = -1

    def __call__(self, core_agent_key_pair=False):
        if core_agent_key_pair:
            return self.key, self.agent_id
        else:
            return self.key
