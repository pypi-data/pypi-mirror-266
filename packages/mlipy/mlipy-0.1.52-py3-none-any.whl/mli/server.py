__all__ = [
    'MLIServer',
]

import asyncio

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

import os
import re
import json
import shlex
import base64
import argparse
import traceback
import subprocess
from weakref import WeakKeyDictionary
from tempfile import NamedTemporaryFile
from typing import AsyncIterator, TypedDict, Optional, Required, Unpack

from aiohttp import web, WSMsgType
from transformers import AutoTokenizer
from huggingface_hub import try_to_load_from_cache

from .fake_proc import FakeProc
from .params import Message, ModelParams, LlamaCppParams, CandleParams
from .formatter import format_messages


DEBUG = int(os.getenv('DEBUG', 0))

# TODO: improve
IS_CPU = True
IS_AMD = False
IS_NVIDIA = False

try:
    VGA = '\n'.join([n for n in subprocess.run(['lspci'], check=True, stdout=subprocess.PIPE).stdout.decode().splitlines() if 'VGA' in n])
    IS_CPU = False
    IS_AMD = 'AMD' in VGA
    IS_NVIDIA = not IS_AMD
except FileNotFoundError:
    IS_CPU = True
    IS_AMD = False
    IS_NVIDIA = False

print(f'{IS_CPU = }')
print(f'{IS_AMD = }')
print(f'{IS_NVIDIA = }')


