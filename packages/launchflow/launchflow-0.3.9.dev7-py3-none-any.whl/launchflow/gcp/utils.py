import os
from typing import Optional

import requests
from google.auth import default, impersonated_credentials
from launchflow.context import ctx

_ProjectIdMetadataKey = "project/project-id"
_ProjectNumberMetadataKey = "project/numeric-project-id"
_RegionMetadataKey = "instance/region"
_InstanceIdMetadataKey = "instance/id"
_ServiceAccountEmailMetadataKey = "instance/service-accounts/default/email"
_ServiceAccountTokenMetadataKey = "instance/service-accounts/default/token"


# Cloud Run automatically sets the K_SERVICE environment variable
# Docs: https://cloud.google.com/run/docs/container-contract#env-vars
def _is_running_on_cloud_run():
    """Check if running on Google Cloud Run."""
    return "K_SERVICE" in os.environ


# Cloud Run instances expose a metadata server to fetch info at runtime
# Docs: https://cloud.google.com/run/docs/reference/container-contract#metadata-server
def _get_cloud_run_metadata(metadata_key: str):
    """
    Get the metadata value from the Cloud Run instance metadata server.
    """
    metadata_server_url = "http://metadata.google.internal/computeMetadata/v1/"
    metadata_server_url += metadata_key

    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_server_url, headers=headers)
    if metadata_key == _ServiceAccountTokenMetadataKey:
        return response.json()
    return response.text


def get_service_account_credentials(
    project_name: Optional[str] = None,
    environment_name: Optional[str] = None,
) -> str:
    """
    Get the GCP service account credentials for the specified project and environment.
    """

    if _is_running_on_cloud_run():
        # If running on Cloud Run, fetch the service account from the metadata server
        gcp_service_account_email = _get_cloud_run_metadata(
            _ServiceAccountEmailMetadataKey
        )
    else:
        # If not on Cloud Run, fetch the GCP service account email from LaunchFlow
        gcp_service_account_email = ctx.get_gcp_service_account_email(
            project_name, environment_name
        )

    # Load the default credentials (from environment, compute engine, etc.)
    creds, _ = default()
    # Define the target service account to impersonate
    target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=creds,
        target_principal=gcp_service_account_email,
        target_scopes=target_scopes,
        lifetime=30 * 60,  # The maximum lifetime in seconds
    )

    return target_credentials
