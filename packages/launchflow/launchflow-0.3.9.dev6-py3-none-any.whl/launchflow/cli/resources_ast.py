import ast
import importlib
import logging
import os
from typing import List

from launchflow.resource import Resource

# TODO: add primitive ones here.
# NOTE: We do this to ensure we don't trigger imports in files we don't need to.
# For instance if someone uses `launchflow.fastapi` in a file, we don't want to
# execute that file.
KNOWN_RESOURCE_IMPORT_PATHS = ["launchflow.gcp", "launchflow.aws"]


def _is_launchflow_resource(import_path: str) -> bool:
    maybe_resource = False
    for known_import in KNOWN_RESOURCE_IMPORT_PATHS:
        if known_import in import_path:
            maybe_resource = True
            break
    if not maybe_resource:
        return False
    split_path = import_path.split(".")
    resource_name = split_path[-1]
    module = ".".join(split_path[:-1])
    module_type = importlib.import_module(module)

    # This checks if the resource_name starts with a lowercase character to act as a
    # proxy check for the resource being a class. This is not foolproof but should
    # filter out most utility functions.
    if resource_name[0].islower():
        return False

    if hasattr(module_type, resource_name) and issubclass(
        getattr(module_type, resource_name), Resource
    ):
        return True
    return False


class LaunchFlowAssignmentVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.launchflow_imported_names = {}
        self.launchflow_vars = []
        self.nesting_level = 0

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "launchflow":
                self.launchflow_imported_names[
                    alias.asname if alias.asname else alias.name
                ] = "launchflow"

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module is not None and "launchflow" in node.module:
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                self.launchflow_imported_names[
                    alias.asname if alias.asname else alias.name
                ] = full_name
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Increase nesting level when entering a function
        self.nesting_level += 1
        self.generic_visit(node)  # Visit children
        # Decrease nesting level when leaving a function
        self.nesting_level -= 1

    def visit_AsyncFunctionDef(self, node):
        # Handle async functions similarly to regular functions
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ClassDef(self, node):
        # Increase nesting level when entering a class
        self.nesting_level += 1
        self.generic_visit(node)  # Visit children
        # Decrease nesting level when leaving a class
        self.nesting_level -= 1

    def visit_Assign(self, node):
        # Check to ensure the resource was assigned to a variable.
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            return
        # Check to ensure the value is a call to a function
        if not isinstance(node.value, ast.Call):
            return

        assigned_var = node.targets[0].id
        call_name = None
        if isinstance(node.value.func, ast.Name):
            call_name = self.launchflow_imported_names.get(node.value.func.id)
        elif isinstance(node.value.func, ast.Attribute):
            call_name = self._reconstruct_full_name(node.value.func)
        else:
            return
        if call_name and _is_launchflow_resource(call_name):
            if self.nesting_level != 0:
                logging.error(
                    "Resource is not defined as a global variable `%s` of type `%s` and will be ignored",
                    assigned_var,
                    call_name,
                )
                return
            self.launchflow_vars.append(assigned_var)

    def _reconstruct_full_name(self, node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name) and node.id in self.launchflow_imported_names:
            parts.append(self.launchflow_imported_names[node.id])
        else:
            return None
        parts.reverse()
        return ".".join(parts)


def find_launchflow_resources(directory: str):
    to_scan = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                to_scan.append(os.path.join(root, file))
    return _scan_for_resources(to_scan, root=directory)


def _scan_for_resources(files: List[str], root: str):
    resource_imports = []
    for file_path in files:
        with open(file_path, "r") as f:
            file_contents = f.read()
        tree = ast.parse(file_contents)
        finder = LaunchFlowAssignmentVisitor()
        finder.visit(tree)
        base_module_path = (
            os.path.relpath(file_path, root)[:-3].split(os.path.sep)
            if file_path.endswith(".py")
            else os.path.relpath(file_path, root).split(os.path.sep)
        )
        module_path = ".".join(base_module_path)
        for var in finder.launchflow_vars:
            resource_imports.append(f"{module_path}:{var}")
    return resource_imports
