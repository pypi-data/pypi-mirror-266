from pydantic import BaseModel
from typedllm.tool import Tool, create_tool_from_function


def test_basic_tool_creation():
    class ArgType(BaseModel):
        value: int

    tool = Tool(
        name="test",
        description="test",
        function=lambda x: str(x+1),
        parameter_type=ArgType
    )

    result = tool.openapi_json()

    assert result == {
        "type": "function",
        "function": {
            "name": "test",
            "description": "test",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "title": "Value",
                        "type": "integer"
                    }
                },
                "title": "ArgType",
                "required": ["value"]
            }
        }
    }


def test_tool_creation_from_function():
    class ArgType(BaseModel):
        value: int

    def test_function(x: ArgType) -> str:
        return str(x.value+1)

    tool = create_tool_from_function(test_function)

    result = tool.openapi_json()

    assert result == {
        "type": "function",
        "function": {
            "name": "test_function",
            "description": "Tool called test_function",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "title": "Value",
                        "type": "integer"
                    }
                },
                "title": "ArgType",
                "required": ["value"]
            }
        }
    }
