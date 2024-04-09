import asyncio
import os
from typing import List, Optional

import beaupy
import fsspec
import rich
import typer
import uvloop
from launchflow.cli import project_gen
from launchflow.cli.accounts import account_commands
from launchflow.cli.config import config_commands
from launchflow.cli.constants import (
    ENVIRONMENT_HELP,
    PROJECT_HELP,
    SCAN_DIRECTORY_HELP,
    SERVICE_HELP,
)
from launchflow.cli.environments import environment_commands
from launchflow.cli.gen.templates.django.django_template import DjangoProjectGenerator
from launchflow.cli.gen.templates.fastapi.fastapi_template import (
    FastAPIProjectGenerator,
)
from launchflow.cli.gen.templates.flask.flask_template import FlaskProjectGenerator
from launchflow.cli.project import project_commands
from launchflow.cli.resources import resource_commands
from launchflow.cli.resources_ast import find_launchflow_resources
from launchflow.cli.services import service_commands
from launchflow.cli.utils import print_response, tar_source_in_memory
from launchflow.cli.utyper import UTyper
from launchflow.clients.client import LaunchFlowAsyncClient
from launchflow.clients.response_schemas import EnvironmentResponse, ProjectResponse
from launchflow.config import config
from launchflow.config.launchflow_yaml import ServiceConfig
from launchflow.exceptions import LaunchFlowRequestFailure
from launchflow.flows.account_id import get_account_id_from_config
from launchflow.flows.auth import login_flow, logout_flow
from launchflow.flows.cloud_provider import CloudProvider
from launchflow.flows.cloud_provider import connect as connect_provider
from launchflow.flows.environments_flows import get_environment
from launchflow.flows.project_flows import get_project
from launchflow.flows.resource_flows import clean as clean_resources
from launchflow.flows.resource_flows import create as create_resources
from launchflow.flows.resource_flows import destroy as destroy_resources
from launchflow.flows.resource_flows import import_resources
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Column

from launchflow.clients import async_launchflow_client_ctx

app = UTyper(help="LaunchFlow CLI.")
app.add_typer(account_commands.app, name="accounts")
app.add_typer(project_commands.app, name="projects")
app.add_typer(environment_commands.app, name="environments")
app.add_typer(resource_commands.app, name="resources")
app.add_typer(service_commands.app, name="services")
app.add_typer(config_commands.app, name="config")


async def _get_project_info(
    client: LaunchFlowAsyncClient,
    project_name: Optional[str] = None,
    prompt_for_creation: bool = True,
):
    # This check replaces the cli project arg with the configured project (if set)
    if project_name is None:
        project_name = config.project
    # Fetches the latest project info from the server
    return await get_project(
        client, project_name=project_name, prompt_for_creation=prompt_for_creation
    )


async def _get_environment_info(
    client: LaunchFlowAsyncClient,
    project: ProjectResponse,
    environment_name: Optional[str] = None,
    prompt_for_creation: bool = True,
):
    # This check replaces the cli env arg with the configured environment (if set)
    if environment_name is None:
        environment_name = config.environment
    # Fetches the latest environment info from the server
    return await get_environment(
        client=client,
        project=project,
        environment_name=environment_name,
        prompt_for_creation=prompt_for_creation,
    )


def _get_service_infos(service_name: Optional[str] = None) -> List[ServiceConfig]:
    service_configs = config.list_service_configs()
    if service_name is not None:
        for service in service_configs:
            if service.name == service_name:
                return service
        typer.echo(f"Service `{service_name}` not found in launchflow.yaml.")
        raise typer.Exit(1)
    if not service_configs:
        typer.echo("No services configured in launchflow.yaml.")
        raise typer.Exit(1)
    return service_configs


