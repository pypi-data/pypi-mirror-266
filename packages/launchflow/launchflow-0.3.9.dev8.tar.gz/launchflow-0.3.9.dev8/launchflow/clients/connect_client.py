import httpx
from launchflow.clients.response_schemas import (
    AWSConnectionInfoResponse,
    ConnectionInfoResponse,
    GCPConnectionInfoResponse,
)
from launchflow.config import config
from launchflow.exceptions import LaunchFlowRequestFailure


class CloudConectAsyncClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.url = f"{config.settings.launch_service_address}/cloud/connect"
        self.http_client = http_client

    async def status(self, account_id: str, include_aws_template_url: bool = False):
        response = await self.http_client.get(
            f"{self.url}?account_id={account_id}&include_aws_template_url={include_aws_template_url}",
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return ConnectionInfoResponse.model_validate(response.json())

    async def connect_gcp(self, account_id: str):
        response = await self.http_client.post(
            f"{self.url}/gcp?account_id={account_id}",
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return GCPConnectionInfoResponse.model_validate(response.json())

    async def connect_aws(self, account_id: str, aws_account_id: str):
        response = await self.http_client.post(
            f"{self.url}/aws?account_id={account_id}",
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
            json={"aws_account_id": aws_account_id},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return AWSConnectionInfoResponse.model_validate(response.json())
