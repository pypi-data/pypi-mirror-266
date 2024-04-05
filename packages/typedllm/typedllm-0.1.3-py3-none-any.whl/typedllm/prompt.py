from typing import ClassVar, Optional
from langchain_core.runnables import RunnableLambda
from typedtemplate import TypedTemplate, BaseTemplateEngine


class TypedPrompt(TypedTemplate):
    template_engine: ClassVar[BaseTemplateEngine]
    template_file: ClassVar[Optional[str]] = None
    template_string: ClassVar[Optional[str]] = None

    @classmethod
    def to_runnable(cls):
        def __inner__(input_data: dict):
            template = cls(**input_data)
            return {
                "prompt": template.render(),
            }
        return RunnableLambda(func=__inner__)
