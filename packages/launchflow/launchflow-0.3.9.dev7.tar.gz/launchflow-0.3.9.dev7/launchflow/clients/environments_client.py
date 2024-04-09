import enum

import httpx
from launchflow.clients.response_schemas import (
    EnvironmentResponse,
    EnvironmentType,
    OperationResponse,
)
from launchflow.config import config
from launchflow.exceptions import LaunchFlowRequestFailure


class _CloudProvider(enum.Enum):
    AWS = "aws"
    GCP = "gcp"


class EnvironmentsSyncClient:
    def __init__(self, http_client: httpx.Client):
        self.http_client = http_client

    def base_url(self, project_name: str) -> str:
        return f"{config.settings.launch_service_address}/projects/{project_name}/environments"

    def _create(
        self,
        project_name: str,
        env_name: str,
        env_type: EnvironmentType,
        cloud_provider: _CloudProvider,
    ) -> OperationResponse:
        body = {
            "name": env_name,
            "environment_type": env_type.value,
        }
        response = self.http_client.post(
            f"{self.base_url(project_name)}/{cloud_provider.value}",
            json=body,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code not in [200, 201, 202]:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())

    def create_aws(
        self, project_name: str, env_name: str, env_type: EnvironmentType
    ) -> OperationResponse:
        return self._create(project_name, env_name, env_type, _CloudProvider.AWS)

    def create_gcp(
        self, project_name: str, env_name: str, env_type: EnvironmentType
    ) -> OperationResponse:
        return self._create(project_name, env_name, env_type, _CloudProvider.GCP)

    def get(self, project_name: str, env_name: str):
        url = f"{self.base_url(project_name)}/{env_name}"
        response = self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return EnvironmentResponse.model_validate(response.json())

    def list(self, project_name):
        response = self.http_client.get(
            self.base_url(project_name),
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return [
            EnvironmentResponse.model_validate(env)
            for env in response.json()["environments"]
        ]


class EnvironmentsAsyncClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    def base_url(self, project_name: str) -> str:
        return f"{config.settings.launch_service_address}/projects/{project_name}/environments"

    async def _create(
        self,
        project_name: str,
        env_name: str,
        env_type: EnvironmentType,
        cloud_provider: _CloudProvider,
    ) -> OperationResponse:
        body = {
            "name": env_name,
            "environment_type": env_type.value,
        }
        response = await self.http_client.post(
            f"{self.base_url(project_name)}/{cloud_provider.value}",
            json=body,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code not in [200, 201, 202]:
            raise LaunchFlowRequestFailure(response)
        return OperationResponse.model_validate(response.json())

    async def create_aws(
        self, project_name: str, env_name: str, env_type: EnvironmentType
    ) -> OperationResponse:
        return await self._create(project_name, env_name, env_type, _CloudProvider.AWS)

    async def create_gcp(
        self, project_name: str, env_name: str, env_type: EnvironmentType
    ) -> OperationResponse:
        return await self._create(project_name, env_name, env_type, _CloudProvider.GCP)

    async def get(self, project_name: str, env_name: str):
        url = f"{self.base_url(project_name)}/{env_name}"
        response = await self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return EnvironmentResponse.model_validate(response.json())

    async def list(self, project_name):
        response = await self.http_client.get(
            self.base_url(project_name),
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return [
            EnvironmentResponse.model_validate(env)
            for env in response.json()["environments"]
        ]
