"""NDLLM Class"""

import time
from typing import Any, Dict, Iterator, List, Optional, Union

from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.cohere import ChatCohere
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.messages import AIMessage, BaseMessage, BaseMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_together import Together
from litellm import token_counter

from notdiamond import settings
from notdiamond.exceptions import ApiError, MissingLLMProviders
from notdiamond.llms.provider import NDLLMProvider
from notdiamond.llms.request import model_select, report_latency
from notdiamond.metrics.metric import NDMetric
from notdiamond.prompts.prompt import NDChatPromptTemplate, NDPromptTemplate
from notdiamond.types import NDApiKeyValidator


class NDLLM(LLM):
    """
    Implementation of NDLLM class, the main class responsible for routing.
    The class inherits from Langchain's LLM class. Starting reference is from here:
    https://python.langchain.com/docs/modules/model_io/llms/custom_llm

    It's mandatory to have an API key set. If the api_key is not explicitly specified,
    it will check for NOTDIAMOND_API_KEY in the .env file.

    Raises:
        MissingLLMProviders: you must specify at least one LLM provider for the router to work
        ApiError: error raised when the NotDiamond API call fails.
                    Ensure to set a default LLM provider to not break the code.
    """

    api_key: str
    """
    API key required for making calls to NotDiamond.
    You can get an API key via our dashboard: https://app.notdiamond.ai
    If an API key is not set, it will check for NOTDIAMOND_API_KEY in .env file.
    """

    llm_providers: List[NDLLMProvider]
    """The list of LLM providers that are available to route between."""
    default: Optional[Union[NDLLMProvider, int, str]]
    """
    Set a default LLM provider, so in case anything goes wrong in the flow,
    as for example NotDiamond API call fails, your code won't break and you have
    a fallback model. There are various ways to configure a default model:

    - Integer, specifying the index of the default provider from the llm_providers list
    - String, similar how you can specify llm_providers, of structure 'provider_name/model_name'
    - NDLLMProvider, just directly specify the object of the provider
    """
    max_model_depth: int
    """
    If your top recommended model is down, specify up to which depth of routing you're willing to go.
    If max_model_depth is not set, it defaults to the length of the llm_providers list.
    If max_model_depth is set to 0, the init will fail.
    If the value is larger than the llm_providers list length, we reset the value to len(llm_providers).
    """
    latency_tracking: bool
    """
    Tracking and sending latency of LLM call to NotDiamond server as feedback, so we can improve our router.
    By default this is turned on, set it to False to turn off.
    """

    preference_weights: Optional[Dict[str, float]]
    """
    Define the quality, cost and latency weights of importance for the router.
    Each value in the dict must be between 0 and 1.

    The supported dictionary to define this field:
    {
        'quality': 0.8,
        'cost': 0.3,
        'latency': 0.5
    }

    Defaults to None.
    """
    preference_id: Optional[str]
    """The ID of the router preference that was configured via the Dashboard. Defaults to None."""

    def __init__(
        self,
        llm_providers: List[NDLLMProvider],
        api_key: Optional[str] = None,
        default: Optional[Union[NDLLMProvider, int, str]] = None,
        max_model_depth: Optional[int] = None,
        latency_tracking: bool = True,
        preference_weights: Optional[Dict[str, float]] = None,
        preference_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        if api_key is None:
            api_key = settings.NOTDIAMOND_API_KEY
        NDApiKeyValidator(api_key=api_key)

        if llm_providers is None or len(llm_providers) == 0:
            raise MissingLLMProviders(
                "No LLM provider specified. Specify at least one."
            )
        llm_providers = self._parse_llm_providers_data(llm_providers)

        if max_model_depth is None:
            max_model_depth = len(llm_providers)
        if max_model_depth == 0:
            raise ValueError("max_model_depth has to be bigger than 0.")

        if max_model_depth > len(llm_providers):
            print(
                "WARNING: max_model_depth cannot be bigger than the number of LLM providers."
            )
            max_model_depth = len(llm_providers)

        if preference_weights is not None:
            for k, v in preference_weights.items():
                if k not in ["cost", "quality", "latency"]:
                    raise ValueError(
                        "Invalid preference weights. Accepted keys: quality, cost, latency."
                    )
                if v < 0 or v > 1:
                    raise ValueError(
                        "Invalid preference weights. Value must be between 0 and 1."
                    )

        super(NDLLM, self).__init__(
            api_key=api_key,
            llm_providers=llm_providers,
            default=default,
            max_model_depth=max_model_depth,
            latency_tracking=latency_tracking,
            preference_weights=preference_weights,
            preference_id=preference_id,
            **kwargs,
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        address = hex(id(self))  # Gets the memory address of the object
        return f"<{class_name} object at {address}>"

    @property
    def default_llm_provider(self) -> Union[NDLLMProvider, None]:
        """
        Return the default LLM provider that's set on the NDLLM class.
        """
        if self.default is None:
            return None
        if isinstance(self.default, int):
            return self.llm_providers[int(self.default)]
        if isinstance(self.default, str):
            if self.default.isdigit():
                return self.llm_providers[int(self.default)]
            return NDLLMProvider.from_string(self.default)
        if isinstance(self.default, NDLLMProvider):
            return self.default
        return None

    @staticmethod
    def _parse_llm_providers_data(llm_providers: list) -> List[NDLLMProvider]:
        providers = []
        for llm_provider in llm_providers:
            if isinstance(llm_provider, NDLLMProvider):
                providers.append(llm_provider)
                continue
            parsed_provider = NDLLMProvider.from_string(llm_provider)
            providers.append(parsed_provider)
        return providers

    @property
    def _llm_type(self) -> str:
        return "NotDiamond LLM"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return "This function is deprecated for the latest LangChain version, use invoke instead"

    def invoke(
        self,
        prompt_template: Union[
            NDPromptTemplate,
            PromptTemplate,
            NDChatPromptTemplate,
            ChatPromptTemplate,
            str,
        ],
        input: Optional[Dict[str, Any]] = None,
        metric: NDMetric = NDMetric("accuracy"),
        **kwargs,
    ) -> AIMessage:
        """
        Function to invoke the LLM. Behind the scenes what happens:
        1. API call to NotDiamond backend to get the most suitable LLM for the given prompt
        2. Invoke the returned LLM client side
        3. Return the response

        Parameters:
            prompt_template (Union[ NDPromptTemplate, PromptTemplate, NDChatPromptTemplate, ChatPromptTemplate, str, ]):
                the prompt template defined by the user. It also supports Langchain prompt template types.
            input (Optional[Dict[str, Any]], optional): If the prompt_template contains variables, use input to specify
                                                        the values for those variables. Defaults to None, assuming no variables.
            metric (NDMetric, optional): Metric used by NotDiamond router to choose the best LLM.
                                            Defaults to NDMetric("accuracy").
            **kwargs: Any other arguments that are supported by Langchain's invoke method, will be passed through.

        Raises:
            ApiError: when the NotDiamond API fails

        Returns:
            AIMessage: type defined by Langchain, contains the response from the LLM.
        """
        prompt_template = self._prepare_prompt_template(prompt_template)

        if input is None:
            input = {}

        prompt_template.partial_variables = {
            **prompt_template.partial_variables,
            **input,
        }

        best_llm, session_id = model_select(
            prompt_template=prompt_template,
            llm_providers=self.llm_providers,
            metric=metric,
            notdiamond_api_key=self.api_key,
            max_model_depth=self.max_model_depth,
            preference_weights=self.preference_weights,
            preference_id=self.preference_id,
        )

        is_default = False
        if not best_llm:
            best_llm = self.default_llm_provider
            is_default = True

            if best_llm is None:
                raise ApiError(
                    "ND couldn't find a suitable model to call."
                    + "To avoid disruptions, we recommend setting a default fallback model or make max depth larger."
                )

        llm = self._llm_from_provider(best_llm)
        chain = prompt_template | llm

        try:
            if self.latency_tracking:
                result = self._invoke_with_latency_tracking(
                    session_id=session_id,
                    chain=chain,
                    llm_provider=best_llm,
                    is_default=is_default,
                    input=input,
                    **kwargs,
                )
            else:
                result = chain.invoke(input, **kwargs)
        except (ChatGoogleGenerativeAIError, ValueError) as e:
            if (
                isinstance(prompt_template, NDChatPromptTemplate)
                and best_llm.provider == "google"
            ):
                print(
                    f"WARNING: Google model's chat messages are violating requirements with error {e}."
                )
                print(
                    "If you see this message, means the NotDiamond API returned a Google model as the best option,"
                    + "but the LLM call will fail. So we will automatically fall back to a non-Google model, if possible."
                )

                non_google_llm = next(
                    (
                        llm_provider
                        for llm_provider in self.llm_providers
                        if llm_provider.provider != "google"
                    ),
                    None,
                )

                if non_google_llm is not None:
                    best_llm = non_google_llm
                    llm = self._llm_from_provider(best_llm)
                    chain = prompt_template | llm

                    if self.latency_tracking:
                        result = self._invoke_with_latency_tracking(
                            session_id=session_id,
                            chain=chain,
                            llm_provider=best_llm,
                            is_default=is_default,
                            input=input,
                            **kwargs,
                        )
                    else:
                        result = chain.invoke(input, **kwargs)
                else:
                    raise e
            else:
                raise e

        if isinstance(result, str):
            result = AIMessage(content=result)

        return result, session_id, best_llm

    def stream(self, input=None, **kwargs) -> Iterator[BaseMessageChunk]:
        prompt_template = self._prepare_prompt_template(prompt_template=input)
        best_llm, session_id = model_select(
            prompt_template=prompt_template,
            llm_providers=self.llm_providers,
            metric=NDMetric("accuracy"),
            notdiamond_api_key=self.api_key,
            max_model_depth=self.max_model_depth,
            preference_weights=self.preference_weights,
            preference_id=self.preference_id,
        )
        if not best_llm:
            best_llm = self.default_llm_provider

            if best_llm is None:
                raise ApiError(
                    "ND couldn't find a suitable model to call."
                    + " To avoid disruptions, we recommend setting a default fallback model or make max depth larger."
                )

        llm = self._llm_from_provider(best_llm)
        for chunk in llm.stream(input, **kwargs):
            yield chunk

    def model_select(
        self,
        prompt_template: Optional[
            Union[
                NDPromptTemplate,
                PromptTemplate,
                NDChatPromptTemplate,
                ChatPromptTemplate,
                str,
            ]
        ],
        input: Optional[Dict[str, Any]] = None,
        metric: NDMetric = NDMetric("accuracy"),
        **kwargs,
    ) -> tuple[str, Optional[NDLLMProvider]]:
        """
        This function calls the NotDiamond backend to fetch the most suitable model for the given prompt,
        and leaves the execution of the LLM call to the developer.

        Parameters:
            prompt_template (Union[ NDPromptTemplate, PromptTemplate, NDChatPromptTemplate, ChatPromptTemplate, str, ]):
                the prompt template defined by the user. It also supports Langchain prompt template types.
            input (Optional[Dict[str, Any]], optional): If the prompt_template contains variables, use input to specify
                                                        the values for those variables. Defaults to None, assuming no variables.
            metric (NDMetric, optional): Metric used by NotDiamond router to choose the best LLM.
                                            Defaults to NDMetric("accuracy").
            **kwargs: Any other arguments that are supported by Langchain's invoke method, will be passed through.

        Returns:
            tuple[str, Optional[NDLLMProvider]]: returns the session_id and the chosen LLM provider
        """
        prompt_template = self._prepare_prompt_template(prompt_template)

        if input is None:
            input = {}

        prompt_template.partial_variables = {
            **prompt_template.partial_variables,
            **input,
        }

        best_llm, session_id = model_select(
            prompt_template=prompt_template,
            llm_providers=self.llm_providers,
            metric=metric,
            notdiamond_api_key=self.api_key,
            max_model_depth=self.max_model_depth,
            preference_weights=self.preference_weights,
            preference_id=self.preference_id,
        )

        if not best_llm and self.default is not None:
            print("ND API error. Falling back to default provider.")
            best_llm = self.default_llm_provider

        return session_id, best_llm

    def _invoke_with_latency_tracking(
        self,
        session_id: str,
        chain: Any,
        llm_provider: NDLLMProvider,
        input: Optional[Dict[str, Any]] = {},
        is_default: bool = True,
        **kwargs,
    ):
        if session_id in ("NO-SESSION-ID", "") and not is_default:
            raise ApiError(
                "ND session_id is not valid for latency tracking. Please check the API response."
            )

        start_time = time.time()
        result = chain.invoke(input, **kwargs)
        end_time = time.time()

        if isinstance(result, str):
            result = AIMessage(content=result)

        tokens_completed = token_counter(
            model=llm_provider.model,
            messages=[{"role": "assistant", "content": result.content}],
        )
        tokens_per_second = tokens_completed / (end_time - start_time)

        report_latency(
            session_id=session_id,
            llm_provider=llm_provider,
            tokens_per_second=tokens_per_second,
            notdiamond_api_key=self.api_key,
        )

        return result

    @staticmethod
    def _llm_from_provider(provider: NDLLMProvider) -> Any:
        if provider.provider == "openai":
            return ChatOpenAI(
                openai_api_key=provider.api_key,
                model_name=provider.model,
                **provider.kwargs,
            )
        if provider.provider == "anthropic":
            return ChatAnthropic(
                anthropic_api_key=provider.api_key,
                model=provider.model,
                **provider.kwargs,
            )
        if provider.provider == "google":
            return ChatGoogleGenerativeAI(
                google_api_key=provider.api_key,
                model=provider.model,
                convert_system_message_to_human=True,
                **provider.kwargs,
            )
        if provider.provider == "cohere":
            return ChatCohere(
                cohere_api_key=provider.api_key,
                model=provider.model,
                **provider.kwargs,
            )
        if provider.provider == "mistral":
            return ChatMistralAI(
                mistral_api_key=provider.api_key,
                model=provider.model,
                **provider.kwargs,
            )
        if provider.provider == "togetherai":
            provider_settings = settings.PROVIDERS.get(provider.provider, None)
            model_prefixes = provider_settings.get("model_prefix", None)
            model_prefix = model_prefixes.get(provider.model, None)

            model = provider.model
            if model_prefix is not None:
                model = f"{model_prefix}/{provider.model}"
            print(f"MODEL: {model}")
            return Together(
                together_api_key=provider.api_key,
                model=model,
                **provider.kwargs,
            )
        raise ValueError(f"Unsupported provider: {provider.provider}")

    @staticmethod
    def _prepare_prompt_template(
        prompt_template,
    ) -> Union[NDPromptTemplate, NDChatPromptTemplate]:
        if isinstance(prompt_template, NDPromptTemplate) or isinstance(
            prompt_template, NDChatPromptTemplate
        ):
            return prompt_template
        if isinstance(prompt_template, str):
            return NDPromptTemplate(template=prompt_template)
        if isinstance(prompt_template, PromptTemplate):
            return NDPromptTemplate.from_langchain_prompt_template(
                prompt_template
            )
        if isinstance(prompt_template, ChatPromptTemplate):
            return NDChatPromptTemplate.from_langchain_chat_prompt_template(
                prompt_template
            )
        if isinstance(prompt_template, list):
            if all(isinstance(pt, BaseMessage) for pt in prompt_template):
                return NDChatPromptTemplate.from_messages(prompt_template)
        raise ValueError(
            f"Unsupported prompt_template type {type(prompt_template)}"
        )
