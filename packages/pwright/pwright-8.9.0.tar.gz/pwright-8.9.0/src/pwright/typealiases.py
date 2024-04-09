from datetime import timedelta
import typing as t


try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec  # type: ignore[assignment]


T = t.TypeVar('T')
P = ParamSpec('P')


SecondsT = t.Union[float, timedelta]

GeneratorContextManager = t.Callable[P, t.ContextManager[T]]
AsyncGeneratorContextManager = t.Callable[P, t.AsyncContextManager[T]]
