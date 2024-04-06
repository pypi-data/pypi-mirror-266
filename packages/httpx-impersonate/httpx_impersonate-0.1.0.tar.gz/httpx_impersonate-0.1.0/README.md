![Python >= 3.8](https://img.shields.io/badge/python->=3.8-red.svg)
# Httpx impersonate

HTTPX with custom Client and AsyncClient that include randomized headers and SSL context.

## Table of Contents
* [Install](#install)
* [Features](#features)
* [Usage](#usage)

## Install
```python
pip install -U httpx_impersonate
```

## Features
- [x] Randomized Headers: headers that mimic popular web browsers and operating systems.
- [x] Randomized SSL Context: randomized ciphers for SSL connections.


## Usage

```python3
import httpx_impersonate

with httpx_impersonate.Client() as client:
    r = client.get("https://httpbin.org/anything")
    print(r)
```
**async**
```python3
import asyncio
import httpx_impersonate

async def get_url():
    async with httpx_impersonate.AsyncClient() as client:
        r = await client.get("https://httpbin.org/anything")
        print(r.json())

asyncio.run(get_url())
```
