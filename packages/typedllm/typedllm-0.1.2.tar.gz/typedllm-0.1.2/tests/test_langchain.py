from typing import Type
from typedllm import TypedPrompt, LLMSession, LLMRequest
from typedllm.langchain import execute_request


def test_basic_langchain(
        llmprompt: Type[TypedPrompt],
        llmsession: LLMSession,
        llmrequest: LLMRequest
):
    chain = (
        llmprompt.to_runnable() |
        llmsession.to_runnable() |
        llmrequest.to_runnable() |
        execute_request()
    )

    result = chain.invoke({
        "city": "New York City",
    })

    assert result is not None
