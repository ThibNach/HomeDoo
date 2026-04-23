import importlib
import json
import sys

from pathlib import Path

from database import database
from modules_repository import modules_repository
from utils import singleton

ADDONS_DIR = "addons"
CORE_ADDONS_DIR = "core/addons"
MODULE_FILE = "module.json"
BACKEND_DIR = "backend"

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

@singleton
class Registry:

    def fetch_addons(self, path):

        modules = {}
        for directory in Path.iterdir(project_root / path):
            if directory.is_dir():
                manifest = directory / MODULE_FILE
                if manifest.exists():
                    with open(manifest) as file:
                        try:
                            loaded_manifest = json.load(file)
                            loaded_manifest["path"] = directory
                            modules[loaded_manifest["name"]] = loaded_manifest
                        except json.JSONDecodeError as e:
                            raise ValueError(f"invalid Json file : {e}")
    
        return modules

    def sort_by_dependencies(self, manifests):
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


    def register_addons(self, app):
        loaded_addons = []
        gathered_addons = self.fetch_addons(project_root / CORE_ADDONS_DIR)
        gathered_addons.update(self.fetch_addons(project_root / ADDONS_DIR))
        sorted_addons = self.sort_by_dependencies(gathered_addons)
        installed_addons_names = [module.get("name") for module in modules_repository.get_all_installed()]
        for addon in sorted_addons:
            manifest = gathered_addons.get(addon)
            if addon not in installed_addons_names and not manifest.get("core_module"):
                continue
            if manifest.get("db_schema_path"):
                database.create_tables_if_not_exist(manifest["path"] / manifest["db_schema_path"], manifest["name"])
    
            loaded_addons.append(manifest)
            parts = Path(manifest.get("path") / BACKEND_DIR).parts
            start = parts.index(CORE_ADDONS_DIR.split('/')[0]) if manifest.get("core_module") else parts.index(ADDONS_DIR)
            module_name = '.'.join(parts[start:])
            importlib.import_module(module_name).setup(app)
    
        return loaded_addons
