import io
from typing import Any, Dict, List, Optional

import httpx
from launchflow.clients.response_schemas import OperationResponse, ServiceResponse
from launchflow.config import config
from launchflow.exceptions import LaunchFlowRequestFailure, ServiceProductMismatch


class ServicesAsyncClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    def base_url(self, project_name: str, environment_name: str) -> str:
        return f"{config.settings.launch_service_address}/projects/{project_name}/environments/{environment_name}/services"

    async def deploy(
        self,
        project_name: str,
        environment_name: str,
        product_name: str,
        service_name: str,
        tar_bytes: io.BytesIO,
        # TODO: add create args on client
        create_args: Dict[str, Any],
    ):
        response = await self.http_client.post(
            f"{self.base_url(project_name, environment_name)}/{product_name}/{service_name}",
            files={"source_tarball": ("source.tar.gz", tar_bytes, "application/zip")},
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
            # default timeout is 5 seconds, but submitting a build can take a while
            timeout=60,
        )
        if response.status_code != 201:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())

    # NOTE: Product name is optional because its only used for opt-in validation.
    async def get(
        self,
        project_name: str,
        environment_name: str,
        service_name: str,
        product_name_to_validate: Optional[str] = None,
    ):
        url = f"{self.base_url(project_name, environment_name)}/{service_name}"
        response = await self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)

        service_info = ServiceResponse.model_validate(response.json())

        # Validate product name matches if provided
        if (
            product_name_to_validate
            and service_info.service_product != product_name_to_validate
        ):
            raise ServiceProductMismatch(
                product_name_to_validate, service_info.service_product
            )

        return service_info

    async def list(
        self, project_name: str, environment_name: str
    ) -> List[ServiceResponse]:
        url = self.base_url(project_name, environment_name)
        response = await self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return [
            ServiceResponse.model_validate(service)
            for service in response.json()["services"]
        ]

    async def delete(self, project_name: str, environment_name: str, service_name: str):
        url = f"{self.base_url(project_name, environment_name)}/{service_name}"
        response = await self.http_client.delete(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 202:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())
