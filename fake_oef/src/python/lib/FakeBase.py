class FakeBase(object):

    objects = set()

    def __init__(self, *args, **kwargs):
        FakeBase.objects.add(self)

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
