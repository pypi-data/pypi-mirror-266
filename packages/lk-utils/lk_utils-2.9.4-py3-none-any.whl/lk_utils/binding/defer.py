import typing as t

from .signal import Signal


def define_later():
    pass


def iterate_later() -> 'DeferredIterator':
    return DeferredIterator()


class DeferredIterator:
    __slots__ = ('_results', '_signal')
    
    def __init__(self) -> None:
        # self._results = ()
        self._signal = Signal()
    
    # def __iter__(self) -> t.Iterator:
    #     yield from self._results
    
    def bind(self, func: t.Callable[[], t.Iterator[t.Any]]) -> None:
        # self._results = func()
        self._signal.emit(func())

    def on_triggered(self, func: t.Callable) -> None:
        self._signal.bind(func)
        

class Later:
    
    def __call__(self, func):
        pass
