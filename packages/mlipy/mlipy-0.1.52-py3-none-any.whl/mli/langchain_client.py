__all__ = ['LangchainMLIClient']

from typing import Iterator, AsyncIterator, Mapping, Any, Optional, Unpack

from langchain.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from langchain.schema.output import GenerationChunk

from .client import SyncMLIClient, AsyncMLIClient
from .params import ModelParams


class LangchainMLIClient(LLM):
    endpoint: str = 'http://127.0.0.1:5000/api/1.0'
    streaming: bool = False

    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return 'LangchainMLIClient'

    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            'endpoint': self.endpoint,
        }


    def _call(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Unpack[ModelParams],
    ) -> str:
        """Run the LLM on the given prompt and input."""
        # print('_call', self)
        sync_client = SyncMLIClient(self.endpoint)

        if self.streaming:
            output: list[str] | str = []

            for chunk in self._stream(prompt=prompt, stop=stop, run_manager=run_manager, **kwargs):
                output.append(chunk.text)

            output = ''.join(output)
        else:
            res: dict = sync_client.text(prompt=prompt, stop=stop, **kwargs)
            output: str = res['output']
        
            logprobs = None

            if run_manager:
                run_manager.on_llm_new_token(
                    token=output,
                    verbose=self.verbose,
                    log_probs=logprobs,
                )

        return output


    async def _acall(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Unpack[ModelParams],
    ) -> str:
        """Run the LLM on the given prompt and input."""
        # print('_acall', self)
        async_client = AsyncMLIClient(self.endpoint)

        if self.streaming:
            output: list[str] | str = []

            async for chunk in self._astream(prompt=prompt, stop=stop, run_manager=run_manager, **kwargs):
                output.append(chunk.text)

            output = ''.join(output)
        else:
            res: dict = await async_client.text(prompt=prompt, stop=stop, **kwargs)
            output: str = res['output']
            logprobs = None

            if run_manager:
                await run_manager.on_llm_new_token(
                    token=output,
                    verbose=self.verbose,
                    log_probs=logprobs,
                )

        return output


    def _stream(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Unpack[ModelParams],
    ) -> Iterator[GenerationChunk]:
        """Yields results objects as they are generated in real time.

        It also calls the callback manager's on_llm_new_token event with
        similar parameters to the LLM class method of the same name.
        """
        # print('_stream', self)
        sync_client = SyncMLIClient(self.endpoint)
        logprobs = None

        for text in sync_client.iter_text(prompt=prompt, stop=stop, **kwargs):
            chunk = GenerationChunk(
                text=text,
                generation_info={'logprobs': logprobs},
            )

            yield chunk

            if run_manager:
                run_manager.on_llm_new_token(
                    token=chunk.text,
                    verbose=self.verbose,
                    log_probs=logprobs,
                )


    async def _astream(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Unpack[ModelParams],
    ) -> AsyncIterator[GenerationChunk]:
        """Yields results objects as they are generated in real time.

        It also calls the callback manager's on_llm_new_token event with
        similar parameters to the LLM class method of the same name.
        """
        # print('_astream', self)
        async_client = AsyncMLIClient(self.endpoint)
        logprobs = None

        async for text in async_client.iter_text(prompt=prompt, stop=stop, **kwargs):
            chunk = GenerationChunk(
                text=text,
                generation_info={'logprobs': logprobs},
            )

            yield chunk

            if run_manager:
                await run_manager.on_llm_new_token(
                    token=chunk.text,
                    verbose=self.verbose,
                    log_probs=logprobs,
                )
