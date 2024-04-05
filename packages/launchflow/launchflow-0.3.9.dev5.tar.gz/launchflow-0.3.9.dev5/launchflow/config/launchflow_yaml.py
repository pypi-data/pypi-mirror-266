import os
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Literal, Optional, Union

import yaml

# Define the allowed product types
ProductType = Literal["gcp_cloud_run", "aws_ecs_fargate"]


@dataclass
class ProductConfig:
    pass

    def to_dict(self):
        dict_with_nones = asdict(self)
        return {k: v for k, v in dict_with_nones.items() if v is not None}


@dataclass
class GcpCloudRunConfig(ProductConfig):
    location: Optional[str] = None
    cpu: Optional[int] = None
    memory: Optional[str] = None
    min_instances: Optional[int] = None
    max_instances: Optional[int] = None
    container_concurrency: Optional[int] = None


@dataclass
class AwsEcsFargateConfig(ProductConfig):
    cpu: Optional[str] = None
    memory: Optional[int] = None


# Factory function to create product config instances based on type
def create_product_config(product_type: ProductType, config: Dict) -> ProductConfig:
    if product_type == "gcp_cloud_run":
        return GcpCloudRunConfig(**config)
    elif product_type == "aws_ecs_fargate":
        return AwsEcsFargateConfig(**config)
    else:
        raise ValueError(f"Unsupported product type: {product_type}")


@dataclass
class ServiceConfig:
    name: str
    product: ProductType
    product_config: Optional[Union[GcpCloudRunConfig, AwsEcsFargateConfig]] = None
    directory: str = "."
    dockerfile: str = None
    domain_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        product_type = data.get("product")
        product_config_data = data.get("product-config", {})
        product_config = create_product_config(product_type, product_config_data)

        return cls(
            name=data.get("name", ""),
            product=product_type,
            product_config=product_config,
            directory=data.get("directory", "."),
            dockerfile=data.get("dockerfile"),
            domain_name=data.get("domain_name"),
        )

    def to_dict(self):
        to_return = {
            "name": self.name,
            "product": self.product,
        }
        if self.product_config:
            to_return["product-config"] = self.product_config.to_dict()
        if self.directory:
            to_return["directory"] = self.directory
        if self.dockerfile:
            to_return["dockerfile"] = self.dockerfile
        if self.domain_name:
            to_return["domain_name"] = self.domain_name
        return to_return


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


@dataclass
class LaunchFlowDotYaml:
    project: str
    environment: str
    services: List[ServiceConfig] = field(default_factory=list)

    @classmethod
    def load_from_cwd(cls, start_path="."):
        file_path = find_launchflow_yaml(start_path)
        if file_path is None:
            raise FileNotFoundError("Could not find 'launchflow.yaml' file.")
        return cls.load_from_file(file_path)

    @classmethod
    def load_from_file(cls, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            project = data.get("project", "")
            environment = data.get("environment", "")
            services_data = data.get("services", [])
            services = [ServiceConfig.from_dict(service) for service in services_data]

        return cls(project=project, environment=environment, services=services)

    def save_to_file(self, file_path: str):
        services_data = [service.to_dict() for service in self.services]

        data = {
            "project": self.project,
            "environment": self.environment,
        }
        if services_data:
            data["services"] = services_data

        with open(file_path, "w") as file:
            yaml.dump(data, file, Dumper=Dumper)


def find_launchflow_yaml(start_path="."):
    current_path = os.path.abspath(start_path)

    while True:
        file_path = os.path.join(current_path, "launchflow.yaml")
        if os.path.isfile(file_path):
            return file_path

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            break

        current_path = parent_path

    return None


launchflow_config = None


def load_launchflow_dot_yaml():
    global launchflow_config
    if launchflow_config is None:
        launchflow_config = LaunchFlowDotYaml.load_from_cwd()
    return launchflow_config


if __name__ == "__main__":
    # create a new LaunchFlowDotYaml instance
    config = LaunchFlowDotYaml(
        project="my-project",
        environment="production",
        services=[
            ServiceConfig(
                name="my-service",
                product="gcp_cloud_run",
                product_config=GcpCloudRunConfig(location="us-central1", num_cpus=4),
            ),
        ],
    )
    # save the configuration to a file
    config.save_to_file("launchflow.yaml")
