from abc import abstractmethod
from collections import deque
from typing import Any, Dict, List, Optional

from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.string import get_template_variables

from notdiamond.prompts.hash import nd_hash


class NDAbstractBase:
    def __init__(self, content):
        self.content = content

    @abstractmethod
    def optimize(self):
        pass

    @abstractmethod
    def get_module_type(self) -> Optional[str]:
        pass

    @abstractmethod
    def hash_content(self):
        return nd_hash(self.content)


class NDPrompt(NDAbstractBase):
    def __init__(self, prompt: str):
        self.prompt = prompt
        super(NDPrompt, self).__init__(self.prompt)

    def __call__(self):
        return self.prompt

    def optimize(self):
        print("Not yet implemented!")

    def get_module_type(self):
        return "NDPrompt"

    def get_component(self):
        return {
            "module_type": self.get_module_type(),
            "content": self.hash_content(),
        }


class NDContext(NDAbstractBase):
    def __init__(self, context: str):
        self.context = context
        super(NDContext, self).__init__(self.context)

    def __call__(self):
        return self.context

    def optimize(self):
        print("Not yet implemented!")

    def get_module_type(self):
        return "NDContext"

    def get_component(self):
        return {
            "module_type": self.get_module_type(),
            "content": self.hash_content(),
        }


class NDQuery(NDAbstractBase):
    def __init__(self, query: str):
        self.query = query
        super(NDQuery, self).__init__(self.query)

    def __call__(self):
        return self.query

    def optimize(self):
        print("Not yet implemented!")

    def get_module_type(self):
        return "NDQuery"

    def get_component(self):
        return {
            "module_type": self.get_module_type(),
            "content": self.hash_content(),
        }


class NDPromptTemplate(PromptTemplate):
    """Custom implementation of NDPromptTemplate
    Starting reference is from here:
    https://api.python.langchain.com/en/latest/prompts/langchain_core.prompts.prompt.PromptTemplate.html
    """

    def __init__(
        self,
        template: str,
        input_variables: Optional[List[str]] = None,
        partial_variables: Optional[Dict[str, Any]] = {},
    ):
        if input_variables is None:
            input_variables = get_template_variables(template, "f-string")

        if partial_variables:
            input_variables = []

        super(NDPromptTemplate, self).__init__(
            template=template,
            input_variables=input_variables,
            partial_variables=partial_variables,
        )

    @classmethod
    def from_langchain_prompt_template(cls, prompt_template: PromptTemplate):
        return cls(
            template=prompt_template.template,
            input_variables=prompt_template.input_variables,
            partial_variables=prompt_template.partial_variables,
        )

    def format(self, **kwargs: Any) -> str:
        inputs = {}
        for k, v in kwargs.items():
            if type(v) is not str:
                if issubclass(v.__class__, NDAbstractBase):
                    inputs[k] = v.content
            else:
                inputs[k] = v

        return super(NDPromptTemplate, self).format(**inputs)

    def optimize(self):
        print("Not yet implemented!")

    def prepare_for_request(self):
        components = {}
        for k, v in self.partial_variables.items():
            if issubclass(v.__class__, NDAbstractBase):
                components[k] = {
                    "module_type": v.get_module_type(),
                    "content": v.hash_content(),
                }
            elif type(v) is str:
                components[k] = {
                    "module_type": "NDPrompt",
                    "content": nd_hash(v),
                }
            else:
                raise ValueError(
                    f"Unsupported type in prompt template value: {type(v)}"
                )

        return components


def get_last_human_message(messages: List) -> str:
    user_query = []
    deque_messages = deque(messages)
    for message in reversed(deque_messages):
        if isinstance(message, HumanMessage):
            user_query.append(message.content)
            messages.remove(message)
        elif isinstance(message, AIMessage):
            break
    user_query = "\n ".join(user_query[::-1])
    return user_query


def get_system_and_context_messages(messages: List) -> (str, str):
    system_prompt, context_prompt = "", ""
    for message in messages:
        if (
            isinstance(message, SystemMessage)
            or isinstance(message, AIMessage)
            or isinstance(message, HumanMessage)
        ):
            if isinstance(message, SystemMessage):
                system_prompt += message.content + "\n "
            if isinstance(message, AIMessage) or isinstance(
                message, HumanMessage
            ):
                context_prompt += (
                    f"User: {message.content}\n "
                    if isinstance(message, HumanMessage)
                    else f"Assistant: {message.content}\n "
                )
        else:
            raise ValueError(f"Unsupported message type: {type(message)}")
    return system_prompt, context_prompt


class NDChatPromptTemplate(ChatPromptTemplate):
    """
    Starting reference is from
    here:https://api.python.langchain.com/en/latest/prompts/langchain_core.prompts.chat.ChatPromptTemplate.html
    """

    def __init__(
        self,
        messages: Optional[List] = None,
        input_variables: Optional[List[str]] = None,
        partial_variables: [str, Any] = dict,
    ):
        if messages is None:
            messages = []
        if partial_variables:
            input_variables = []

        super().__init__(
            messages=messages,
            input_variables=input_variables,
            partial_variables=partial_variables,
        )

    @property
    def template(self):
        message = """
        SYSTEM: {system_prompt}
        CONTEXT: {context_prompt}
        QUERY: {user_query}
        """
        return message

    @classmethod
    def from_langchain_chat_prompt_template(
        cls, chat_prompt_template: ChatPromptTemplate
    ):
        return cls(
            messages=chat_prompt_template.messages,
            input_variables=chat_prompt_template.input_variables,
            partial_variables=chat_prompt_template.partial_variables,
        )

    def format(self, **kwargs: Any) -> str:
        inputs = {}
        for k, v in kwargs.items():
            if type(v) is not str:
                if issubclass(v.__class__, NDAbstractBase):
                    inputs[k] = v.content
            else:
                inputs[k] = v

        return super(NDChatPromptTemplate, self).format(**inputs)

    def prepare_for_request(self):
        messages = self.format_messages(**self.partial_variables)
        user_query = get_last_human_message(messages)
        system_prompt, context_prompt = get_system_and_context_messages(
            messages
        )

        nd_prompt = NDPrompt(prompt=system_prompt)
        nd_context = NDContext(context=context_prompt)
        nd_query = NDQuery(query=user_query)
        components = {
            "system_prompt": nd_prompt.get_component(),
            "context_prompt": nd_context.get_component(),
            "user_query": nd_query.get_component(),
        }

        return components
