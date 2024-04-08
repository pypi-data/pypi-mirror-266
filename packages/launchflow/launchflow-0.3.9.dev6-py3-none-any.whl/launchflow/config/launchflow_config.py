import dataclasses
import os
import time
from typing import Any, Dict, Optional

import requests
import toml
from launchflow.config.launchflow_env import LaunchFlowEnvVars, load_launchflow_env
from launchflow.config.launchflow_yaml import (
    LaunchFlowDotYaml,
    load_launchflow_dot_yaml,
)
from launchflow.exceptions import LaunchFlowRequestFailure

SETTINGS_PATH = os.path.expanduser("~/.config/launchflow/settings.toml")
CREDENTIALS_PATH = os.path.expanduser("~/.config/launchflow/credentials.toml")
_REFRESH_BUFFER = 60  # seconds


@dataclasses.dataclass
class Settings:
    default_account_id: Optional[str] = None
    launch_service_address: str = "https://launch.launchflow.com"
    account_service_address: str = "https://accounts.launchflow.com"


@dataclasses.dataclass
class Credentials:
    access_token: str
    expires_at_seconds: int
    refresh_token: str

    def is_expired(self):
        return self.expires_at_seconds - _REFRESH_BUFFER < int(time.time())


@dataclasses.dataclass
class LaunchFlowConfig:
    settings: Settings
    credentials: Optional[Credentials]
    launchflow_yaml: Optional[LaunchFlowDotYaml]
    env: LaunchFlowEnvVars

    @property
    def project(self):
        # Environment variable takes precedence
        if self.env.project is not None:
            return self.env.project
        # Then launchflow.yaml
        if self.launchflow_yaml is not None:
            return self.launchflow_yaml.project
        # Default to None
        return None

    @property
    def environment(self):
        # Environment variable takes precedence
        if self.env.environment is not None:
            return self.env.environment
        # Then launchflow.yaml
        if self.launchflow_yaml is not None:
            return self.launchflow_yaml.environment
        # Default to None
        return None

    def list_service_configs(self):
        if self.launchflow_yaml is not None:
            return self.launchflow_yaml.services
        return []

    @classmethod
    def load(cls):
        settings = Settings()
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH) as f:
                settings = Settings(**toml.load(f))
        else:
            # populate settings file with default values
            os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
            with open(SETTINGS_PATH, "w") as f:
                toml.dump(dataclasses.asdict(settings), f)

        credentials = None
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH) as f:
                credentials = Credentials(**toml.load(f))

        try:
            launchflow_dot_yaml = load_launchflow_dot_yaml()
        except FileNotFoundError:
            launchflow_dot_yaml = None

        launchflow_env = load_launchflow_env()

        return cls(
            settings=settings,
            credentials=credentials,
            launchflow_yaml=launchflow_dot_yaml,
            env=launchflow_env,
        )

    def get_access_token(self):
        if self.credentials is None:
            raise ValueError("No credentials")
        if self.credentials.is_expired():
            response = requests.post(
                f"{self.settings.account_service_address}/auth/refresh",
                json={"refresh_token": self.credentials.refresh_token},
            )
            if response.status_code != 200:
                raise LaunchFlowRequestFailure(response)
            self.update_credentials(response.json())
        return self.credentials.access_token

    def save(self):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)

        with open(SETTINGS_PATH, "w") as f:
            toml.dump(dataclasses.asdict(self.settings), f)

        if self.credentials is not None:
            with open(CREDENTIALS_PATH, "w") as f:
                toml.dump(dataclasses.asdict(self.credentials), f)
        # Remove credentials file if it exists but credentials is None
        elif os.path.exists(CREDENTIALS_PATH):
            os.remove(CREDENTIALS_PATH)

    def update_credentials(self, credentials_json: Dict[str, Any]):
        self.credentials = Credentials(**credentials_json)
        self.save()

    def clear_credentials(self):
        self.credentials = None
        self.save()

    def info(self):
        return {
            "settings": dataclasses.asdict(self.settings),
        }
