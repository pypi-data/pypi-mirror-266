__all__ = ['SyncMLIClient', 'AsyncMLIClient']

import asyncio

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

import os
import json
import time
import threading
from typing import Iterator, AsyncIterator, Any, Unpack, Callable

from aiohttp import ClientSession, WSMsgType

from .params import LlamaCppParams, CandleParams, ModelParams


DEBUG = int(os.getenv('DEBUG', 0))
DONE = object()


def _async_to_sync_iter(loop: Any, async_iter: AsyncIterator, queue: asyncio.Queue) -> Iterator:
    t = threading.Thread(target=_run_coroutine, args=(loop, async_iter, queue))
    t.start()

    while True:
        if queue.empty():
            time.sleep(0.001)
            continue

        item = queue.get_nowait()

        if item is DONE:
            break

        yield item

    t.join()


def _run_coroutine(loop, async_iter, queue):
    loop.run_until_complete(_consume_async_iterable(async_iter, queue))


async def _consume_async_iterable(async_iter, queue):
    async for item in async_iter:
        await queue.put(item)

    await queue.put(DONE)


def async_to_sync_iter(async_iter: AsyncIterator) -> Callable:
    queue = asyncio.Queue()
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as e:
        loop = asyncio.new_event_loop()

    return _async_to_sync_iter(loop, async_iter, queue)


class BaseMLIClient:
    endpoint: str
    ws_endpoint: str


    def __init__(self, endpoint: str, ws_endpoint: str | None=None):
        # endpoint
        if not (endpoint.startswith('http://') or endpoint.startswith('https://')):
            # check if IPv4 address
            if endpoint.replace('.', '').replace(':', '').isnumeric():
                endpoint = 'http://' + endpoint
            else:
                endpoint = 'https://' + endpoint

        self.endpoint = endpoint

        # ws_endpoint
        if ws_endpoint is None:
            if endpoint.startswith('http://'):
                ws_endpoint = 'ws://' + endpoint[len('http://'):]
            elif endpoint.startswith('https://'):
                ws_endpoint = 'wss://' + endpoint[len('https://'):]
        
        self.ws_endpoint = ws_endpoint


class SyncMLIClient(BaseMLIClient):
    def __init__(self, endpoint: str, ws_endpoint: str | None=None):
        super().__init__(endpoint, ws_endpoint)
        self.async_client = AsyncMLIClient(endpoint, ws_endpoint)


    def text(self, **kwargs: Unpack[ModelParams]) -> str:
        data = asyncio.run(self.async_client.text(**kwargs))
        return data


    def chat(self, **kwargs: Unpack[ModelParams]) -> str:
        data = asyncio.run(self.async_client.chat(**kwargs))
        return data


    def iter_text(self, **kwargs: Unpack[ModelParams]) -> Iterator[str]:
        for chunk in async_to_sync_iter(self.async_client.iter_text(**kwargs)):
            yield chunk


    def iter_chat(self, **kwargs: Unpack[ModelParams]) -> Iterator[str]:
        for chunk in async_to_sync_iter(self.async_client.iter_chat(**kwargs)):
            yield chunk


class AsyncMLIClient(BaseMLIClient):
    async def text(self, **kwargs: Unpack[ModelParams]) -> str:
        url: str = f'{self.endpoint}/text/completions'

        # if kwargs.get('model_id') == 'echo/echo':
        #     return {'output': kwargs.get('prompt', 'echo')}

        async with ClientSession() as session:
            async with session.post(url, json=kwargs, verify_ssl=False) as resp:
                data = await resp.json()

        return data


    async def chat(self, **kwargs: Unpack[ModelParams]) -> str:
        url: str = f'{self.endpoint}/chat/completions'

        # if kwargs.get('model_id') == 'echo/echo':
        #     return {'output': 'echo'}

        async with ClientSession() as session:
            async with session.post(url, json=kwargs, verify_ssl=False) as resp:
                data = await resp.json()

        return data


    async def iter_text(self, **kwargs: Unpack[ModelParams]) -> AsyncIterator[str]:
        url: str = f'{self.ws_endpoint}/text/completions'

        # if kwargs.get('model_id') == 'echo/echo':
        #     yield kwargs.get('prompt', 'echo')
        #     return
        
        async with ClientSession() as session:
            async with session.ws_connect(url, verify_ssl=False) as ws:
                await ws.send_json(kwargs)

                async for msg in ws:
                    if msg.type == WSMsgType.PING:
                        await ws.pong(msg.data)
                    elif msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        yield data['chunk']
                    elif msg.type == WSMsgType.ERROR:
                        print(f'[ERROR] websocket closed with exception: {ws.exception()}')
                        break


    async def iter_chat(self, **kwargs: Unpack[ModelParams]) -> AsyncIterator[str]:
        url: str = f'{self.ws_endpoint}/chat/completions'

        # if kwargs.get('model_id') == 'echo/echo':
        #     yield 'echo'
        #     return
        
        async with ClientSession() as session:
            async with session.ws_connect(url, verify_ssl=False) as ws:
                await ws.send_json(kwargs)

                async for msg in ws:
                    if msg.type == WSMsgType.PING:
                        await ws.pong(msg.data)
                    elif msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        yield data['chunk']
                    elif msg.type == WSMsgType.ERROR:
                        print(f'[ERROR] websocket closed with exception: {ws.exception()}')
                        break
