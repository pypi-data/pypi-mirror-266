import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

import toml


def _build_key(project: str, environment: str, product: str, resource: str) -> str:
    return f"{project}:{environment}:{product}:{resource}"


@dataclass
class LaunchFlowCache:
    resource_connection_bucket_paths: Dict[str, str] = field(default_factory=dict)
    resource_connection_info: Dict[str, Dict[str, str]] = field(default_factory=dict)
    gcp_service_account_emails: Dict[str, str] = field(default_factory=dict)

    def get_resource_connection_bucket_path(
        self, project: str, environment: str, product: str, resource: str
    ) -> Optional[str]:
        key = _build_key(project, environment, product, resource)
        return self.resource_connection_bucket_paths.get(key)

    def set_resource_connection_bucket_path(
        self,
        project: str,
        environment: str,
        product: str,
        resource: str,
        connection_bucket_path: str,
    ):
        key = _build_key(project, environment, product, resource)
        self.resource_connection_bucket_paths[key] = connection_bucket_path
        self.save_to_file(find_launchflow_tmp())

    def delete_resource_connection_bucket_path(
        self, project: str, environment: str, product: str, resource: str
    ):
        key = _build_key(project, environment, product, resource)
        self.resource_connection_bucket_paths.pop(key, None)
        self.save_to_file(find_launchflow_tmp())

    def get_resource_connection_info(
        self, project: str, environment: str, product: str, resource: str
    ) -> Optional[Dict[str, str]]:
        key = _build_key(project, environment, product, resource)
        return self.resource_connection_info.get(key)

    def set_resource_connection_info(
        self,
        project: str,
        environment: str,
        product: str,
        resource: str,
        connection_info: Dict[str, str],
    ):
        key = _build_key(project, environment, product, resource)
        self.resource_connection_info[key] = connection_info
        self.save_to_file(find_launchflow_tmp())

    def delete_resource_connection_info(
        self, project: str, environment: str, product: str, resource: str
    ):
        key = _build_key(project, environment, product, resource)
        self.resource_connection_info.pop(key, None)
        self.save_to_file(find_launchflow_tmp())

    def get_gcp_service_account_email(
        self, project: str, environment: str
    ) -> Optional[str]:
        key = f"{project}:{environment}"
        return self.gcp_service_account_emails.get(key)

    def set_gcp_service_account_email(self, project: str, environment: str, email: str):
        key = f"{project}:{environment}"
        self.gcp_service_account_emails[key] = email
        self.save_to_file(find_launchflow_tmp())

    def delete_gcp_service_account_email(self, project: str, environment: str):
        key = f"{project}:{environment}"
        self.gcp_service_account_emails.pop(key, None)
        self.save_to_file(find_launchflow_tmp())

    @classmethod
    def load_from_file(cls, file_path: str):
        if not os.path.exists(file_path):
            logging.debug(
                f"The file '{file_path}' does not exist. Creating with default values."
            )
            return cls()

        with open(file_path, "r") as file:
            data = toml.load(file)
            resource_connection_bucket_paths = data.get(
                "resource_connection_bucket_paths", {}
            )
            resource_connection_info = data.get("resource_connection_info", {})
            gcp_service_account_emails = data.get("gcp_service_account_emails", {})
        return cls(
            resource_connection_bucket_paths=resource_connection_bucket_paths,
            resource_connection_info=resource_connection_info,
            gcp_service_account_emails=gcp_service_account_emails,
        )

    def save_to_file(self, file_path: str):
        data = {
            "resource_connection_bucket_paths": self.resource_connection_bucket_paths,
            "resource_connection_info": self.resource_connection_info,
            "gcp_service_account_emails": self.gcp_service_account_emails,
        }
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            toml.dump(data, file)
        logging.debug(f"Saved to {file_path}")


def find_launchflow_tmp():
    # We use /var/tmp over /tmp since it persists across system reboot
    tmp_dir = "/var/tmp" if os.name != "nt" else os.environ.get("TEMP")
    file_path = os.path.join(tmp_dir, "lf", "cache.toml")
    return file_path


launchflow_dot_toml = None


def load_launchflow_tmp():
    global launchflow_dot_toml
    if launchflow_dot_toml is None:
        file_path = find_launchflow_tmp()
        launchflow_dot_toml = LaunchFlowCache.load_from_file(file_path)
    return launchflow_dot_toml
