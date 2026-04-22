import importlib
import json
import sys

from pathlib import Path

from database import Database

ADDONSDIR = "addons"
MODULEFILE = "module.json"
BACKENDDIR = "backend"

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def fetch_addons():
    path = project_root / ADDONSDIR
    modules = {}
    for directory in Path.iterdir(path):
        if directory.is_dir():
            manifest = directory / MODULEFILE
            if manifest.exists():
                with open(manifest) as file:
                    try:
                        loaded_manifest = json.load(file)
                        loaded_manifest["path"] = directory
                        modules[loaded_manifest["name"]] = loaded_manifest
                    except json.JSONDecodeError as e:
                        raise ValueError(f"invalid Json file : {e}")

    return modules


def sort_by_dependencies(manifests):
    dependencies = {v["name"]: v.get("dependencies", []) for v in manifests.values()}
    degrees = {name: len(dep) for name, dep in dependencies.items()}
    queue = [name for name, count in degrees.items() if count == 0]

    order_list = []
    while queue:
        current = queue.pop(0)
        order_list.append(current)
        for k, v in dependencies.items():
            if current in v:
                degrees[k] -= 1
                if degrees.get(k) == 0:
                    queue.append(k)

    if len(order_list) < len(manifests):
        raise ValueError("Circular dependencies in modules detected")

    return order_list


def register_addons(app):
    loaded_addons = []
    gathered_addons = fetch_addons()
    sorted_addons = sort_by_dependencies(gathered_addons)
    for addon in sorted_addons:

        manifest = gathered_addons.get(addon)
        if manifest.get("db_schema_path"):
            Database().create_tables_if_not_exist(manifest["path"] / manifest["db_schema_path"], manifest["name"])

        loaded_addons.append(manifest)

        parts = Path(manifest.get("path") / BACKENDDIR).parts
        module_name = '.'.join(parts[parts.index(ADDONSDIR):])
        importlib.import_module(module_name).setup(app)

    return loaded_addons
