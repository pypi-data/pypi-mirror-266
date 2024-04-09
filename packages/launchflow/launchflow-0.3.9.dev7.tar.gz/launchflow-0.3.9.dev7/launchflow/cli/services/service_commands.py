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

app = UTyper(help="Commands for managing services in LaunchFlow")


@app.command()
async def get(
    service_name: str = typer.Argument(..., help="Service to fetch information for."),
    project: str = typer.Option(None, help=PROJECT_HELP),
    environment: str = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """Fetch information about a service."""
    async with async_launchflow_client_ctx() as client:
        project_info = await get_project(client, project, prompt_for_creation=False)
        environment_info = await get_environment(
            client,
            project=project_info,
            environment_name=environment,
            prompt_for_creation=False,
        )
        try:
            service = await client.services.get(
                project_info.name, environment_info.name, service_name
            )

            print_response("Service", service.model_dump())
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


@app.command()
async def list(
    project: str = typer.Option(None, help=PROJECT_HELP),
    environment: str = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """List all services in a project/environment."""
    async with async_launchflow_client_ctx() as client:
        try:
            project_info = await get_project(client, project, prompt_for_creation=False)
            environment_info = await get_environment(
                client,
                project=project_info,
                environment_name=environment,
                prompt_for_creation=False,
            )
            services = await client.services.list(
                project_info.name, environment_info.name
            )
            print_response(
                "Services",
                {
                    "services": [r.model_dump() for r in services],
                },
            )
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


@app.command()
async def delete(
    service_name: str = typer.Argument(..., help="Service to delete."),
    project: str = typer.Option(None, help=PROJECT_HELP),
    environment: str = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """Delete a service."""
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
                task = progress.add_task("Deleting service...", total=1)
                operation = await client.services.delete(
                    project_info.name, environment_info.name, service_name
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
                    progress.console.print("[green]✓[/green] Service deleted.")
                else:
                    progress.console.print("[red]✗[/red] Service deletion failed")

        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)
