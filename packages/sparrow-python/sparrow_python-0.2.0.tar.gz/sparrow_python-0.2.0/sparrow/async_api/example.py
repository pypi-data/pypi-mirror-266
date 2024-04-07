import asyncio

import aiofiles
import requests

async def fetch(url):
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url)
    print(f"Fetched {url} with status code {response.status_code}")

async def main():
    urls = [
        "https://www.example.com",
        "https://www.google.com",
        "https://www.github.com"
    ]
    tasks = [fetch(url) for url in urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
