import asyncio
from typing import List, Optional, Tuple

import beaupy
import rich
from launchflow.clients.response_schemas import (
    EnvironmentResponse,
    EnvironmentType,
    OperationStatus,
    ProjectResponse,
)
from launchflow.exceptions import LaunchFlowOperationFailure, LaunchFlowRequestFailure
from launchflow.operations import AsyncOp
from rich.progress import Progress, SpinnerColumn, TextColumn

from launchflow.clients import LaunchFlowAsyncClient

_GCP_TASK_MESSAGES = [
    ("Creating GCP project for environment...", "GCP project successfully created."),
    (
        "Creating service account for environment...",
        "Service account successfully created.",
    ),
    (
        "Setting project IAM permissions for service account...",
        "Project IAM permissions updated.",
    ),
    (
        "Enabling required APIs in GCP (this may take several minutes)...",
        "Required APIs enabled in GCP.",
    ),
]

_AWS_TASK_MESSAGES = [
    ("Creating artifact bucket...", "Artifact bucket successfully create."),
    ("Creating IAM policy...", "IAM policy successfully created."),
    ("Creating IAM role...", "IAM role successfully created."),
    ("Creating environment VPC...", "VPC successfully created."),
]


async def get_environment(
    client: LaunchFlowAsyncClient,
    project: ProjectResponse,
    environment_name: Optional[str],
    prompt_for_creation: bool = True,
):
    if environment_name is None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Fetching environments...", total=None)
            environments = await client.environments.list(project.name)
            progress.remove_task(task)
        environment_names = [f"{e.name}" for e in environments]
        if prompt_for_creation:
            environment_names.append("[i yellow]Create new environment[/i yellow]")
        print("Select the environment to use:")
        selected_environment = beaupy.select(
            environment_names, return_index=True, strict=True
        )
        if prompt_for_creation and selected_environment == len(environment_names) - 1:
            environment = await create_environment(
                client, environment_name=None, project=project, environment_type=None
            )
        else:
            environment = environments[selected_environment]
            rich.print(f"[pink1]>[/pink1] {environment.name}")
        return environment
    try:
        # Fetch the environment to ensure it exists
        environment = await client.environments.get(project.name, environment_name)
    except LaunchFlowRequestFailure as e:
        if e.status_code == 404 and prompt_for_creation:
            answer = beaupy.confirm(
                f"Environment `{environment_name}` does not exist yet. Would you like to create it?"
            )
            if answer:
                # TODO: this will just use their default account. Should maybe ask them.
                # But maybe that should be in the create project flow?
                environment = await create_environment(
                    client, environment_name, project, environment_type=None
                )
            else:
                raise e
        else:
            raise e
    return environment


async def _monitor_env_creation(
    client: LaunchFlowAsyncClient,
    project: ProjectResponse,
    environment_name: str,
    environment_type: EnvironmentType,
    environment_tasks: List[Tuple[str, str]],
    time_between_task_seconds: int = 3,
):
    print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:

        async def create_env():
            if "gcp" in project.configured_cloud_providers:
                return await client.environments.create_gcp(
                    project.name, environment_name, environment_type
                )
            elif "aws" in project.configured_cloud_providers:
                return await client.environments.create_aws(
                    project.name, environment_name, environment_type
                )
            else:
                raise ValueError("No cloud provider configured for this project.")

        op = AsyncOp(operation_id=None, client=client, _op=create_env)

        await op.run()

        # TODO: ideally the server would return the status updates but for now this is fine.
        tasks = {}
        for task in environment_tasks:
            progress_task = progress.add_task(task[0], total=None)
            tasks[progress_task] = task

        def mark_done(task: int, pop: bool = True):
            progress.remove_task(task)
            msg = tasks[task][1]
            progress.console.print(f"[green]✓[/green] {msg}")
            if pop:
                tasks.pop(task)

        while True:
            try:
                status = await op.get_status()
                if not status.is_final():
                    await asyncio.sleep(time_between_task_seconds)
                    if len(tasks) > 1:
                        task = next(iter(tasks))
                        mark_done(task)
                    continue
                environment = await client.environments.get(
                    project.name, environment_name
                )
                if status != OperationStatus.SUCCESS:
                    raise LaunchFlowOperationFailure(project.status_message)
                break
            except Exception as e:
                # Remove all tasks and print error message
                [progress.remove_task(t.id) for t in progress.tasks]
                progress.console.print("[red]✗[/red] Failed to create environment.")
                raise e
        for task in tasks.keys():
            mark_done(task, pop=False)
        progress.console.print("\n[green]✓[/green] Environment created successfully.")
        return environment


async def create_environment(
    client: LaunchFlowAsyncClient,
    environment_name: Optional[str],
    project: ProjectResponse,
    environment_type: Optional[EnvironmentType],
) -> EnvironmentResponse:
    """Create a new environment in a project."""
    if environment_name is None:
        environment_name = beaupy.prompt("Enter the environment name:")
        rich.print(f"[pink1]>[/pink1] {environment_name}")

    if environment_type is None:
        print("Select the environment type:")
        selection = beaupy.select(
            ["development", "production"],
            strict=True,
        )
        environment_type = EnvironmentType(selection)

    if "gcp" in project.configured_cloud_providers:
        tasks = _GCP_TASK_MESSAGES
        wait_time = 3
    elif "aws" in project.configured_cloud_providers:
        tasks = _AWS_TASK_MESSAGES
        wait_time = 3
    else:
        raise ValueError("No cloud provider configured for this project.")
    return await _monitor_env_creation(
        client,
        project,
        environment_name,
        environment_type,
        tasks,
        time_between_task_seconds=wait_time,
    )
