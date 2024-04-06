from typing import Any, Literal

from browserforge.headers import Browser, HeaderGenerator  # type: ignore

BROWSERS = [
    Browser(name="chrome", min_version=123),
    # Browser(name='firefox', min_version=124),
    # Browser(name='edge', min_version=120),
    # Browser(name='safari', min_version=17),
]
HEADERS_GEN = HeaderGenerator(
    browser=BROWSERS,
    os=("windows", "macos", "linux", "android", "ios"),
    device=("desktop", "mobile"),
    # locale=('en-US'),
)


def get_random_headers(http_version: Literal[1, 2] = 1) -> Any:
    return HEADERS_GEN.generate(http_version=http_version)
