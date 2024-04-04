try:
    from langchain_core.runnables import RunnableLambda
except ImportError:
    raise ImportError("Please install langchain-core to use this module. Run `pip install typedllm[langchain]`.")

from .client import llm_request, async_llm_request
from .models import LLMUserMessage


def execute_request() -> RunnableLambda:
    async def __afunc__(input_data: dict):
        session = input_data.get("session")
        request = input_data.get("request")
        request.message = LLMUserMessage(
            content=input_data.get("prompt")
        )
        new_session, response = await async_llm_request(session, request)
        return {
            "session": new_session,
            "response": response,
        }

    def __func__(input_data: dict):
        session = input_data.get("session")
        request = input_data.get("request")
        prompt = input_data.get("prompt")
        request.message = LLMUserMessage(content=prompt)
        new_session, response = llm_request(session, request)
        return {
            "session": new_session,
            "response": response,
        }

    return RunnableLambda(func=__func__, afunc=__afunc__)
