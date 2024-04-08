import enum
import importlib
import io
import os
import sys
import tarfile
from datetime import datetime, timezone
from typing import Any, Dict, List

import yaml
from pathspec import PathSpec


def import_from_string(import_str: str) -> Any:
    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        message = (
            'Import string "{import_str}" must be in format "<module>:<attribute>".'
        )
        raise ValueError(message.format(import_str=import_str))

    try:
        module = importlib.import_module(module_str)
    except ImportError as exc:
        if exc.name != module_str:
            raise exc from None
        message = 'Could not import module "{module_str}".'
        raise ValueError(message.format(module_str=module_str))

    instance = module
    try:
        for attr_str in attrs_str.split("."):
            instance = getattr(instance, attr_str)
    except AttributeError:
        message = 'Attribute "{attrs_str}" not found in module "{module_str}".'
        raise ValueError(message.format(attrs_str=attrs_str, module_str=module_str))

    # Clear cache to allow reloading of module
    del sys.modules[module_str]

    return instance


_keys_to_convert = ["verified_at", "created_at", "updated_at"]


def _preprocess_dict(d):
    """Converts timestamps to human readable local times."""
    for key, value in d.items():
        if key in _keys_to_convert and isinstance(value, datetime):
            try:
                utc_time = value.replace(tzinfo=timezone.utc)
                local_time = utc_time.astimezone()
                d[key] = local_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            except ValueError:
                pass
        elif isinstance(value, dict):
            _preprocess_dict(value)
        elif isinstance(value, enum.Enum):
            d[key] = value.value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _preprocess_dict(item)

    return d


def json_to_yaml(json_dict: Dict[str, Any]) -> str:
    return yaml.dump(json_dict, default_flow_style=False, sort_keys=False, indent=4)


def print_response(header: str, response: Dict[str, Any]):
    response = _preprocess_dict(response)
    print(header)
    print("-" * len(header))
    print(json_to_yaml(response))


def tar_source_in_memory(
    directory: str = ".",
    ignore_patterns: List[str] = [
        "*.log",
        "__pycache__/",
        ".env",
        ".git/",
        ".terraform/",
        ".terraform.lock.hcl",
    ],
):
    def should_include_file(pathspec: PathSpec, file_path: str, root_dir: str):
        relative_path = os.path.relpath(file_path, root_dir)
        return not pathspec.match_file(relative_path)

    pathspec = PathSpec.from_lines("gitwildmatch", ignore_patterns)

    # Use BytesIO object as an in-memory file
    in_memory_tar = io.BytesIO()

    # Open the tarfile using the in-memory file-like object
    with tarfile.open(fileobj=in_memory_tar, mode="w:gz") as tar:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if should_include_file(pathspec, file_path, directory):
                    tar.add(file_path, arcname=os.path.relpath(file_path, directory))

    # Seek to the beginning of the in-memory file
    in_memory_tar.seek(0)

    # Return the in-memory file
    return in_memory_tar
