from typing import Callable

import typedllm
from typedllm.interop import litellm_request, async_litellm_request
from typedllm import LLMModel
import pytest


def acompletion_gen(response: dict) -> Callable:
    async def acompletion(*args, **kwargs):
        return response
    return acompletion


@pytest.mark.asyncio
async def test_basic_litellm_request(model: LLMModel, monkeypatch: pytest.MonkeyPatch, hi_acompletion: dict):
    monkeypatch.setattr(typedllm.interop, "acompletion", acompletion_gen(hi_acompletion))

    messages = [
        {"type": "message", "content": "Hi"}
    ]
    tools = []
    tool_choice = {}
    verbose = True

    response = await async_litellm_request(
        model.ssl_verify,
        model.name,
        model.max_retries,
        model.api_key,
        messages,
        tools,
        tool_choice,
        verbose,
        model.headers,
        model.organization,
        model.api_base
    )
    assert response == hi_acompletion, "Response should be the same as the fixture"


@pytest.mark.asyncio
async def test_no_msg_error(openai_key: str, model: LLMModel):
    messages = []
    tools = []
    tool_choice = {}
    verbose = True

    with pytest.raises(ValueError):
        await async_litellm_request(
            model.ssl_verify,
            model.name,
            model.max_retries,
            model.api_key,
            messages,
            tools,
            tool_choice,
            verbose,
            model.headers,
            model.organization,
            model.api_base
        )
        assert False, "Should not reach this point"
