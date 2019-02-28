

class Connection(object):
    def __init__(self, **kwargs):
        for k in [ 'target', 'core', 'agent', 'agent_id', 'subject' ]:
            setattr(self, k, kwargs.get(k, None))

        self.core.agent_register(self.agent, self.agent_id, self.subject, self)

    def destroy(self):
        self.agent.connection_dropped(self)
        self.core.agent_unregister_connection(self)

    def kill(self):
        self.destroy()
