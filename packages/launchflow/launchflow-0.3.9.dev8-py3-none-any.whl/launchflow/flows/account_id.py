from typing import Optional

import beaupy
import rich
from launchflow.clients.client import LaunchFlowAsyncClient
from launchflow.config import config
from rich.progress import Progress, SpinnerColumn, TextColumn


async def get_account_id_from_config(
    client: LaunchFlowAsyncClient, account_id: Optional[str]
) -> str:
    if account_id is None:
        account_id = config.settings.default_account_id
    if account_id is None:
        account_id = await get_account_id_no_config(client, account_id)
    return account_id


async def get_account_id_no_config(
    client: LaunchFlowAsyncClient, account_id: Optional[str]
) -> str:
    if account_id is None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Fetching accounts...", total=None)
            accounts = await client.accounts.list()
            progress.remove_task(task)
        account_ids = [f"{a.id}" for a in accounts]
        selected_account = beaupy.select(account_ids, return_index=True, strict=True)
        account_id = account_ids[selected_account]
        rich.print(f"[pink1]>[/pink1] {account_id}")
    return account_id