@app.command()
async def init(
    directory: str = typer.Argument(None, help="Directory to initialize launchflow."),
    account_id: str = typer.Option(
        None,
        help="Account ID to use for this project. Defaults to the account ID set in the config.",
    ),
):
    """Initialize a new launchflow project."""
    async with async_launchflow_client_ctx() as client:
        try:
            project = await project_gen.project(client, account_id)

            if "aws" in project.configured_cloud_providers:
                cloud_provider = "aws"
            elif "gcp" in project.configured_cloud_providers:
                cloud_provider = "gcp"
            else:
                raise NotImplementedError(
                    f"Cloud provider {project.configured_cloud_providers} is not supported yet."
                )

            environment = await get_environment(
                client=client,
                project=project,
                environment_name=None,
                prompt_for_creation=True,
            )
        except Exception as e:
            typer.echo(e)
            raise typer.Exit(1)

        if not directory:
            relative_path = project.name
            full_directory_path = os.path.join(os.path.abspath("."), relative_path)
        else:
            relative_path = directory
            full_directory_path = os.path.abspath(relative_path)
        while os.path.exists(full_directory_path):
            typer.echo(f"Directory `{full_directory_path}` already exists.")
            directory_name = beaupy.prompt("Enter a directory name for your project:")
            full_directory_path = os.path.join(
                os.path.abspath(directory), directory_name
            )

        framework = project_gen.framework(cloud_provider)
        resources = project_gen.resources(cloud_provider)

        if framework == project_gen.Framework.FASTAPI:
            generator = FastAPIProjectGenerator(
                resources=resources,
                cloud_provider=cloud_provider,
                launchflow_project_name=project.name,
                launchflow_environment_name=environment.name,
            )
            generator.generate_project(full_directory_path)
        elif framework == project_gen.Framework.FLASK:
            generator = FlaskProjectGenerator(
                resources=resources,
                cloud_provider=cloud_provider,
                launchflow_project_name=project.name,
                launchflow_environment_name=environment.name,
            )
            generator.generate_project(full_directory_path)
        elif framework == project_gen.Framework.DJANGO:
            generator = DjangoProjectGenerator(
                resources=resources,
                cloud_provider=cloud_provider,
                launchflow_project_name=project.name,
                launchflow_environment_name=environment.name,
            )
            generator.generate_project(full_directory_path)
        else:
            raise NotImplementedError(f"Framework {framework} is not supported yet.")

        print()
        print("Done!")
        print()
        print("Navigate to your project directory:")
        rich.print(f"  $ [green]cd {relative_path}")
        print()
        print("To create your resources run:")
        rich.print("  $ [green]launchflow create")
        print()
        print("To build and deploy your app remotely run:")
        rich.print("  $ [green]launchflow deploy")


@app.command()
async def create(
    resource: str = typer.Argument(
        None,
        help="Resource to create. If none we will scan the directory for resources.",
    ),
    project: Optional[str] = typer.Option(None, help=PROJECT_HELP),
    environment: Optional[str] = typer.Option(None, help=ENVIRONMENT_HELP),
    scan_directory: str = typer.Option(".", help=SCAN_DIRECTORY_HELP),
):
    """Create any resources that are not already created."""
    try:
        async with async_launchflow_client_ctx() as client:
            project_info = await _get_project_info(client, project)
            environment_info = await _get_environment_info(
                client, project_info, environment
            )

            if resource is None:
                resources = find_launchflow_resources(scan_directory)
            else:
                resources = [resource]

            await create_resources(
                project_info.name,
                environment_info.name,
                *import_resources(resources),
            )

    except LaunchFlowRequestFailure as e:
        e.pretty_print()
        raise typer.Exit(1)


