import asyncio
from contextlib import asynccontextmanager
import sys
import time

from pwright import apw as pw


if sys.version_info < (3, 10):
    anext = pw.anext


def test_pw_page():
    async def get_title(*, url: str):
        async with pw.pw_page() as page:
            await page.goto(url)
            title = await page.title()
            return title

    assert 'Playwright' in asyncio.run(get_title(url='https://playwright.dev/'))


async def _test_renew(headed=True):
    @asynccontextmanager
    async def gen_page():
        async with pw.pw_page(headed=headed) as page:
            yield page

    gen_page_cm: pw.AsyncGeneratorContextManager[pw.Page] = gen_page

    async def run(gen: pw.AsyncGenerator[pw.Page]):
        for _ in range(5):
            page = await anext(gen)
            await page.goto('https://playwright.dev/')
            print(id(page))
            if 0:
                time.sleep(0.2)
        await gen.aclose()
        if 0:
            await asyncio.sleep(30)

    renewable: pw.AsyncGenerator[pw.Page] = pw.renewable(gen_page_cm, 3)
    await run(renewable)

    auto_renew: pw.AsyncGeneratorContextManagerAsyncGenerator[pw.Page] = pw.auto_renew(
        gen_page_cm, 3
    )
    async with auto_renew as agen:
        await run(agen)


def test_renew():
    asyncio.run(_test_renew(headed=False))


if __name__ == '__main__':
    asyncio.run(_test_renew())
