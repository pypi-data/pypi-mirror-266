import typing as t


if t.TYPE_CHECKING:
    from _typeshed import SupportsAnext

    _T = t.TypeVar('_T')
    _VT = t.TypeVar('_VT')

    @t.overload  # type: ignore[no-overload-impl]
    async def anext(__i: SupportsAnext[_T]) -> _T: ...
    @t.overload
    async def anext(__i: SupportsAnext[_T], __default: _VT) -> t.Union[_T, _VT]: ...


__anext_default = object()


async def anext(__i, __default=__anext_default):  # type: ignore[no-redef]
    try:
        return await __i.__anext__()
    except StopAsyncIteration:
        if __default is __anext_default:
            raise
        return __default
