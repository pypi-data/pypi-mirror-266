import logging
import typing
from uuid import UUID

import httpx

from neos_common import error
from neos_common.authorization.signer import KeyPair
from neos_common.base import Action
from neos_common.client.base import NeosClient

logger = logging.getLogger(__name__)


class HubClient(NeosClient):
    """Identity Access Manager and Registry client."""

    @property
    def service_name(self) -> str:
        return "Hub"

    @property
    def known_errors(self) -> set[str]:
        return {
            "policy-not-found",
            "core-already-registered",
            "core-not-registered",
            "data-product-already-registered",
            "data-product-not-registered",
            "core-already-subscribed",
            "core-not-subscribed",
            "core-host-not-defined",
            "data-product-has-active-subscriptions",
            "core-service-user-not-defined",
            "user-manager-service-error",
        }

    def process_response_with_mapping(self, response: httpx.Response) -> dict:
        try:
            return self.process_response(response)
        except (error.ServiceApiError, error.UnhandledServiceApiError) as exc:
            if exc.type == "authorization-required":
                raise error.AuthorizationRequiredError(exc.details) from exc
            if exc.type == "invalid-authorization":
                raise error.InvalidAuthorizationError(exc.details) from exc
            if exc.type == "insufficient-permissions":
                raise error.InsufficientPermissionsError(exc.details) from exc
            if exc.type == "invalid-resource-format":
                raise error.InvalidResourceFormatError(exc.details) from exc
            if exc.type == "identity-access-manager-error":
                raise error.IdentityAccessManagerError(exc.details) from exc
            if exc.type == "signature-error":
                raise error.SignatureError(exc.details) from exc
            raise

    def __init__(
        self,
        host: str,
        token: typing.Union[str, None],
        key_pair: typing.Union[KeyPair, None],
        account: str,
        partition: str,
    ) -> None:
        # TODO(edgy): Use a better error
        assert token is not None or key_pair is not None  # noqa: S101

        self._token = token
        self._key_pair = key_pair

        self._account = account
        self._partition = partition

        self._host = host
        self._principals = None

    @property
    def token(self) -> typing.Union[str, None]:
        return self._token

    @property
    def key_pair(self) -> typing.Union[KeyPair, None]:
        return self._key_pair

    @property
    def iam_host(self) -> str:
        return f"{self._host}/iam"

    @property
    def registry_host(self) -> str:
        return f"{self._host}/registry"

    @property
    def validate_token_url(self) -> str:
        return f"{self.iam_host}/validate/token"

    @property
    def validate_signature_url(self) -> str:
        return f"{self.iam_host}/validate/signature"

    @property
    def core_url(self) -> str:
        return f"{self.registry_host}/core/{{identifier}}/announce"

    @property
    def data_product_url(self) -> str:
        return f"{self.registry_host}/core/{{identifier}}/data_product"

    @property
    def metadata_url(self) -> str:
        return f"{self.registry_host}/core/{{identifier}}/data_product/metadata"

    async def validate_token(
        self,
        principal: UUID,
        actions: list[Action],
        resources: list[str],
        *,
        return_allowed_resources: bool = False,
    ) -> tuple[UUID, list[str]]:
        r = await self._get(
            url=self.validate_token_url,
            params={
                "principal_id": principal,
                "action": [action.value for action in actions],
                "resource": resources,
                "return_allowed_resources": return_allowed_resources,
            },
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        data = self.process_response_with_mapping(r)
        logger.info(data)
        return data["principal_id"], data["resources"]

    async def validate_signature(
        self,
        access_key: str,
        auth_schema: str,
        scope: str,
        challenge: str,
        signed_challenge: str,
        actions: list[Action],
        resources: list[str],
        *,
        return_allowed_resources: bool = False,
    ) -> tuple[UUID, list[str]]:
        r = await self._get(
            url=self.validate_signature_url,
            params={
                "access_key_id": access_key,
                "auth_schema": auth_schema,
                "scope": scope,
                "challenge": challenge,
                "signed_challenge": signed_challenge,
                "action": [action.value for action in actions],
                "resource": resources,
                "return_allowed_resources": return_allowed_resources,
            },
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        data = self.process_response_with_mapping(r)

        return data["principal_id"], data["resources"]

    async def get_allowed_resources(
        self,
        principal_id: str,
        action: Action,
    ) -> list[str]:
        r = await self._get(
            f"{self.iam_host}/principal/{principal_id}/resource",
            params={"action": action.value},
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        d = self.process_response(r)

        return d["resources"]

    async def announce_core(self, host: str, version: str, core_identifier: str) -> None:
        r = await self._post(
            url=self.core_url.format(identifier=core_identifier),
            json={
                "host": host,
                "version": version,
            },
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        self.process_response(r)

    async def register_data_product(
        self,
        urn: str,
        name: str,
        metadata: dict,
        description: str,
        label: str,
        sanitized_name: str,
        data_product_type: str,
        engine: str,
        table: str,
        identifier: str,
        core_identifier: str,
        *,
        public: bool = True,
    ) -> None:
        json = {
            "urn": urn,
            "name": name,
            "metadata": metadata,
            "description": description,
            "label": label,
            "sanitized_name": sanitized_name,
            "data_product_type": data_product_type,
            "engine": engine,
            "table": table,
            "identifier": identifier,
            "public": public,
        }
        logger.info(
            f"Register data product request: {json}",
        )

        r = await self._post(
            url=self.data_product_url.format(identifier=core_identifier),
            json=json,
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        self.process_response(r)

    async def update_data_product_metadata(
        self,
        urn: str,
        metadata: dict,
        description: str,
        core_identifier: str,
    ) -> None:
        r = await self._post(
            url=self.metadata_url.format(identifier=core_identifier),
            json={
                "urn": urn,
                "metadata": metadata,
                "description": description,
            },
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        self.process_response(r)

    async def deregister_data_product(self, urn: str, core_identifier: str) -> None:
        r = await self._delete(
            url=self.data_product_url.format(identifier=core_identifier),
            json={
                "urn": urn,
            },
            headers={"X-Account": self._account, "X-Partition": self._partition},
        )

        self.process_response(r)
