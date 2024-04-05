from .interop import litellm_request, async_litellm_request
from .tool import ToolCollection
from .models import (
    LLMSession,
    LLMRequest,
    LLMResponse,
    LLMAssistantMessage,
    LLMAssistantToolCall
)


async def async_llm_request(
        session: LLMSession,
        request: LLMRequest
) -> (LLMSession, LLMResponse):
    # TODO: Add support for a Memory Interface here.
    # Memory can be set as a configuration option and can be invoked here.
    messages = generate_message_json(
        *session.messages,
        *request.tool_results,
        request.message
    )
    tools, tool_choice = generate_tool_json(
        *session.tools, *request.tools,
        force_text_response=request.force_text_response,
        required_tool=request.required_tool
    )
    raw_response = await async_litellm_request(
        session.model.ssl_verify,
        session.model.name,
        session.model.max_retries,
        session.model.api_key,
        messages,
        tools.openapi_json(),
        tool_choice,
        verbose=session.verbose,
        headers=session.model.headers,
        organization=session.model.organization,
        api_base=session.model.api_base
    )
    response = extract_response_messages(raw_response, tools)

    # Add tool calls to session messsages
    if response.tool_calls and len(response.tool_calls) > 0:
        for tool_call in response.tool_calls:
            session.messages.append(tool_call)


    # Add messages to the session
    if response.message:
        session.messages.append(response.message)

    return session, response


def llm_request(
        session: LLMSession,
        request: LLMRequest
) -> (LLMSession, LLMResponse):
    # TODO: Add support for a Memory Interface here.
    # Memory can be set as a configuration option and can be invoked here.
    messages = generate_message_json(
        *session.messages,
        *request.tool_results,
        request.message
    )
    tools, tool_choice = generate_tool_json(
        *session.tools, *request.tools,
        force_text_response=request.force_text_response,
        required_tool=request.required_tool
    )
    raw_response = litellm_request(
        session.model.ssl_verify,
        session.model.name,
        session.model.max_retries,
        session.model.api_key,
        messages,
        tools.openapi_json(),
        tool_choice,
        verbose=session.verbose,
        headers=session.model.headers,
        organization=session.model.organization,
        api_base=session.model.api_base
    )
    response = extract_response_messages(raw_response, tools)

    # Add tool calls to session messsages
    if response.tool_calls and len(response.tool_calls) > 0:
        for tool_call in response.tool_calls:
            session.messages.append(tool_call)


    # Add messages to the session
    if response.message:
        session.messages.append(response.message)

    return session, response


def generate_message_json(*messages):
    return [msg.openai_json() for msg in messages]


def generate_tool_json(*tools, force_text_response=False, required_tool=None):
    tools = ToolCollection(*tools)
    if len(tools) == 0 or force_text_response:
        tool_choice = "none"
    elif required_tool:
        tool_choice = required_tool.openai_tool_choice_json()
    else:
        tool_choice = "auto"
    return tools, tool_choice


def extract_response_messages(res, tools: ToolCollection) -> LLMResponse:
    from litellm.utils import ModelResponse
    response: ModelResponse = res

    if len(response.choices) != 1:
        raise Exception("Invalid number of choices in response. Expect only one choice.")

    msg = response.choices[0].message

    if msg["role"] != "assistant":
        raise Exception("Invalid role in response")
    llm_msg = None
    if msg.content:
        llm_msg = LLMAssistantMessage(
            content=msg.content,
        )
    if not hasattr(msg, "tool_calls"):
        return LLMResponse(
            message=llm_msg,
            raw=response
        )
    tool_calls = []
    if len(msg.tool_calls) > 0:
        for tool_call in msg["tool_calls"]:
            tc = LLMAssistantToolCall(
                id=tool_call.id,
                tool=tools.get_by_name(tool_call.function.name),
                args=tool_call.function.arguments
            )
            tool_calls.append(tc)

    return LLMResponse(
        message=llm_msg,
        tool_calls=tool_calls,
        raw=response
    )
