from contextlib import contextmanager
import time
import typing as t

from pwright import pw


def test_pw_page():
    def get_title(*, url: str):
        with pw.pw_page() as page:
            page.goto(url)
            title = page.title()
            return title

    assert 'Playwright' in get_title(url='https://playwright.dev/')


def _test_renew(headed=True):
    @contextmanager
    def gen_page():
        with pw.pw_page(headed=headed) as page:
            yield page

    def run(gen: t.Generator[pw.Page, None, None]):
        for _ in range(5):
            page = next(gen)
            page.goto('https://playwright.dev/')
            print(id(page))
            if 0:
                time.sleep(0.2)
        gen.close()
        if 0:
            time.sleep(30)

    run(pw.renewable(gen_page, 3))
    with pw.auto_renew(gen_page, 3) as gen:
        run(gen)


def test_renew():
    _test_renew(headed=False)


if __name__ == '__main__':
    _test_renew()
