
class SvgElement(object):
    def __init__(self, name, **kwargs):
        self._name = name
        self._attributes_list = kwargs.get('attributes_list', [])
        self._children = []
        for k in self._attributes_list:
            if k in kwargs:
                setattr(self, k, kwargs[k])

    def render(self):
        return ''.join(self._render())

    def _render(self):
        if self._children:
            yield self.open() + ">"
            for c in self._children:
                yield c.render()
            yield self.close()
        else:
            yield self.open() + "/>"

    def __setattribute__(self, n, v):
        if n in self.__dict__ or n in self._attributes_list:
            self.__dict__[n] = v
        else:
            raise AttributeError("Not a settable value:"+n)

#    def __getattribute__(self, n):
#        if n in self.__dict__:
#            return self.__dict__[n]
#        if
#
#        if hasattr(self, n):
#            return getattr(self, n)
#        if n in getattr(self, '_attributes_list'):
#            return None
#        raise AttributeError("Not a gettable value:"+n)

    def close(self):
        return "</{}>".format(self._name)

    def open(self):
        r = "<{}".format(self._name)
        for a in self._attributes_list:
            if hasattr(self, a):
                v = getattr(self, a)
                if hasattr(v, 'render'):
                    r += " {}=\"{}\"".format(a, v.render())
                else:
                    r += " {}=\"{}\"".format(a, v)
        return r
