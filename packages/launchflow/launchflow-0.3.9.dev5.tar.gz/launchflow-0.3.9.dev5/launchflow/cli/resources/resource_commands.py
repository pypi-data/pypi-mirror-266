import typer
from launchflow.cli.constants import ENVIRONMENT_HELP, PROJECT_HELP
from launchflow.cli.utils import print_response
from launchflow.cli.utyper import UTyper
from launchflow.clients.response_schemas import OperationStatus
from launchflow.exceptions import LaunchFlowRequestFailure
from launchflow.flows.environments_flows import get_environment
from launchflow.flows.project_flows import get_project
from rich.progress import Progress, SpinnerColumn, TextColumn

from launchflow.clients import async_launchflow_client_ctx

app = UTyper(help="Commands for managing resources in LaunchFlow")


@app.command()
async def get(
    resource_name: str = typer.Argument(..., help="Resource to fetch information for."),
    project: str = typer.Option(None, help=PROJECT_HELP),
    environment: str = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """Fetch information about a resource."""
    async with async_launchflow_client_ctx() as client:
        project_info = await get_project(client, project, prompt_for_creation=False)
        environment_info = await get_environment(
            client,
            project=project_info,
            environment_name=environment,
            prompt_for_creation=False,
        )
        try:
            resource = await client.resources.get(
                project_info.name, environment_info.name, resource_name
            )

            print_response("Resource", resource.model_dump())
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


@app.command()
async def list(
    project: str = typer.Option(None, help=PROJECT_HELP),
    environment: str = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """List all resources in a project/environment."""
    async with async_launchflow_client_ctx() as client:
        try:
            project_info = await get_project(client, project, prompt_for_creation=False)
            environment_info = await get_environment(
                client,
                project=project_info,
                environment_name=environment,
                prompt_for_creation=False,
            )
            resources = await client.resources.list(
                project_info.name, environment_info.name
            )
            print_response(
                "Resources",
                {
                    "resources": [r.model_dump() for r in resources],
                },
            )
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


@app.command()
async def delete(
    resource_name: str = typer.Argument(..., help="Resource to delete."),
    project: str = typer.Option(None, help=PROJECT_HELP),
    environment: str = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """Delete a resource."""
    async with async_launchflow_client_ctx() as client:
        project_info = await get_project(client, project, prompt_for_creation=False)
        environment_info = await get_environment(
            client,
            project=project_info,
            environment_name=environment,
            prompt_for_creation=False,
        )
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("Deleting resource...", total=1)
                operation = await client.resources.delete(
                    project_info.name, environment_info.name, resource_name
                )
                try:
                    status = OperationStatus.PENDING
                    async for (
                        remote_status
                    ) in client.operations.stream_operation_status(operation.id):
                        status = remote_status
                except LaunchFlowRequestFailure as e:
                    if e.status_code == 404:
                        status = OperationStatus.SUCCESS
                    else:
                        raise e
                progress.remove_task(task)
                if status == OperationStatus.SUCCESS:
                    progress.console.print("[green]✓[/green] Resource deleted.")
                else:
                    progress.console.print("[red]✗[/red] Resource deletion failed")

        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)
