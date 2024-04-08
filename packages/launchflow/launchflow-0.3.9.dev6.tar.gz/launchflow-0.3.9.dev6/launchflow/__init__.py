# ruff: noqa
import asyncio
from contextlib import asynccontextmanager, contextmanager

from launchflow.resource import Resource

from . import aws, fastapi, gcp
from .flows.resource_flows import clean, create

# TODO: Add generic resource imports, like Postgres, StorageBucket, etc.
# This should probably live directly under launchflow, i.e. launchflow/postgres.py


async def connect_all(*resources: Resource):
    connect_tasks = [resource.connect_async() for resource in resources]
    await asyncio.gather(*connect_tasks)
