import typer
from launchflow.cli.utils import print_response
from launchflow.cli.utyper import UTyper
from launchflow.exceptions import LaunchFlowRequestFailure

from launchflow.clients import async_launchflow_client_ctx

app = UTyper(help="Commands for managing accounts in LaunchFlow")


@app.command()
async def get(
    account_id: str = typer.Argument("The account ID to fetch. Format: `account_123`"),
):
    """Get information about a specific account."""
    async with async_launchflow_client_ctx() as client:
        try:
            account = await client.accounts.get(account_id)
            print_response("Account", account.model_dump())
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


@app.command()
async def list():
    """List accounts that you have access to."""
    async with async_launchflow_client_ctx() as client:
        try:
            accounts = await client.accounts.list()
            print_response(
                "Accounts",
                {
                    "accounts": [acc.model_dump() for acc in accounts],
                },
            )
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)
