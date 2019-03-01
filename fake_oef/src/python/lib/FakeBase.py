class FakeBase(object):

    objects = set()

    def __init__(self, name, *args, **kwargs):
        FakeBase.objects.add(self)
        self._name = name

    def identify(self, *args, **kwargs):
        return self._name

    def tick(self, *args, **kwargs):
        pass

    def visit(function,
                fakebase_type_filter = None,
                *args, **kwargs):
        return [
            function(x, *args, **kwargs)
            for x in FakeBase.objects
        ]

    def filter(function,
                fakebase_type_filter = None,
                *args, **kwargs):
        return [
            x
            for x in FakeBase.objects
            if function(x, *args, **kwargs)
        ]
