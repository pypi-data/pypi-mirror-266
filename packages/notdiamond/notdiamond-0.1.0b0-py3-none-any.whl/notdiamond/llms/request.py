import json
from typing import Dict, List, Optional, Union

import requests

from notdiamond import settings
from notdiamond.exceptions import ApiError
from notdiamond.llms.provider import NDLLMProvider
from notdiamond.metrics.metric import NDMetric
from notdiamond.prompts.hash import nd_hash
from notdiamond.prompts.prompt import NDChatPromptTemplate, NDPromptTemplate
from notdiamond.types import ModelSelectRequestPayload


def model_select(
    prompt_template: Optional[Union[NDPromptTemplate, NDChatPromptTemplate]],
    llm_providers: List[NDLLMProvider],
    metric: NDMetric,
    notdiamond_api_key: str,
    max_model_depth: int,
    preference_weights: Optional[Dict[str, float]] = None,
    preference_id: Optional[str] = None,
):
    """
    This endpoint receives the prompt and routing settings, and makes a call to the NotDiamond API.
    It returns the best fitting LLM to call and a session ID that can be used for feedback.

    Parameters:
        prompt_template (Optional[Union[NDPromptTemplate, NDChatPromptTemplate]]): prompt template for the LLM call
        llm_providers (List[NDLLMProvider]): a list of available LLM providers that the router can decide from
        metric (NDMetric): metric based off which the router makes the decision. As of now only 'accuracy' supported.
        notdiamond_api_key (str): API key generated via the NotDiamond dashboard.
        max_model_depth (int): if your top recommended model is down, specify up to which depth of routing you're willing to go.
        preference_weights (Optional[Dict[str, float]], optional): Define the quality, cost and latency weights of importance
                                                                    for the router. Defaults to None.
        preference_id (Optional[str], optional): The ID of the router preference that was configured via the Dashboard.
                                                    Defaults to None.

    Returns:
        tuple(NDLLMProvider, string): returns a tuple of the chosen NDLLMProvider to call and a session ID string.
                                        In case of an error the LLM defaults to None and the session ID defaults
                                        to 'NO-SESSION-ID'.

    Raises:
        ApiError: the NotDiamond API throws an error. To ensure this doesn't break your code, make sure to set a default model as
                    as fallback on the NDLLM class.
    """
    url = f"{settings.ND_BASE_URL}/v1/optimizer/modelSelect"

    payload: ModelSelectRequestPayload = {
        "prompt_template": prompt_template.template,
        "formatted_prompt": nd_hash(prompt_template.format()),
        "components": prompt_template.prepare_for_request(),
        "llm_providers": [
            llm_provider.prepare_for_request()
            for llm_provider in llm_providers
        ],
        "metric": metric.metric,
        "max_model_depth": max_model_depth,
    }

    if preference_weights is not None:
        payload["preference_weights"] = preference_weights
    if preference_id is not None:
        payload["preference_id"] = preference_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {notdiamond_api_key}",
    }

    try:
        response = requests.post(
            url, data=json.dumps(payload), headers=headers
        )
    except Exception as e:
        raise ApiError(f"ND API error for modelSelect: {e}")

    if response.status_code == 200:
        response_json = response.json()

        providers = response_json["providers"]
        session_id = response_json["session_id"]

        # TODO: make use of full providers list in the future and rest of params returned
        top_provider = providers[0]

        best_llm = list(
            filter(
                lambda x: (x.model == top_provider["model"])
                & (x.provider == top_provider["provider"]),
                llm_providers,
            )
        )[0]
        return best_llm, session_id
    else:
        if response.status_code == 401:
            print(
                f"ND API error: {response.status_code}. Make sure you have a valid NotDiamond API Key."
            )
        else:
            print(f"ND API error: {response.status_code}")
        return None, "NO-SESSION-ID"


def report_latency(
    session_id: str,
    llm_provider: NDLLMProvider,
    tokens_per_second: float,
    notdiamond_api_key: str,
):
    """
    This method makes an API call to the NotDiamond server to report the latency of an LLM call.
    It helps fine-tune our model router and ensure we offer recommendations that meet your latency expectation.

    This feature can be disabled on the NDLLM class level by setting `latency_tracking` to False.

    Parameters:
        session_id (str): the session ID that was returned from the `invoke` or `model_select` calls, so we know which
                            router call your latency report refers to.
        llm_provider (NDLLMProvider): specifying the LLM provider for which the latency is reported
        tokens_per_second (float): latency of the model call calculated based on time elapsed, input tokens, and output tokens
        notdiamond_api_key (str): NotDiamond API call used for authentication

    Returns:
        int: status code of the API call, 200 if it's success

    Raises:
        ApiError: if the API call to the NotDiamond backend fails, this error is raised
    """
    url = f"{settings.ND_BASE_URL}/v1/report/metrics/latency"

    payload = {
        "session_id": session_id,
        "provider": llm_provider.prepare_for_request(),
        "latency": {"tokens_per_second": tokens_per_second},
    }

    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {notdiamond_api_key}",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        raise ApiError(f"ND API error for report metrics latency: {e}")

    return response.status_code
