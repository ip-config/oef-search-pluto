from svg_output.src.python.lib import SvgElement

class SvgGraph(SvgElement.SvgElement):
    def __init__(self, *args, **kwargs):
        super().__init__("g", attributes_list=['id'], **kwargs)
        if args:
            self._children.extend(args)

    def add(self, *args):
        self._children.extend(args)
        return self

    def empty(self):
        self._children = []
        return self
