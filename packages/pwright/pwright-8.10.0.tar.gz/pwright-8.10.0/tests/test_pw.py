from contextlib import contextmanager
import time

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

    gen_page_cm: pw.GeneratorContextManager[pw.Page] = gen_page

    def run(gen: pw.Generator[pw.Page]):
        for _ in range(5):
            page = next(gen)
            page.goto('https://playwright.dev/')
            print(id(page))
            if 0:
                time.sleep(0.2)
        gen.close()
        if 0:
            time.sleep(30)

    renewable: pw.Generator[pw.Page] = pw.renewable(gen_page_cm, 3)
    run(renewable)

    auto_renew: pw.GeneratorContextManagerGenerator[pw.Page] = pw.auto_renew(gen_page_cm, 3)
    with auto_renew as gen:
        run(gen)


def test_renew():
    _test_renew(headed=False)


if __name__ == '__main__':
    _test_renew()
