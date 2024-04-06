import pytest

import httpx_impersonate


def test_client_headers_():
    with httpx_impersonate.Client() as client:
        r = client.get("https://httpbin.org/anything")
        assert "headers" in r.json()


def test_client_ssl_context():
    with httpx_impersonate.Client() as client:
        r = client.get("https://tools.scrapfly.io/api/fp/ja3")
        assert "ja3_digest" in r.json()


@pytest.mark.asyncio
async def test_async_client_headers():
    async with httpx_impersonate.AsyncClient() as client:
        r = await client.get("https://httpbin.org/anything")
        assert "headers" in r.json()


@pytest.mark.asyncio
async def test_async_client_ssl_context():
    async with httpx_impersonate.AsyncClient() as client:
        r = await client.get("https://tools.scrapfly.io/api/fp/ja3")
        assert "ja3_digest" in r.json()


def test_random_ciphers():
    ciphers1 = httpx_impersonate.get_random_ssl_context().get_ciphers()
    ciphers2 = httpx_impersonate.get_random_ssl_context().get_ciphers()
    assert ciphers1 != ciphers2


def test_random_headers():
    headers1 = httpx_impersonate.get_random_headers()
    headers2 = httpx_impersonate.get_random_headers(http_version=2)
    assert headers1 != headers2
