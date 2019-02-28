class SvgStyle(object):
    def __init__(self, values={}, **kwargs):
        self.values = {}
        self.values.update(values)
        self.values.update(**kwargs)

    def render(self):
        return "".join(
            [
                "{}:{};".format(k,v) for k,v in self.values.items()
            ])
