import json
from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, Field
from .tool import Tool


class LLMMessage(BaseModel):

    def openai_json(self):
        raise NotImplementedError("This method must be implemented by the subclass.")


class LLMSystemMessage(LLMMessage):
    content: str

    def openai_json(self):
        return {
            "role": "system",
            "content": self.content
        }


class ImageURL(BaseModel):
    url: str = Field(description="The URL of the image. Can be a web URL or a Base64 encoded image.")


class LLMUserMessage(LLMMessage):
    content: Union[str, List[Union[str, ImageURL]]] = Field(
        description="The content of the message. Either a list of strings or Image URLs."
    )

    def openai_json(self):
        content = None
        if isinstance(self.content, str):
            content = self.content
        else:
            content = []
            for item in self.content:
                if isinstance(item, str):
                    content.append({
                        "type": "text",
                        "text": item
                    })
                else:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": item.url
                        }
                    })
        return {
            "role": "user",
            "content": content
        }


class LLMAssistantToolCall(LLMMessage):
    id: str = Field(description="The id of the tool call")
    tool: Tool
    args: str = Field(description="The arguments to the function")

    @property
    def arguments(self):
        argument_dict = json.loads(self.args)
        clz = self.tool.parameter_type
        argument = clz(**argument_dict)
        return argument

    def openai_json(self):
        return {
            "id": self.id,
            "function": {
                "name": self.tool.name,
                "arguments": self.args
            }
        }


class LLMAssistantMessage(LLMMessage):
    content: str = Field(
        description="The content of the message. Either a list of strings or Image URLs."
    )

    def openai_json(self):
        return {
            "role": "assistant",
            "content": self.content
        }


class LLMToolResultMessage(LLMMessage):
    id: str = Field(description="The id of the tool call")
    content: Any = Field(description="The result of the tool call")

    def openai_json(self):
        return {
            "role": "tool",
            "content": self.content,
            "tool_call_id": self.id
        }


class LLMModel(BaseModel):
    name: str = Field(
        description="The name of the model using the naming conventions of LiteLLM. "
                    "More info here: https://docs.litellm.ai/docs/providers"
    )
    api_key: str = Field(description="The API key for the model provider.")
    organization: Optional[str] = Field(
        description="The organization ID for the model provider.",
        default=None
    )
    api_base: Optional[str] = Field(
        description="If using a Proxy or 3rd Party vendor, this is the base url for requests.",
        default=None
    )
    headers: Optional[Dict[str, str]] = Field(
        description="Additional headers to include with the requests. "
                    "More info here: https://docs.litellm.ai/docs/providers/openai#using-helicone-proxy-with-litellm",
        default=None
    )
    max_retries: int = Field(
        default=3,
        description="The maximum number of retries for a step in the pipeline."
    )
    ssl_verify: bool = Field(
        description="Whether to verify the SSL certificate of the model provider.",
        default=True
    )


class LLMSession(BaseModel):
    model: Optional[LLMModel] = Field(description="The model used in the session", default=None)
    messages: List[LLMMessage] = Field(description="The messages in the session", default=[])
    tools: List[Tool] = Field(description="The tools available in the session", default=[])
    verbose: bool = Field(description="Whether to log verbose output", default=False)

    def merge(self, other: 'LLMSession') -> 'LLMSession':
        return LLMSession(
            model=self.model or other.model,
            messages=self.messages + other.messages,
            tools=self.tools + other.tools,
            verbose=self.verbose or other.verbose
        )

    def to_runnable(self):
        from langchain_core.runnables import RunnableLambda

        def __inner__(input_data: dict):
            input_data.pop("session", None)
            return {
                "session": self,
                **input_data
            }

        return RunnableLambda(func=__inner__)


class LLMRequest(BaseModel):
    message: Optional[LLMUserMessage] = Field(description="The prompt to use for the request", default=None)
    tool_results: List[LLMToolResultMessage] = Field(description="The tools to use for the request", default=[])
    tools: List[Tool] = Field(
        description="The tools to use for the request in addition to the session tools.",
        default=[]
    )
    required_tool: Optional[Tool] = Field(
        description="The tool that must be used for the request",
        default=None
    )
    force_text_response: bool = Field(
        description="Whether to force the response to be text.",
        default=False
    )

    def merge(self, other: 'LLMRequest') -> 'LLMRequest':
        return LLMRequest(
            message=self.message or other.message,
            tool_results=self.tool_results + other.tool_results,
            tools=self.tools + other.tools,
            required_tool=self.required_tool or other.required_tool,
            force_text_response=self.force_text_response or other.force_text_response
        )

    def to_runnable(self):
        from langchain_core.runnables import RunnableLambda

        def __inner__(input_data: dict):
            input_data.pop("request", None)
            return {
                "request": self,
                **input_data
            }

        return RunnableLambda(func=__inner__)


class LLMResponse(BaseModel):
    message: Optional[LLMAssistantMessage] = Field(description="The message from the assistant", default=None)
    tool_calls: List[LLMAssistantToolCall] = Field(description="The tools to use for the request", default=[])
    raw: BaseModel = Field(description="The raw response from the model provider")
