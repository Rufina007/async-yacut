import asyncio
import urllib.parse

import aiohttp

from . import app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
AUTH_HEADER = f'OAuth {app.config["DISK_TOKEN"]}'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_file_and_get_url(session, file):
    disk_path = 'app:/' + file.filename
    async with session.get(
        REQUEST_UPLOAD_URL,
        headers={'Authorization': AUTH_HEADER},
        params={'path': disk_path, 'overwrite': 'True'}
    ) as response:
        data = await response.json()
        upload_href = data['href']

    async with session.put(
        upload_href,
        data=file.read()
    ) as response:
        location = response.headers['Location']
        location = urllib.parse.unquote(location)
        location = location.replace('/disk', '')

    async with session.get(
        DOWNLOAD_LINK_URL,
        headers={'Authorization': AUTH_HEADER},
        params={'path': location}
    ) as response:
        data = await response.json()
        download_url = data['href']

    return file.filename, download_url


async def async_upload_files_to_disk(files):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for file in files:
            tasks.append(
                asyncio.ensure_future(
                    upload_file_and_get_url(session, file)
                )
            )
        results = await asyncio.gather(*tasks)
    return results
