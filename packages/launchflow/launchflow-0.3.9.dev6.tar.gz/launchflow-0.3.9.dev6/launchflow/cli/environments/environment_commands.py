from typing import Optional

import typer
from launchflow.cli.utils import print_response
from launchflow.cli.utyper import UTyper
from launchflow.clients.response_schemas import EnvironmentType
from launchflow.exceptions import LaunchFlowException
from launchflow.flows.environments_flows import create_environment
from launchflow.flows.project_flows import get_project

from launchflow.clients import async_launchflow_client_ctx

app = UTyper(help="Interact with your LaunchFlow environments.")


@app.command()
async def create(
    name: str = typer.Argument(None, help="The environment name."),
    project: str = typer.Option(
        None, help="The project to create the environments in."
    ),
    env_type: Optional[EnvironmentType] = typer.Option(
        None, help="The environment type (`development` or `production`)."
    ),
):
    """Create a new environment in a LaunchFlow project."""
    try:
        async with async_launchflow_client_ctx() as client:
            project_info = await get_project(client, project, prompt_for_creation=True)
            environment = await create_environment(client, name, project_info, env_type)
    except LaunchFlowException as e:
        typer.echo(e)
        raise typer.Exit(1)

    print_response("Environment", environment.model_dump())


@app.command()
async def list(
    project: str = typer.Option(None, help="The project to list environments for.")
):
    """List all environments in a LaunchFlow project."""
    try:
        async with async_launchflow_client_ctx() as client:
            project_info = await get_project(client, project, prompt_for_creation=True)
            environments = await client.environments.list(project_info.name)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(1)

    print_response(
        "Environments",
        {"environments": [env.model_dump(mode="json") for env in environments]},
    )


@app.command()
async def get(
    name: str = typer.Argument(..., help="The environment name."),
    project: str = typer.Option(None, help="The project the environment is in."),
):
    """Get information about a specific environment."""
    try:
        async with async_launchflow_client_ctx() as client:
            project_info = await get_project(client, project, prompt_for_creation=True)
            environment = await client.environments.get(project_info.name, name)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(1)

    print_response("Environment", environment.model_dump())
