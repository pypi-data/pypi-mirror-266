import json
import requests
import traceback
from time import sleep

__author__ = 'swliu'


def query_model_list_api(api_access_token, url, num_retry: int = 3) -> list:
    """
    :param api_access_token: API access token.
    :param url: API endpoint
    :param num_retry: int
    :return: a list of large language models that are hosted by ASU
    """
    for i in range(num_retry):
        try:
            headers = _compute_headers(api_access_token=api_access_token)
            response = requests.get(url=url, headers=headers)
            models_dict = json.loads(response.content)
            models = models_dict["models"]
            return models
        except Exception as e:
            print(traceback.format_exc())
            sleep(1)
            continue
    return []


def compute_model_provider_mapper(models: list) -> dict:
    model_provider_mapper = {
        model["name"]: model["provider"]
        for model in models
    }
    return model_provider_mapper


def compute_model_list(models: list) -> set:
    model_list = {model["name"] for model in models}
    return model_list


def _compute_headers(api_access_token):
    headers = {
        "Accept": "application/json",
        "Authorization": f'Bearer {api_access_token}'
    }
    return headers
