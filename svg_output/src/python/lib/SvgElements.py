from svg_output.src.python.lib import SvgElement

class SvgLine(SvgElement.SvgElement):
    def __init__(self, **kwargs):
        super().__init__("line", attributes_list=['x1', 'x2', 'y1', 'y2', 'style', 'id'], **kwargs)

class SvgCircle(SvgElement.SvgElement):
    def __init__(self, **kwargs):
        super().__init__("circle", attributes_list=['cx', 'cy', 'r', 'style', 'id'], **kwargs)

