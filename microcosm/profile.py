"""
Factory loading profiling

"""
from time import time


class NoopProfiler:

    def __call__(self, key):
        return self

    def __enter__(self):
        pass

    def __exit__(self, *args, **kargs):
        pass


class TimingProfiler:

    def __init__(self):
        self.times = dict()
        self.current = []

    def __call__(self, key):
        self.current.append(key)
        return self

    def __enter__(self):
        self.times[self.current[-1]] = time()

    def __exit__(self, *args, **kargs):
        self.times[self.current[-1]] = time() - self.times[self.current[-1]]
        self.current.pop()

    def __str__(self):
        return "\n".join(
            "{:10.8f} - {}".format(value, key)
            for key, value in sorted(
                    self.times.items(),
                    key=lambda item: -item[1],
            )[0:20]
        )
