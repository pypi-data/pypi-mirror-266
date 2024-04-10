from dataclasses import dataclass

__author__ = 'swliu'


@dataclass(frozen=True)
class ModelConfig:
    name: str = ''
    provider: str = ''
    enable_search: bool = True
    api_url: str = ''
    access_token: str = None
    model_temperature: float = None
    model_max_tokens: int = None
    model_top_p = None
    model_top_k = None
    search_collection: str = 'asu'
    search_top_k: int = 3

    @property
    def model_params(self):
        if not self.access_token:
            raise AccessTokenMissing
        if not self.api_url:
            raise APIUrlMissing

        model_params = {}
        if self.model_temperature is not None:
            model_params["temperature"] = self.model_temperature
        if self.model_max_tokens is not None:
            model_params["max_tokens"] = self.model_max_tokens
        if self.model_top_p is not None:
            model_params["top_p"] = self.model_top_p
        if self.model_top_k is not None:
            model_params["top_k"] = self.model_top_k
        return model_params

    @property
    def search_params(self):
        if not self.access_token:
            raise AccessTokenMissing
        if not self.api_url:
            raise APIUrlMissing

        search_params = {}
        if self.enable_search is True:
            search_params["collection"] = self.search_collection
            search_params["top_k"] = self.search_top_k
        return search_params

    def __str__(self):
        if self.enable_search:
            return f"{self.name}_search_enabled"
        else:
            return self.name

    def __repr__(self):
        return f"Model: {self.name}\tSearch Enabled: {str(self.enable_search)}"


class AccessTokenMissing(Exception):
    def __init__(self):
        self.message = "API access token is missing."


class APIUrlMissing(Exception):
    def __init__(self):
        self.message = "API url token is missing."
