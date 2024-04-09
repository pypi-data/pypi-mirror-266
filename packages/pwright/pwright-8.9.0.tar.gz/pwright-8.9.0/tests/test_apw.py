import asyncio
from contextlib import asynccontextmanager
import sys
import time
import typing as t

from pwright import apw


if sys.version_info < (3, 10):
    anext = apw.anext


def test_pw_page():
    async def get_title(*, url: str):
        async with apw.pw_page() as page:
            await page.goto(url)
            title = await page.title()
            return title

    assert 'Playwright' in asyncio.run(get_title(url='https://playwright.dev/'))


async def _test_renew(headed=True):
    @asynccontextmanager
    async def gen_page():
        async with apw.pw_page(headed=headed) as page:
            yield page

    async def run(gen: t.AsyncGenerator[apw.Page, None]):
        for _ in range(5):
            page = await anext(gen)
            await page.goto('https://playwright.dev/')
            print(id(page))
            if 0:
                time.sleep(0.2)
        await gen.aclose()
        if 0:
            await asyncio.sleep(30)

    await run(apw.renewable(gen_page, 3))
    async with apw.auto_renew(gen_page, 3) as agen:
        await run(agen)


def test_renew():
    asyncio.run(_test_renew(headed=False))


if __name__ == '__main__':
    asyncio.run(_test_renew())
