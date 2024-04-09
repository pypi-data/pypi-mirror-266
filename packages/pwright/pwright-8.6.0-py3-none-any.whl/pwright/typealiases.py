from datetime import timedelta
import typing as t


T = t.TypeVar('T')

SecondsT = t.Union[float, timedelta]

GeneratorContextManager = t.Callable[[t.Any], t.ContextManager[T]]
AsyncGeneratorContextManager = t.Callable[[t.Any], t.AsyncContextManager[T]]
