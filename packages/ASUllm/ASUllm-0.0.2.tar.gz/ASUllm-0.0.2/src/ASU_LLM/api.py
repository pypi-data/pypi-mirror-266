import requests
import traceback
from time import sleep
from model_config import ModelConfig

__author__ = 'swliu'


def _compute_headers(access_token):
    headers = {
        "Accept": "application/json",
        "Authorization": f'Bearer {access_token}'
    }
    return headers


def _compute_payload(model: ModelConfig, query: str):
    payload = {
        # required
        "model_provider": model.provider,
        # required
        "model_name": model.name,
        # optional
        "model_params": model.model_params,
        # required
        "prompt": query,
        # optional
        "enable_search": model.enable_search,
        # optional
        "search_params": model.search_params
    }
    return payload


def query_llm(model: ModelConfig, query, num_retry: int = 3) -> str:
    for i in range(num_retry):
        try:
            payload = _compute_payload(model=model, query=query)
            headers = _compute_headers(model.access_token)
            response = requests.post(model.api_url, json=payload, headers=headers)
            response_text = response.json()['response']
            return response_text
        except Exception as e:
            print(traceback.format_exc())
            sleep(1)
            continue
    return ""


if __name__ == '__main__':
    model = ModelConfig(name="claudeinstant", provider="aws", enable_search=True)
    res = query_llm(model=model, query="Where is phoenix arizona?")
    print(res)
