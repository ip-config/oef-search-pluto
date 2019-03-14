from abc import ABC
from abc import abstractmethod
from utils.src.python.Logging import has_logger


class BehaveTreeBaseNode(object):
    @has_logger
    def __init__(self, definition: dict=None, *args, **kwargs):
        self.children = []
        self.name = "--"
        if definition:
            self.configure(definition=definition)

    # Override me to handle setup.
    def configure(self, definition: dict=None):
        self.name = definition.get("name", "??")
        self.log.update_local_name(self.name)

    @abstractmethod
    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        # return True for complete, False for fail or SELF for "call me again".
        pass

    def _buildChildrenFromList(self, loader: 'BehaveTreeLoader.BehaveTreeLoader', definitions: list):
        self.children.extend(loader.buildAll(definitions))

    def _execute(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        try:
            #print("    RUN:", self.name)
            r = self.tick(context=context, prev=prev)
        except Exception as ex:
            self.exception("Exception @ {}: {}".format(self.name, str(ex)))
            r = False
        if r == True:
            #print("SUCCESS:", self.name)
            pass
        elif r == False:
            #print("   FAIL:", self.name)
            pass
        else:
            #print("RUNNING:", self.name)
            pass
        return r

    def printable(self):
        return "{} ({},{})".format(self.name, type(self).__name__, "" if not hasattr(self, "kind") else getattr(self, "kind"))
