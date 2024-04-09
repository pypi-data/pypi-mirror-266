from datetime import timedelta
import typing as t


T = t.TypeVar('T')
P = t.TypeVar('P')

SecondsT = t.Union[float, timedelta]

GeneratorContextManager = t.Callable[[P], t.ContextManager[T]]
AsyncGeneratorContextManager = t.Callable[[P], t.AsyncContextManager[T]]
