from typing import Callable

import yarl

import h2o_mlops_client.deployer
import h2o_mlops_client.external_registry
import h2o_mlops_client.ingest
import h2o_mlops_client.model_monitoring
import h2o_mlops_client.storage


class Client:
    """The composite client for accessing all MLOps services."""

    def __init__(self, gateway_url: str, token_provider: Callable[[], str]) -> None:
        """Initializes MLOps client.

        Args:
            gateway_url: Base url where MLOps gRPC Gateway is accessible.
            token_provider: Function that returns access token. This is called with
                every requests and passed in 'Authorization' header as bearer token.
        Returns:
            New instance of MLOps client.
        """
        url = yarl.URL(gateway_url)
        self._storage = h2o_mlops_client.storage.Client(
            host=str(url / "storage"),
            token_provider=token_provider,
        )
        self._deployer = h2o_mlops_client.deployer.Client(
            host=str(url / "deployer"),
            token_provider=token_provider,
        )
        self._ingest = h2o_mlops_client.ingest.Client(
            host=str(url / "ingest"),
            token_provider=token_provider,
        )
        self._external_registry = h2o_mlops_client.external_registry.Client(
            host=str(url / "external_registry"),
            token_provider=token_provider,
        )
        self._model_monitoring = h2o_mlops_client.model_monitoring.Client(
            host=str(url / "model-monitoring"),
            token_provider=token_provider,
        )

    @property
    def storage(self) -> h2o_mlops_client.storage.Client:
        return self._storage

    @property
    def deployer(self) -> h2o_mlops_client.deployer.Client:
        return self._deployer

    @property
    def ingest(self) -> h2o_mlops_client.ingest.Client:
        return self._ingest

    @property
    def external_registry(self) -> h2o_mlops_client.external_registry.Client:
        return self._external_registry

    @property
    def model_monitoring(self) -> h2o_mlops_client.model_monitoring.Client:
        return self._model_monitoring
