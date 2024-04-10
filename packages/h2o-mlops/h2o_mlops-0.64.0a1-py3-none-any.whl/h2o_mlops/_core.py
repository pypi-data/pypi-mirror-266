from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse

import h2o_authn
import h2o_discovery
import h2o_mlops_autogen

from h2o_mlops import _projects
from h2o_mlops import _runtimes


class Client:
    """Connect to and interact with H2O MLOps.

    Args:
        gateway_url: full URL of the MLOps gRPC Gateway to connect to
            (needed when passing a token_provider)
        h2o_cloud_url: full URL of the H2O Cloud to connect to
            (needed when passing a refresh_token)
        refresh_token: client refresh token retrieved from H2O Cloud
            (needed when passing a h2o_cloud_url)
        token_provider: authentication token to authorize access on H2O AI Cloud
            (needed when passing a gateway_url)

    Examples::

        ### Connect from H2O Cloud notebook
        ### (credentials are automatically discovered and used)

        mlops = h2o_mlops.Client()

        ### Connect with h2o_cloud_url and refresh_token

        mlops = h2o_mlops.Client(
            h2o_cloud_url="https://...",
            refresh_token="eyJhbGciOiJIUzI1N...",
        )

        ### Connect with gateway_url and token_provider

        # 1) set up a token provider with a refresh token from AI Cloud
        token_provider = h2o_authn.TokenProvider(
            refresh_token="eyJhbGciOiJIUzI1N...",
            client_id="python_client",
            token_endpoint_url="https://keycloak-server/auth/realms/..."
        )

        # 2) use the token provider to get authorization to connect to the
        # MLOps API
        mlops = h2o_mlops.Client(
            gateway_url="https://mlops-api.my.domain",
            token_provider=token_provider
        )
    """

    def __init__(
        self,
        gateway_url: Optional[str] = None,
        token_provider: Optional[h2o_authn.TokenProvider] = None,
        h2o_cloud_url: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self._backend = None
        self._discovery = None
        self._token_provider = None

        if gateway_url and token_provider:
            self._backend = h2o_mlops_autogen.Client(
                gateway_url=gateway_url,
                token_provider=token_provider,
            )
            return

        if h2o_cloud_url:
            self._h2o_cloud_url = urlparse(h2o_cloud_url)
            self._discovery = h2o_discovery.discover(h2o_cloud_url)
        else:
            self._discovery = h2o_discovery.discover()

        self._token_provider = h2o_authn.TokenProvider(
            refresh_token=refresh_token or os.getenv("H2O_CLOUD_CLIENT_PLATFORM_TOKEN"),
            issuer_url=self._discovery.environment.issuer_url,
            client_id=self._discovery.clients["platform"].oauth2_client_id,
        )

        self._backend = h2o_mlops_autogen.Client(
            gateway_url=self._discovery.services["mlops-api"].uri,
            token_provider=self._token_provider,
        )

    @property
    def projects(self) -> _projects.MLOpsProjects:
        """Interact with Projects in H2O MLOps"""
        return _projects.MLOpsProjects(self)

    @property
    def runtimes(self) -> _runtimes.MLOpsRuntimes:
        """Interact with Scoring Runtimes in H2O MLOps"""
        return _runtimes.MLOpsRuntimes(self)

    def _get_username(self, user_id: str) -> str:
        """Get user display name from internal ID."""
        return self._backend.storage.user.get_user(
            h2o_mlops_autogen.StorageGetUserRequest(id=user_id)
        ).user.username
