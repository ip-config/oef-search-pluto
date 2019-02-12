

class DapQueryResult:
    def __init__(self, key: bytes):
        self.key = key
        self.score = -1

    def __call__(self, *args, **kwargs):
        return self.key
