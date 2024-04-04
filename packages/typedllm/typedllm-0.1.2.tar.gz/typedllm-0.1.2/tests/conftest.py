import os
import pytest

from typedllm import LLMModel, TypedPrompt, LLMSession, LLMRequest
from typedtemplate import JinjaTemplateEngine
from pydantic import Field


@pytest.fixture(name="openai_key")
def get_openai_key() -> str:
    return os.getenv("OPENAI_API_KEY")


@pytest.fixture(name="model")
def fixture_model(openai_key: str) -> LLMModel:
    return LLMModel(
        name="gpt-4",
        api_key=openai_key,
    )


@pytest.fixture(name="prompt")
def get_prompt_value():
    return {
        "system": "You are an AI assistant. You must respond to questions and follow all instructions.",
        "prompt": "Please respond with just 'Hi' to this message"
    }


@pytest.fixture(name="hi_acompletion")
def hi_acompletion():
    return {"choices": [{"text": "Hi"}]}


@pytest.fixture(name="jinja_engine")
def get_template_engine():
    return JinjaTemplateEngine()


@pytest.fixture(name="llmprompt")
def get_prompt(jinja_engine: JinjaTemplateEngine):
    class PromptTemplate(TypedPrompt):
        template_engine = jinja_engine
        template_string = "What year was {{ city }} founded?"
        city: str = Field(description="The city to use in the prompt")

    return PromptTemplate


@pytest.fixture(name="llmsession")
def get_session(model: LLMModel) -> LLMSession:
    return LLMSession(
        model=model,
        verbose=True,
    )


@pytest.fixture(name="llmrequest")
def get_request():
    return LLMRequest(force_text_response=True)
