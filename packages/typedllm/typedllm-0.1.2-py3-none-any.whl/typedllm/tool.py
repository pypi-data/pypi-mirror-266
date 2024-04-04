import inspect
from typing import Type, Callable, List, Optional
from pydantic import BaseModel, Field


class Tool(BaseModel):
    name: str = Field(description="The name of the tool")
    description: str = Field(description="A description of the tool")
    function: Optional[Callable[[BaseModel], str]] = Field(description="The function to call", default=None)
    parameter_type: Type[BaseModel] = Field(description="The type of the parameter for the function")

    def openai_tool_choice_json(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
            }
        }

    def openapi_json(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameter_type.model_json_schema()
            }
        }


StringClass = "a".__class__


def create_tool_from_function(
        function: Callable,
        name: str = None,
        description: str = None
) -> Tool:
    sig = inspect.signature(function)
    if sig.return_annotation != StringClass:
        raise ValueError("The return value of the tool function must be a string.")

    if len(sig.parameters.items()) != 1:
        raise ValueError("The tool function must have exactly one parameter.")

    parameter_key = list(sig.parameters.keys())[0]
    parameters_model = sig.parameters[parameter_key].annotation

    if name is None:
        name = function.__name__

    if description is None:
        doc = function.__doc__
        description = doc if doc is not None else f"Tool called {name}"

    return Tool(
        name=name,
        description=description,
        function=function,
        parameter_type=parameters_model
    )


def create_tool_from_model(
        model: Type[BaseModel],
        name: str = None,
        description: str = None
) -> Tool:
    if name is None:
        name = model.__name__

    if description is None:
        doc = model.__doc__
        description = doc if doc is not None else f"Tool called {name}"

    return Tool(
        name=name,
        description=description,
        function=None,
        parameter_type=model
    )


class ToolCollection(List[Tool]):
    def __init__(self, *args):
        super().__init__(args)

    def openapi_json(self):
        return [tool.openapi_json() for tool in self]

    def get_by_name(self, name: str) -> Tool:
        for tool in self:
            if tool.name == name:
                return tool
        raise ValueError(f"Tool with name {name} not found.")
