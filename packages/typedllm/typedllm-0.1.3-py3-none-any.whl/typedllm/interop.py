from typing import List, Any, Dict, Optional
import httpx
import litellm
from litellm import acompletion, completion


def make_request(
    model_name: str,
    max_retries: int,
    api_key: str,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    tool_choice: Dict[str, Any],
    organization: Optional[str],
    api_base: Optional[str]
):
    if len(messages) == 0:
        raise ValueError("No messages provided")

    req = {
        "model": model_name,
        "messages": messages,
        "max_retries": max_retries,
        "api_key": api_key,
    }

    if len(tools) > 0:
        req["tools"] = tools
        req["tool_choice"] = tool_choice

    if organization:
        req["organization"] = organization
    if api_base:
        req["api_base"] = api_base

    return req


def pre_request_setup(
        ssl_verify: bool,
        verbose: bool,
        headers: Optional[Dict[str, str]]
):
    if not ssl_verify:
        litellm.client_session = httpx.Client(verify=False)

    if verbose:
        litellm.set_verbose = True

    if headers is not None:
        litellm.headers = headers


def post_request_cleanup(
    ssl_verify: bool,
    verbose: bool,
    headers: Optional[Dict[str, str]]
):
    if not ssl_verify:
        litellm.client_session = None  # reset to default. Might be unnecessary. Evaluate later.

    if headers is not None:
        litellm.headers = None  # reset to default. Might be unnecessary. Evaluate later.

    if verbose:
        litellm.set_verbose = False


def litellm_request(
        ssl_verify: bool,
        model_name: str,
        max_retries: int,
        api_key: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: Dict[str, Any],
        verbose: bool = False,
        headers: Optional[Dict[str, str]] = None,
        organization: Optional[str] = None,
        api_base: Optional[str] = None
) -> Any:
    req = make_request(
        model_name,
        max_retries,
        api_key,
        messages,
        tools,
        tool_choice,
        organization,
        api_base
    )
    pre_request_setup(ssl_verify, verbose, headers)
    response = completion(**req)
    post_request_cleanup(ssl_verify, verbose, headers)
    return response


async def async_litellm_request(
        ssl_verify: bool,
        model_name: str,
        max_retries: int,
        api_key: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: Dict[str, Any],
        verbose: bool = False,
        headers: Optional[Dict[str, str]] = None,
        organization: Optional[str] = None,
        api_base: Optional[str] = None
) -> Any:
    req = make_request(
        model_name,
        max_retries,
        api_key,
        messages,
        tools,
        tool_choice,
        organization,
        api_base
    )
    pre_request_setup(ssl_verify, verbose, headers)
    response = await acompletion(**req)
    post_request_cleanup(ssl_verify, verbose, headers)
    return response
