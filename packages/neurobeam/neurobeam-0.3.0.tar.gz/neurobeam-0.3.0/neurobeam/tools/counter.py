from functools import partial
from itertools import count


class _CallableCounter(count):
    def __call__(self):
        return next(self)


def _inner_counter(_counter: _CallableCounter):
    return _counter()


def counter() -> partial:
    _counter = _CallableCounter()
    return partial(_inner_counter, _counter)
