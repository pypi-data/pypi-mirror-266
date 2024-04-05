from enum import Enum
from typing import List, Literal, Optional, Type

import beaupy
import rich
from launchflow.aws.rds import RDSPostgres
from launchflow.aws.s3 import S3Bucket
from launchflow.clients.client import LaunchFlowAsyncClient
from launchflow.flows.project_flows import get_project
from launchflow.gcp.cloudsql import CloudSQLPostgres
from launchflow.gcp.compute_engine import ComputeEngineRedis
from launchflow.gcp.gcs import GCSBucket
from launchflow.gcp.memorystore import MemorystoreRedis

from launchflow import Resource


class Framework(Enum):
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"


FRAMEWORK_CHOICES = [
    (
        Framework.FASTAPI,
        "FastAPI framework, high performance, easy to learn, fast to code, ready for production",
    ),
    (
        Framework.FLASK,
        "The Python micro framework for building web applications.",
    ),
    (
        Framework.DJANGO,
        "The Web framework for perfectionists with deadlines.",
    ),
]


GCP_RESOURCE_CHOICES = [
    (
        GCSBucket,
        "Storage bucket. Powered by Google Cloud Storage (GCS).",
    ),
    (
        CloudSQLPostgres,
        "PostgreSQL database. Powered by Cloud SQL on GCP.",
    ),
    (
        ComputeEngineRedis,
        "Redis on a VM. Powered by Compute Engine on GCP.",
    ),
    (
        MemorystoreRedis,
        "Redis Cluster. Powered by Memorystore on GCP.",
    ),
]

AWS_RESOURCE_CHOICES = [
    (
        S3Bucket,
        "Storage bucket. Powered by Amazon S3.",
    ),
    (
        RDSPostgres,
        "PostgreSQL database. Powered by Amazon RDS.",
    ),
]


async def project(client: LaunchFlowAsyncClient, account_id: Optional[str]):
    print()
    print("Welcome to launchflow!")
    print("This tool will help you create a new application.")
    print("Let's get started!")
    print()
    return await get_project(client, project_name=None, prompt_for_creation=True)


def framework(cloud_provider: Literal["aws", "gcp"]) -> Framework:
    options = [f"{f[0].value} - {f[1]}" for f in FRAMEWORK_CHOICES]
    print()
    print("Select a framework for your API: (More coming soon)")
    answer = beaupy.select(options=options, return_index=True)
    rich.print(f"[pink1]>[/pink1] {options[answer]}")
    return FRAMEWORK_CHOICES[answer][0]


def resources(cloud_provider: Literal["aws", "gcp"]) -> List[Type[Resource]]:
    RESOURCE_CHOICES = (
        GCP_RESOURCE_CHOICES if cloud_provider == "gcp" else AWS_RESOURCE_CHOICES
    )
    options = [f"{f[0].__name__} - {f[1]}" for f in RESOURCE_CHOICES]
    print()
    print(
        "Select any resources you want to include in your application. These resources will be created in your cloud provider account:"
    )
    answers = beaupy.select_multiple(options=options, return_indices=True)
    to_ret = []
    for answer in answers:
        rich.print(f"[pink1]>[/pink1] {options[answer]}")
        to_ret.append(RESOURCE_CHOICES[answer][0])
    if not answers:
        rich.print("[pink1]>[/pink1] No resources selected.")
    return to_ret