@app.command()
async def clean(
    scan_directory: str = typer.Option(".", help=SCAN_DIRECTORY_HELP),
    project: Optional[str] = typer.Option(None, help=PROJECT_HELP),
    environment: Optional[str] = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """Clean up any resources that are not in the current directory but are part of the project / environment."""
    try:
        async with async_launchflow_client_ctx() as client:
            project_info = await _get_project_info(client, project)
            environment_info = await _get_environment_info(
                client, project_info, environment
            )

            resources = find_launchflow_resources(scan_directory)
            await clean_resources(
                project_info.name,
                environment_info.name,
                *import_resources(resources),
            )

    except LaunchFlowRequestFailure as e:
        e.pretty_print()
        raise typer.Exit(1)


@app.command()
async def destroy(
    project: Optional[str] = typer.Option(None, help=PROJECT_HELP),
    environment: Optional[str] = typer.Option(None, help=ENVIRONMENT_HELP),
):
    """Destroy all resources in the project / environment."""
    try:
        async with async_launchflow_client_ctx() as client:
            project_info = await _get_project_info(client, project)
            environment_info = await _get_environment_info(
                client, project_info, environment
            )
            # NOTE: This prompts the user to confirm the destruction of each resource
            await destroy_resources(project_info.name, environment_info.name)

    except LaunchFlowRequestFailure as e:
        e.pretty_print()
        raise typer.Exit(1)


async def _deploy_service(
    client: LaunchFlowAsyncClient,
    service_info: ServiceConfig,
    project_info: ProjectResponse,
    environment_info: EnvironmentResponse,
    progress: Progress,
):
    service_ref = (
        f'Service(name="{service_info.name}", product="{service_info.product}")'
    )
    bundle_task = progress.add_task("Bundling service files...", total=None)
    tar_bytes = tar_source_in_memory(directory=service_info.directory)
    progress.remove_task(bundle_task)

    # TODO: List out the infra changes that will be made in the user's
    # account, like creating the docker repo, docker image, cloud run service, etc.

    # TODO: Add a way to notify the user of build progress

    # TODO: (maybe) add a ETA for the build
    description = f"Deploying {service_ref}..."
    deploy_task = progress.add_task(description, total=None)
    operation = await client.services.deploy(
        project_name=project_info.name,
        environment_name=environment_info.name,
        product_name=service_info.product,
        service_name=service_info.name,
        tar_bytes=tar_bytes,
        create_args=service_info.product_config.to_dict(),
    )
    last_message = ""
    async for (
        status,
        current_message,
    ) in client.operations.stream_operation_status_and_message(operation.id):
        if status.is_error():
            operation = await client.operations.get(operation.id)
            progress.remove_task(deploy_task)
            progress.console.print(
                f"[red]✗[/red] Deployment failed for [blue]{service_ref}[/blue]"
            )
            progress.console.print(
                f"    └── View logs for operation by running `launchflow logs {operation.id}`"
            )
            if operation.build_url:
                progress.console.print(
                    f"    └── View build logs at {operation.build_url}"
                )
            raise typer.Exit(1)
        elif status.is_cancelled():
            progress.remove_task(deploy_task)
            progress.console.print(
                f"[yellow]✗[/yellow] Deployment cancelled for [blue]{service_ref}[/blue]"
            )
            raise typer.Exit(1)
        elif status.is_success():
            progress.remove_task(deploy_task)
            progress.console.print(
                f"[green]✓[/green] Deployment successful for [blue]{service_ref}[/blue]"
            )
            break
        elif last_message != current_message:
            last_message = current_message
            new_description = f"{description}\n    └── {current_message}"
            description = new_description
            progress.update(deploy_task, description=description)


@app.command(hidden=True)
async def deploy(
    project: Optional[str] = typer.Option(None, help=PROJECT_HELP),
    environment: Optional[str] = typer.Option(None, help=ENVIRONMENT_HELP),
    service: Optional[str] = typer.Option(None, help=SERVICE_HELP),
):
    """Deploy a service to a project / environment."""
    async with async_launchflow_client_ctx() as client:
        try:
            project_info = await _get_project_info(client, project)
            environment_info = await _get_environment_info(
                client, project_info, environment
            )
            service_infos = _get_service_infos(service)
            selected_services: List[ServiceConfig] = []
            if len(service_infos) == 1:
                service_ref = f'Service(name="{service_infos[0].name}", product="{service_infos[0].product}")'

                answer = beaupy.confirm(
                    f"Deploy {service_ref} to `{project_info.name}/{environment_info.name}`?"
                )
                if not answer:
                    print("User cancelled deployment. Exiting.")
                    return
                selected_services.append(service_infos[0])
            else:
                print(
                    f"Select the services you want to deploy to `{project_info.name}/{environment_info.name}`."
                )
                service_refs = [
                    f'Service(name="{si.name}", product="{si.product}")'
                    for si in service_infos
                ]
                selected = beaupy.select_multiple(service_refs, return_indices=True)
                for answer in selected:
                    rich.print(f"[pink1]>[/pink1] {service_refs[answer]}")
                    selected_services.append(service_infos[answer])
            if not selected_services:
                print("No services selected. Exiting.")
                return
            coros = []
            with Progress(
                SpinnerColumn(),
                # NOTE: we provide column here to customize how overflow is displayed since the build urls can be kind of long
                TextColumn(
                    "[progress.description]{task.description}",
                    table_column=Column(no_wrap=False, overflow="fold"),
                ),
            ) as progress:
                for service in service_infos:
                    coros.append(
                        _deploy_service(
                            client=client,
                            service_info=service,
                            project_info=project_info,
                            environment_info=environment_info,
                            progress=progress,
                        )
                    )
                await asyncio.gather(*coros)

        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


@app.command()
async def login():
    """Login to LaunchFlow. If you haven't signup this will create a free account for you."""
    try:
        async with async_launchflow_client_ctx() as client:
            await login_flow(client)
    except Exception as e:
        typer.echo(f"Failed to login. {e}")
        typer.Exit(1)


@app.command()
def logout():
    """Logout of LaunchFlow."""
    try:
        logout_flow()
    except Exception as e:
        typer.echo(f"Failed to logout. {e}")
        typer.Exit(1)


@app.command()
async def connect(
    account_id: str = typer.Argument(
        None, help="The account ID to fetch. Of the format `acount_123`"
    ),
    provider: CloudProvider = typer.Option(
        None, help="The cloud provider to setup your account with."
    ),
    status: bool = typer.Option(
        False,
        "--status",
        "-s",
        help="Only print out connection status instead of instructions for connecting.",
    ),
):
    """Connect your LaunchFlow account to a cloud provider (AWS or GCP) or retrieve connection info with the `--status / -s` flag."""
    async with async_launchflow_client_ctx() as client:
        if status:
            account_id = await get_account_id_from_config(client, account_id)
            connection_status = await client.connect.status(account_id)
            to_print = connection_status.model_dump()
            del to_print["aws_connection_info"]["cloud_foundation_template_url"]
            print_response("Connection Status", to_print)
        else:
            try:
                await connect_provider(client, account_id, provider)
            except LaunchFlowRequestFailure as e:
                e.pretty_print()
                raise typer.Exit(1)
            except Exception as e:
                typer.echo(str(e))
                raise typer.Exit(1)


@app.command()
async def logs(
    operation_id: str = typer.Argument(
        None, help="The operation ID to fetch logs for."
    ),
):
    """Fetch the logs for a given operation."""
    async with async_launchflow_client_ctx() as client:
        try:
            operation = await client.operations.get(operation_id)
            if not operation.environment_name:
                typer.echo("Operation does not have an environment.")
                raise typer.Exit(1)
            environment = await client.environments.get(
                operation.project_name, operation.environment_name
            )
            if environment.aws_config:
                path = f"s3://{environment.aws_config.artifact_bucket}/logs/{operation_id}.log"
            elif environment.gcp_config:
                path = f"gs://{environment.gcp_config.artifact_bucket}/logs/{operation_id}.log"
            else:
                typer.echo("No artifact bucket found for environment.")
                raise typer.Exit(1)
            with fsspec.open(path) as f:
                print(f.read().decode("utf-8"))
        except LaunchFlowRequestFailure as e:
            e.pretty_print()
            raise typer.Exit(1)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app()
