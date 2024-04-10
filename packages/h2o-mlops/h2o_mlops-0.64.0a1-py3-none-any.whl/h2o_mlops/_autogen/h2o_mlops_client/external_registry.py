import os
from typing import Callable

from _h2o_mlops_client.external_registry import api
from _h2o_mlops_client.external_registry import api_client
from _h2o_mlops_client.external_registry.exceptions import *  # noqa: F403, F401


class ApiClient(api_client.ApiClient):
    """Overrides update_params_for_auth method of the generated ApiClient classes"""

    def __init__(
        self, configuration: api_client.Configuration, token_provider: Callable[[], str]
    ):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(self, headers, querys, auth_settings, request_auth=None):
        token = self._token_provider()
        headers["Authorization"] = f"Bearer {token}"


class Client:
    """The composite client for accessing External registry services via adapters."""

    def __init__(self, host: str, token_provider: Callable[[], str]):
        configuration = api_client.Configuration(
            host=host,
        )

        if os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE"):
            configuration.ssl_ca_cert = os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")

        client = ApiClient(
            configuration=configuration,
            token_provider=token_provider,
        )
        self._external_registered_model_service = api.ExternalRegisteredModelServiceApi(
            api_client=client
        )
        self._external_registered_model_version_service = (
            api.ExternalRegisteredModelVersionServiceApi(api_client=client)
        )

    @property
    def external_registered_model_service(
        self,
    ) -> api.ExternalRegisteredModelServiceApi:
        return self._external_registered_model_service

    @property
    def external_registered_model_version_service(
        self,
    ) -> api.ExternalRegisteredModelVersionServiceApi:
        return self._external_registered_model_version_service
