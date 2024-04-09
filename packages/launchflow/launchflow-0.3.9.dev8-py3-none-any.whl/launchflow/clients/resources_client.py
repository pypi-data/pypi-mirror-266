from typing import Any, Dict, List, Optional

import httpx
from launchflow.clients.response_schemas import OperationResponse, ResourceResponse
from launchflow.config import config
from launchflow.exceptions import LaunchFlowRequestFailure, ResourceProductMismatch


class ResourcesSyncClient:
    def __init__(self, http_client: httpx.Client):
        self.http_client = http_client

    def base_url(self, project_name: str, environment_name: str) -> str:
        return f"{config.settings.launch_service_address}/projects/{project_name}/environments/{environment_name}/resources"

    def get(
        self,
        project_name: str,
        environment_name: str,
        resource_name: str,
        product_name_to_validate: Optional[str] = None,
    ):
        url = f"{self.base_url(project_name, environment_name)}/{resource_name}"
        response = self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)

        resource_info = ResourceResponse.model_validate(response.json())

        # Validate product name matches if provided
        if (
            product_name_to_validate
            and resource_info.resource_product != product_name_to_validate
        ):
            raise ResourceProductMismatch(
                product_name_to_validate, resource_info.resource_product
            )

        return resource_info


class ResourcesAsyncClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    def base_url(self, project_name: str, environment_name: str) -> str:
        return f"{config.settings.launch_service_address}/projects/{project_name}/environments/{environment_name}/resources"

    async def create(
        self,
        project_name: str,
        environment_name: str,
        product_name: str,
        resource_name: str,
        create_args: Dict[str, Any],
    ):
        response = await self.http_client.post(
            f"{self.base_url(project_name, environment_name)}/{product_name}/{resource_name}",
            json=create_args,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 201:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())

    async def replace(
        self,
        project_name: str,
        environment_name: str,
        product_name: str,
        resource_name: str,
        create_args: Dict[str, Any],
    ):
        response = await self.http_client.put(
            f"{self.base_url(project_name, environment_name)}/{product_name}/{resource_name}",
            json=create_args,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 201:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())

    # NOTE: Product name is optional because its only used for opt-in validation.
    async def get(
        self,
        project_name: str,
        environment_name: str,
        resource_name: str,
        product_name_to_validate: Optional[str] = None,
    ):
        url = f"{self.base_url(project_name, environment_name)}/{resource_name}"
        response = await self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)

        resource_info = ResourceResponse.model_validate(response.json())

        # Validate product name matches if provided
        if (
            product_name_to_validate
            and resource_info.resource_product != product_name_to_validate
        ):
            raise ResourceProductMismatch(
                product_name_to_validate, resource_info.resource_product
            )

        return resource_info

    async def list(
        self, project_name: str, environment_name: str
    ) -> List[ResourceResponse]:
        url = self.base_url(project_name, environment_name)
        response = await self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return [
            ResourceResponse.model_validate(resource)
            for resource in response.json()["resources"]
        ]

    async def delete(
        self, project_name: str, environment_name: str, resource_name: str
    ):
        url = f"{self.base_url(project_name, environment_name)}/{resource_name}"
        response = await self.http_client.delete(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 202:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())