class MLIServer:
    host: str
    port: int
    timeout: float
    candle_path: str
    llama_cpp_path: str
    app: web.Application
    lock: asyncio.Lock
    ws_proc_map: WeakKeyDictionary


    def __init__(self,
                 host: str='0.0.0.0',
                 port=5000,
                 timeout: float=90.0,
                 candle_path: str | None=None,
                 llama_cpp_path: str | None=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.candle_path = candle_path
        self.llama_cpp_path = llama_cpp_path
        self.app = web.Application()
        self.lock = asyncio.Lock()
        self.ws_proc_map = WeakKeyDictionary()


    # def _format_llama_cpp_cmd(self, executable: str, **kwargs: Unpack[LlamaCppParams]) -> str:
    def _format_llama_cpp_cmd(self, kwargs: LlamaCppParams) -> str:
        executable: str = kwargs['executable']
        cmd: list[str] | str = []
        
        if executable == 'main':
            prompt: str = kwargs.get('prompt')
            file: str = kwargs.get('file')
            image: str = kwargs.get('image')
            model: str = kwargs['model']
            model_id: str | None = kwargs.get('model_id')
            mmproj: str = kwargs.get('mmproj')
            chatml: bool | None = bool(kwargs.get('chatml', False))
            n_predict: int = int(kwargs.get('n_predict', -2))
            ctx_size: int = int(kwargs.get('ctx_size', 0))
            batch_size: int = int(kwargs.get('batch_size', 512))
            temp: float = float(kwargs.get('temp', 0.8))
            keep: int = int(kwargs.get('keep', 0))
            n_gpu_layers: int | None = kwargs.get('n_gpu_layers')
            top_k: int = int(kwargs.get('top_k', 40))
            top_p: float = float(kwargs.get('top_p', 0.9))
            min_p: float = float(kwargs.get('min_p', 0.1))
            repeat_last_n: int = int(kwargs.get('repeat_last_n', 64))
            repeat_penalty: float = float(kwargs.get('repeat_penalty', 1.0))
            penalize_nl: bool | None = kwargs.get('penalize_nl')
            no_display_prompt: float = float(kwargs.get('no_display_prompt', True))
            split_mode: str | None = kwargs.get('split_mode')
            tensor_split: str | None = kwargs.get('tensor_split')
            main_gpu: int | None = kwargs.get('main_gpu')
            seed: int | None = kwargs.get('seed')
            threads: int | None = kwargs.get('threads')
            grammar: str | None = kwargs.get('grammar')
            grammar_file: str | None = kwargs.get('grammar_file')
            cfg_negative_prompt: str | None = kwargs.get('cfg_negative_prompt')
            cfg_scale: float | None = kwargs.get('cfg_scale')
            rope_scaling: str | None = kwargs.get('rope_scaling')
            rope_scale: int | float | None = kwargs.get('rope_scale')
            rope_freq_base: int | float | None = kwargs.get('rope_freq_base')
            rope_freq_scale: int | float | None = kwargs.get('rope_freq_scale')
            cont_batching: bool | None = kwargs.get('cont_batching', False)
            prompt_to_file: bool = kwargs.get('prompt_to_file', False)
            image_to_file: bool = kwargs.get('image_to_file', False)
            
            # model_path
            if model_id:
                model_path = try_to_load_from_cache(repo_id=model_id, filename=model)
            else:
                model_path = model

            cmd.extend([
                f'{self.llama_cpp_path}/{executable}',
                '--model', model_path,
            ])

            if mmproj is not None:
                cmd.extend([
                    '--mmproj', mmproj,
                ])

            if chatml:
                cmd.extend([
                    '--chatml',
                ])

            if no_display_prompt:
                cmd.extend([
                    '--no-display-prompt',
                ])

            if IS_NVIDIA and split_mode is not None:
                cmd.extend([
                    '--split-mode', split_mode,
                ])

            if IS_NVIDIA and tensor_split is not None:
                cmd.extend([
                    '--tensor-split', tensor_split,
                ])

            if IS_NVIDIA and main_gpu is not None:
                cmd.extend([
                    '--main-gpu', main_gpu,
                ])

            if n_gpu_layers is not None:
                cmd.extend([
                    '--n-gpu-layers', n_gpu_layers,
                ])

            if seed is not None:
                cmd.extend([
                    '--seed', seed,
                ])
            
            if threads is not None:
                cmd.extend([
                    '--threads', threads,
                ])

            if grammar is not None:
                shell_grammar: str = shlex.quote(grammar)

                cmd.extend([
                    '--grammar', shell_grammar,
                ])
            
            if grammar_file is not None:
                cmd.extend([
                    '--grammar-file', grammar_file,
                ])

            if cfg_negative_prompt is not None:
                shell_cfg_negative_prompt: str = shlex.quote(cfg_negative_prompt)

                cmd.extend([
                    '--cfg-negative-prompt', shell_cfg_negative_prompt,
                ])
            
            if cfg_scale is not None:
                cmd.extend([
                    '--cfg-scale', cfg_scale,
                ])

            if rope_scaling is not None:
                cmd.extend([
                    '--rope-scaling', rope_scaling,
                ])

            if rope_scale is not None:
                cmd.extend([
                    '--rope-scale', rope_scale,
                ])

            if rope_freq_base is not None:
                cmd.extend([
                    '--rope-freq-base', rope_freq_base,
                ])

            if rope_freq_scale is not None:
                cmd.extend([
                    '--rope-freq-scale', rope_freq_scale,
                ])

            if cont_batching is not None:
                cmd.extend([
                    '--cont-batching',
                ])

            if prompt and not prompt_to_file:
                shell_prompt: str = shlex.quote(prompt)

                cmd.extend([
                    '--prompt', shell_prompt,
                ])

            if file and not prompt_to_file:
                cmd.extend([
                    '--file', file,
                ])

            if image and not image_to_file:
                cmd.extend([
                    '--image', image,
                ])

            if prompt_to_file:
                with NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
                    print(prompt)
                    f.write(prompt)
                    f.flush()

                cmd.extend([
                    '--file', f.name,
                ])

                kwargs['file'] = f.name

                if 'prompt' in kwargs:
                    del kwargs['prompt']

                if 'messages' in kwargs:
                    del kwargs['messages']

            if image_to_file:
                image_content: bytes = base64.b64decode(image)

                with NamedTemporaryFile('w+b', suffix='.jpg', delete=False) as f:
                    f.write(image_content)
                    f.flush()

                cmd.extend([
                    '--image', f.name,
                ])

                kwargs['image'] = f.name

                if 'image' in kwargs:
                    del kwargs['image']

            if penalize_nl:
                cmd.extend([
                    '--penalize-nl',
                ])

            cmd.extend([
                '--n-predict', n_predict,
                '--ctx-size', ctx_size,
                '--batch-size', batch_size,
                '--temp', temp,
                '--top-k', top_k,
                '--top-p', top_p,
                '--min-p', min_p,
                '--repeat-last-n', repeat_last_n,
                '--repeat-penalty', repeat_penalty,
                '--keep', keep,
                '--simple-io',
                '--log-disable',
            ])
        else:
            raise ValueError(f'Unsupported executable: {executable}')

        cmd = ' '.join(str(n) for n in cmd)
        return cmd


    def _format_candle_cmd(self, kwargs: CandleParams) -> str:
        executable: str = kwargs['executable']
        cmd: list[str] | str = []
        
        if executable == 'phi':
            prompt: str = kwargs['prompt']
            model: str = kwargs['model']
            cpu: bool = bool(kwargs.get('cpu', False))
            temperature: int = float(kwargs.get('temperature', 0.8))
            top_p: int = float(kwargs.get('top_p', 0.9))
            sample_len: int = int(kwargs.get('sample_len', 100))
            quantized: bool = bool(kwargs.get('quantized', False))

            # shell_prompt
            shell_prompt: str = shlex.quote(prompt)
            
            cmd.extend([
                f'{self.candle_path}/target/release/examples/phi',
            ])

            if cpu:
                cmd.extend([
                    '--cpu',
                ])

            cmd.extend([
                '--model', model,
                '--temperature', temperature,
                '--top-p', top_p,
                '--sample-len', sample_len,
            ])
            
            if quantized:
                cmd.extend([
                    '--quantized',
                ])

            cmd.extend([
                '--prompt', shell_prompt,
            ])
        elif executable == 'stable-lm':
            prompt: str = kwargs['prompt']
            model_id: str = kwargs.get('model_id', 'lmz/candle-stablelm-3b-4e1t')
            cpu: bool = bool(kwargs.get('cpu', False))
            temperature: int = float(kwargs.get('temperature', '0.8'))
            top_p: int = float(kwargs.get('top_p', '0.9'))
            sample_len: int = int(kwargs.get('sample_len', '100'))
            quantized: bool = bool(kwargs.get('quantized', False))
            use_flash_attn: bool = bool(kwargs.get('use_flash_attn', False))

            # shell_prompt
            shell_prompt: str = shlex.quote(prompt)
            
            cmd.extend([
                f'{self.candle_path}/target/release/examples/stable-lm',
            ])

            if cpu:
                cmd.extend([
                    '--cpu',
                ])

            cmd.extend([
                '--model-id', model_id,
                '--temperature', temperature,
                '--top-p', top_p,
                '--sample-len', sample_len,
            ])
            
            if quantized:
                cmd.extend([
                    '--quantized',
                ])
            
            if use_flash_attn:
                cmd.extend([
                    '--use-flash-attn',
                ])

            cmd.extend([
                '--prompt', shell_prompt,
            ])
        elif executable == 'llama':
            prompt: str = kwargs['prompt']
            model_id: str = kwargs.get('model_id')
            cpu: bool = bool(kwargs.get('cpu', False))
            temperature: int = float(kwargs.get('temperature', '0.8'))
            top_p: int = float(kwargs.get('top_p', '0.9'))
            sample_len: int = int(kwargs.get('sample_len', '100'))
            use_flash_attn: bool = bool(kwargs.get('use_flash_attn', False))

            # shell_prompt
            shell_prompt: str = shlex.quote(prompt)

            cmd.extend([
                f'{self.candle_path}/target/release/examples/llama',
            ])

            if cpu:
                cmd.extend([
                    '--cpu',
                ])

            if model_id:
                cmd.extend([
                    '--model-id', model_id
                ])

            cmd.extend([
                '--temperature', temperature,
                '--top-p', top_p,
                '--sample-len', sample_len,
            ])
            
            if use_flash_attn:
                cmd.extend([
                    '--use-flash-attn',
                ])

            cmd.extend([
                '--prompt', shell_prompt,
            ])
        elif executable == 'mistral':
            prompt: str = kwargs['prompt']
            model_id: str = kwargs.get('model_id')
            cpu: bool = bool(kwargs.get('cpu', False))
            temperature: int = float(kwargs.get('temperature', '0.8'))
            top_p: int = float(kwargs.get('top_p', '0.9'))
            sample_len: int = int(kwargs.get('sample_len', '100'))
            quantized: bool = bool(kwargs.get('quantized', False))
            use_flash_attn: bool = bool(kwargs.get('use_flash_attn', False))

            # shell_prompt
            shell_prompt: str = shlex.quote(prompt)

            cmd.extend([
                f'{self.candle_path}/target/release/examples/mistral',
            ])

            if cpu:
                cmd.extend([
                    '--cpu',
                ])

            if model_id:
                cmd.extend([
                    '--model-id', model_id
                ])

            cmd.extend([
                '--temperature', temperature,
                '--top-p', top_p,
                '--sample-len', sample_len,
            ])
            
            if quantized:
                cmd.extend([
                    '--quantized',
                ])

            if use_flash_attn:
                cmd.extend([
                    '--use-flash-attn',
                ])

            cmd.extend([
                '--prompt', shell_prompt,
            ])
        elif executable == 'quantized':
            prompt: str = kwargs['prompt']
            model: str = kwargs['model']
            model_id: str | None = kwargs.get('model_id')
            cpu: bool = bool(kwargs.get('cpu', False))
            temperature: int = float(kwargs.get('temperature', '0.8'))
            top_p: int = float(kwargs.get('top_p', '0.9'))
            sample_len: int = int(kwargs.get('sample_len', '100'))

            # shell_prompt
            shell_prompt: str = shlex.quote(prompt)

            if model_id:
                model_path = try_to_load_from_cache(repo_id=model_id, filename=model)
            else:
                model_path = model

            cmd.extend([
                f'{self.candle_path}/target/release/examples/quantized',
            ])

            if cpu:
                cmd.extend([
                    '--cpu',
                ])

            cmd.extend([
                '--model', model_path,
                '--temperature', temperature,
                '--top-p', top_p,
                '--sample-len', sample_len,
                '--prompt', shell_prompt,
            ])
        else:
            raise ValueError(f'Unsupported executable: {executable}')

        cmd = ' '.join(str(n) for n in cmd)
        return cmd


    def _format_cmd(self, msg: ModelParams) -> str:
        engine: str = msg['engine']
        cmd: str

        if engine == 'echo':
            cmd = ''
        elif engine == 'llama.cpp':
            cmd = self._format_llama_cpp_cmd(msg)
        elif engine == 'candle':
            cmd = self._format_candle_cmd(msg)
        else:
            raise ValueError(f'Unknown engine: {engine}')

        return cmd


    async def _run_shell_cmd(self, ws: web.WebSocketResponse | None, msg: ModelParams, cmd: str) -> AsyncIterator[str]:
        print(f'[DEBUG] _run_shell_cmd {ws} {msg} {cmd}')
        engine: str = msg['engine']
        file: str = msg.get('file')
        image: str = msg.get('image')
        prompt_to_file: str = msg.get('prompt_to_file', False)
        image_to_file: str = msg.get('image_to_file', False)
        stop: str = msg.get('stop', [])
        stdout: bytes = b''
        stderr: bytes = b''

        # build stop ngrams
        stop_ngrams: list[str] = []

        for n in stop:
            for i in range(1, len(n) + 1):
                ngram = n[:i]
                stop_ngrams.append(ngram)

        max_stop_len = max(len(n) for n in stop)

        print(f'{stop = }')
        print(f'{stop_ngrams = }')
        print(f'{max_stop_len = }')

        async with self.lock:
            try:
                async with asyncio.timeout(self.timeout):
                    # create new proc for model
                    if engine == 'echo':
                        prompt: str = msg['prompt']

                        proc = FakeProc(
                            stdout_contenet=prompt.encode(),
                            stderr_contenet=b'',
                        )
                    else:
                        proc = await asyncio.create_subprocess_shell(
                            cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                        )

                    print(f'{proc = }')

                    # associate ws with proc
                    if ws is not None:
                        self.ws_proc_map[ws] = proc
                    
                    # read rest of tokens
                    chunk = b''
                    buffer = b''
                    text = ''
                    stopped: bool = False

                    while not proc.stdout.at_eof():
                        # make sure `text` can be decoded
                        chunk = await proc.stdout.read(256)
                        buffer += chunk
                        stdout += chunk

                        try:
                            text = buffer.decode()
                        except UnicodeDecodeError as e:
                            print(f'[ERROR] buf.decode() exception: {e}')
                            continue

                        # check stopwords
                        found_stop_ngram: str | None = None
                        found_stop: str | None = None

                        for n in stop_ngrams:
                            if n in text:
                                print(f'stop_ngram {n = }')
                                found_stop_ngram = n

                                for m in stop:
                                    if m in text:
                                        found_stop = m
                                        print(f'stop {n = } {m = }')
                                        break

                        if found_stop_ngram:
                            if len(text) <= max_stop_len:
                                if found_stop:
                                    i = text.index(found_stop)
                                    text = text[:i]
                                    stopped = True
                                else:
                                    continue

                        # yield unicode text chunk
                        yield text

                        if stopped:
                            break

                        buffer = b''
                        await asyncio.sleep(0.1)

                    if stopped:
                        print(f'[INFO] stop word, trying to kill proc: {proc}')
            except asyncio.TimeoutError as e:
                print(f'[ERROR] timeout, trying to kill proc: {proc}, {e}')
            finally:
                ## read stderr at once
                # stderr = await proc.stderr.read()
                #
                try:
                    async with asyncio.timeout(1.0):
                        _, stderr = await proc.communicate()
                except TimeoutError:
                    stderr = b''

            try:
                proc.kill()
            except ProcessLookupError:
                pass

            os.system(f'pkill -9 -P {proc.pid}')
            proc = None

            stderr = stderr.decode()
            print('[DEBUG] stderr:')
            print(stderr)

        if prompt_to_file:
            os.remove(file)

        if image_to_file:
            os.remove(image)


    def _run_cmd(self, ws: web.WebSocketResponse | None, msg: ModelParams) -> AsyncIterator[str]:
        engine: str = msg['engine']
        executable: str = msg.get('executable', msg.get('kind'))
        msg['executable'] = executable
        cmd: str = self._format_cmd(msg)
        res: AsyncIterator[str]
        assert engine in ('echo', 'llama.cpp', 'candle')

        if (engine == 'echo' and 'model_id' in msg) or (engine == 'llama.cpp' and 'model_id' in msg) or (engine == 'candle' and executable == 'quantized' and 'model_id' in msg):
            model_id = msg['model_id']
            model = msg['model']

            if model_id:
                # check if model exists
                model_path = try_to_load_from_cache(repo_id=model_id, filename=model)

                if not isinstance(model_path, str):
                    raise ValueError(f'Unknown model: {model_path!r}')
                else:
                    print(f'[INFO] found model: {model_path!r}')
            else:
                # FIXME: check if model exists
                model_path = model
            
            res = self._run_shell_cmd(ws, msg, cmd)
        else:
            raise ValueError(f'Unknown engine: {engine!r}')

        return res


    async def _api_1_0_text_completions(self, ws: web.WebSocketResponse, msg: ModelParams):
        async for chunk in self._run_cmd(ws, msg):
            # if DEBUG:
            #     print(f'chunk: {chunk!r}')
            msg: dict = {'chunk': chunk}
            await ws.send_json(msg)

        await ws.close()


    def _convert_chat_to_text_message(self, msg: ModelParams) -> ModelParams:
        model_id: str = msg['model_id']
        creator_model_id: str = msg.get('creator_model_id', model_id)
        messages: list[Message] = msg['messages']
        prompt: str = format_messages(creator_model_id, messages)
        chat_msg: ModelParams = {**msg, 'prompt': prompt}
        return chat_msg


    async def post_api_1_0_text_completions(self, request):
        data: ModelParams = await request.json()
        text: list[str] | str = []

        async for chunk in self._run_cmd(None, data):
            # if DEBUG:
            #     print(f'chunk: {chunk!r}')
            text.append(chunk)

        text = ''.join(text)

        res: dict = {
            'output': text,
        }

        return web.json_response(res)


    async def post_api_1_0_chat_completions(self, request):
        data: ModelParams = await request.json()
        data = self._convert_chat_to_text_message(data)
        text: list[str] | str = []

        async for chunk in self._run_cmd(None, data):
            # if DEBUG:
            #     print(f'chunk: {chunk!r}')
            text.append(chunk)

        text = ''.join(text)

        res: dict = {
            'output': text,
        }

        return web.json_response(res)


    async def get_api_1_0_text_completions(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print(f'[INFO] websocket openned: {ws}')
        data: ModelParams

        try:
            async with asyncio.TaskGroup() as tg:
                async for msg in ws:
                    if msg.type == WSMsgType.PING:
                        await ws.pong(msg.data)
                    elif msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)

                        # quick model check
                        engine = data['engine']
                        model_id = data.get('model_id')
                        model = data.get('model')
                        
                        if engine not in ('echo', 'llama.cpp', 'candle'):
                            print(f'[ERROR] Unknown engine: {engine!r}, skipping')
                            break

                        if engine == 'llama.cpp':
                            if not model:
                                print(f'[ERROR] Unknown model: {model!r}, skipping')
                                break
                        elif engine == 'candle':
                            if not model_id or not model:
                                print(f'[ERROR] Unknown model_id {model_id!r} and model {model!r}, skipping')
                                break

                        # text completion
                        coro = self._api_1_0_text_completions(ws, data)
                        task = tg.create_task(coro)
                    elif msg.type == WSMsgType.ERROR:
                        print(f'[ERROR] websocket closed with exception: {ws.exception()}')
        except ExceptionGroup as e:
            traceback.print_exc()
            print(f'[ERROR] websocket ExceptionGroup: {e}')
        except Exception as e:
            traceback.print_exc()
            print(f'[ERROR] TaskGroup Exception: {e}')

        if ws in self.ws_proc_map:
            proc = self.ws_proc_map.pop(ws)
            print(f'[INFO] freed proc: {proc}')
            
            try:
                proc.kill()
            except ProcessLookupError:
                pass

            os.system(f'pkill -9 -P {proc.pid}')
            proc = None

        # close ws
        await ws.close()

        print(f'[INFO] websocket closed: {ws}')
        return ws


    async def get_api_1_0_chat_completions(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print(f'[INFO] websocket openned: {ws}')
        data: ModelParams

        try:
            async with asyncio.TaskGroup() as tg:
                async for msg in ws:
                    if msg.type == WSMsgType.PING:
                        await ws.pong(msg.data)
                    elif msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        data = self._convert_chat_to_text_message(data)
                        coro = self._api_1_0_text_completions(ws, data)
                        task = tg.create_task(coro)
                    elif msg.type == WSMsgType.ERROR:
                        print(f'[ERROR] websocket closed with exception: {ws.exception()}')
                        break
        except ExceptionGroup as e:
            traceback.print_exc()
            print(f'[ERROR] websocket ExceptionGroup: {e}')
        except Exception as e:
            traceback.print_exc()
            print(f'[ERROR] TaskGroup Exception: {e}')

        if ws in self.ws_proc_map:
            proc = self.ws_proc_map.pop(ws)
            print(f'[INFO] freed proc: {proc}')
            
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            
            os.system(f'pkill -9 -P {proc.pid}')
            proc = None

        # close ws
        await ws.close()

        print(f'[INFO] websocket closed: {ws}')
        return ws


    def get_routes(self):
        return [
            web.post('/api/1.0/text/completions', self.post_api_1_0_text_completions),
            web.post('/api/1.0/chat/completions', self.post_api_1_0_chat_completions),
            web.get('/api/1.0/text/completions', self.get_api_1_0_text_completions),
            web.get('/api/1.0/chat/completions', self.get_api_1_0_chat_completions),
        ]


    def run(self):
        routes = self.get_routes()
        self.app.add_routes(routes)
        web.run_app(self.app, host=self.host, port=self.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='server', description='Python llama.cpp HTTP Server')
    parser.add_argument('--host', help='http server host', default='0.0.0.0')
    parser.add_argument('--port', help='http server port', default=4000, type=int)
    parser.add_argument('--timeout', help='llama.cpp timeout in seconds', default=300.0, type=float)
    parser.add_argument('--candle-path', help='candle directory path', default='candle')
    parser.add_argument('--llama-cpp-path', help='llama.cpp directory path', default='llama.cpp')
    cli_args = parser.parse_args()

    server = MLIServer(
        host=cli_args.host,
        port=cli_args.port,
        timeout=cli_args.timeout,
        candle_path=os.path.expanduser(cli_args.candle_path),
        llama_cpp_path=os.path.expanduser(cli_args.llama_cpp_path),
    )

    server.run()