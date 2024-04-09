from contextlib import contextmanager
from pathlib import Path
import typing as t

from .._constants import INIT_SCRIPT_HIDE_NAVIGATOR
from ..typealiases import SecondsT
from ._apis import ProxySettings
from ._cms import playwright_browser
from ._cms import playwright_context
from ._cms import playwright_page


pw_browser = playwright_browser


@contextmanager
def pw_context(
    *,
    # [browser]
    executable_path: t.Optional[t.Union[str, Path]] = None,
    headed: t.Optional[bool] = None,
    proxy: t.Optional[ProxySettings] = None,
    slow_mo: t.Optional[SecondsT] = None,
    traces_dir: t.Optional[t.Union[str, Path]] = None,
    # [context]
    no_viewport: t.Optional[bool] = True,
    user_agent: t.Optional[str] = None,
    is_mobile: t.Optional[bool] = None,
    # proxy: t.Optional[ProxySettings] = None,
    # [context.tracing]
    tracing=False,
    snapshots=True,
    screenshots=True,
    sources=True,
    path='trace.zip',
):
    with playwright_context(**locals()) as (_, context):
        yield context


@contextmanager
def pw_page(
    *,
    # [browser]
    executable_path: t.Optional[t.Union[str, Path]] = None,
    headed: t.Optional[bool] = None,
    proxy: t.Optional[ProxySettings] = None,
    slow_mo: t.Optional[SecondsT] = None,
    traces_dir: t.Optional[t.Union[str, Path]] = None,
    # [context]
    no_viewport: t.Optional[bool] = True,
    user_agent: t.Optional[str] = None,
    is_mobile: t.Optional[bool] = None,
    # proxy: t.Optional[ProxySettings] = None,
    # [context.tracing]
    tracing=False,
    snapshots=True,
    screenshots=True,
    sources=True,
    path='trace.zip',
    # [page]
    default_navigation_timeout: t.Optional[SecondsT] = None,
    default_timeout: t.Optional[SecondsT] = None,
    init_script: t.Optional[str] = INIT_SCRIPT_HIDE_NAVIGATOR,
    init_script_path: t.Optional[t.Union[str, Path]] = None,
):
    with playwright_page(
        **locals(),
    ) as (_, _, page):
        yield page
