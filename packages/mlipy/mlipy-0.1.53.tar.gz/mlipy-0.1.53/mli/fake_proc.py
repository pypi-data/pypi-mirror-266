__all__ = ['FakePipeStream', 'FakeProc']

import asyncio
from random import randint


class FakePipeStream:
    def __init__(self, contenet: bytes):
        self.contenet = contenet
        self.i = 0

    
    def at_eof(self) -> bool:
        return self.i >= len(self.contenet)


    async def read(self, size: int | None=None) -> bytes:
        if size is None:
            return self.contenet

        s = randint(1, 10)
        data: bytes = self.contenet[self.i:self.i + s]
        self.i += s
        await asyncio.sleep(0.01)
        return data


class FakeProc:
    def __init__(self, stdout_contenet: bytes, stderr_contenet: bytes):
        self.stdout = FakePipeStream(stdout_contenet)
        self.stderr = FakePipeStream(stderr_contenet)
        self.pid = 2 ** 32 - 1


    async def communicate(self) -> tuple[bytes, bytes]:
        stdout: bytes = b''
        stderr: bytes = await self.stderr.read()
        return stdout, stderr
