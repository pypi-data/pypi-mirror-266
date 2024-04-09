import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LaunchFlowEnvVars:
    project: Optional[str]
    environment: Optional[str]
    api_key: Optional[str] = None
    connection_bucket: Optional[str] = None
    connection_path: Optional[str] = None

    @classmethod
    def load_from_env(cls):
        """
        Loads the object's properties from environment variables.

        Returns:
            An instance of LaunchFlowDotEnv with properties populated from environment variables.
        """
        project = os.getenv("LAUNCHFLOW_PROJECT", None)
        environment = os.getenv("LAUNCHFLOW_ENVIRONMENT", None)
        api_key = os.getenv("LAUNCHFLOW_API_KEY", None)
        connection_bucket = os.getenv("LAUNCHFLOW_CONNECTION_BUCKET", None)
        connection_path = os.getenv("LAUNCHFLOW_CONNECTION_PATH", None)

        return cls(
            project=project,
            environment=environment,
            api_key=api_key,
            connection_bucket=connection_bucket,
            connection_path=connection_path,
        )


launchflow_env_vars = None


# NOTE: We use a global variable so its only loaded once
def load_launchflow_env():
    global launchflow_env_vars
    if launchflow_env_vars is None:
        launchflow_env_vars = LaunchFlowEnvVars.load_from_env()
    return launchflow_env_vars
