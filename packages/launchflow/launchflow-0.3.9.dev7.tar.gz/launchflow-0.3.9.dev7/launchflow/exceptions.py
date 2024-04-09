from typing import Optional

from launchflow.utils import get_failure_text


class LaunchFlowException(Exception):
    def pretty_print(self):
        print(self)


class LaunchFlowRequestFailure(LaunchFlowException):
    def __init__(self, response) -> None:
        super().__init__(get_failure_text(response))
        self.status_code = response.status_code


class LaunchFlowOperationFailure(LaunchFlowException):
    def __init__(self, status_message: str) -> None:
        super().__init__(status_message)


# TODO: Move "potential fix" messsages into the server.
# Server should return a json payload with a message per client type, i.e.
# {status: 409, message: "Conflict...", fix: {"cli": "Run this command..."}}
# Use details to return the fix payload:
# details = {message: "...", fix: {"cli": "Run this command..."}}
class ConnectionInfoNotFound(Exception):
    def __init__(self, resource_name: str) -> None:
        super().__init__(
            f"Connection info for resource '{resource_name}' not found. "
            f"\n\nPotential Fix:\nRun `launchflow create` it.\n\n"
        )


class PermissionCannotReadConnectionInfo(Exception):
    def __init__(self, resource_name: str, connection_path: str) -> None:
        super().__init__(
            f"Permission denied reading connection info for resource '{resource_name}' please ensure you have access to read the bucket: {connection_path}"
        )


class ForbiddenConnectionInfo(Exception):
    def __init__(self, bucket_url) -> None:
        super().__init__(
            f"Failed to read connection info from bucket. Please ensure you have access at: {bucket_url}"
        )


class ProjectOrEnvironmentNotSet(Exception):
    def __init__(self, project: Optional[str], environment: Optional[str]) -> None:
        super().__init__(
            f"Project or environment name not set. Set the project and environment names using "
            f"launchflow.yaml or the environment variables LAUNCHFLOW_PROJECT and LAUNCHFLOW_ENVIRONMENT. "
            f"\n\nCurrent project: {project}\nCurrent environment: {environment}\n\n"
        )


class RemoteConnectionInfoMissing(Exception):
    def __init__(self, remote_resource_info) -> None:
        super().__init__(
            f"Remote connection info for resource '{remote_resource_info}' is missing. "
            f"\n\nPotential Fix:\nRun `launchflow create` to create the resource or "
            f"`launchflow connect` to connect to it.\n\n"
        )


class OperationNotStarted(Exception):
    def __init__(self, operation: str) -> None:
        super().__init__(
            f"Operation '{operation}' not started. "
            f"\n\nPotential Fix:\nRun `launchflow start` to start the operation.\n\n"
        )


class OperationAlreadyStarted(Exception):
    def __init__(self, operation: str) -> None:
        super().__init__(
            f"Operation '{operation}' already started. "
            f"\n\nPotential Fix:\nRun `launchflow start` to start the operation.\n\n"
        )


class ResourceReplacementRequired(Exception):
    def __init__(self, resource_name: str) -> None:
        super().__init__(
            f"Resource '{resource_name}' already exists but the create operation "
            "requires replacement, which must be explicitly specified. "
        )


class ResourceProductMismatch(Exception):
    def __init__(self, product: str, resource: str) -> None:
        super().__init(
            f"Product '{product}' does not match the product of resource '{resource}'."
        )


class ServiceProductMismatch(Exception):
    def __init__(self, product: str, service: str) -> None:
        super().__init(
            f"Product '{product}' does not match the product of service '{service}'."
        )


class GCPConfigNotFound(Exception):
    def __init__(self, environment_name: str) -> None:
        super().__init(
            f"GCP configuration not found for environment '{environment_name}'. "
            "This environment is most likely an AWS environment."
        )
