import httpx
from launchflow.clients.response_schemas import AccountResponse
from launchflow.config import config
from launchflow.exceptions import LaunchFlowRequestFailure


class AccountsAsyncClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.url = f"{config.settings.account_service_address}/accounts"

    async def list(self):
        response = await self.http_client.get(
            self.url,
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return [
            AccountResponse.model_validate(account)
            for account in response.json()["accounts"]
        ]

    async def get(self, account_id: str):
        response = await self.http_client.get(
            f"{self.url}/{account_id}",
            headers={"Authorization": f"Bearer {config.get_access_token()}"},
        )
        if response.status_code != 200:
            raise LaunchFlowRequestFailure(response)
        return AccountResponse.model_validate(response.json())
