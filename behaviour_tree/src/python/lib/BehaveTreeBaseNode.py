from abc import ABC
from abc import abstractmethod

class BehaveTreeBaseNode(object):
    def __init__(self, definition: dict=None, *args, **kwargs):
        self.children = []
        self.name = "--"
        if definition:
            self.configure(definition=definition)

    # Override me to handle setup.
    def configure(self, definition: dict=None):
        self.name = definition.get("name", "??")

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
            print("     EX:", self.name, ex)
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
