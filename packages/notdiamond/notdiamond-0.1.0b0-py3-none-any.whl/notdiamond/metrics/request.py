from typing import Dict

import requests

from notdiamond import settings
from notdiamond.exceptions import ApiError
from notdiamond.llms.provider import NDLLMProvider
from notdiamond.types import FeedbackRequestPayload


def feedback_request(
    session_id: str,
    llm_provider: NDLLMProvider,
    feedback_payload: Dict[str, int],
    notdiamond_api_key: str,
) -> bool:
    url = f"{settings.ND_BASE_URL}/v1/report/metrics/feedback"

    payload: FeedbackRequestPayload = {
        "session_id": session_id,
        "provider": llm_provider.prepare_for_request(),
        "feedback": feedback_payload,
    }

    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {notdiamond_api_key}",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        raise ApiError(f"ND API error for feedback: {e}")

    if response.status_code != 200:
        print(
            f"ND API feedback error: faild to report feedback with status {response.status_code}"
        )
        return False

    return True
