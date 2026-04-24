import json
import os
import zipfile
import shutil
from urllib.request import urlretrieve
from pathlib import Path

from database import database
from .repository import modules_repository
from .utils import load_manifest
from utils import singleton

MAIN_BRANCH_NAME = "main"
ADDONS_DIR = "addons"

project_root = Path(__file__).parent.parent.parent.parent

@singleton
class ModuleInstaller:
    
    def install(self, git_url):

        if modules_repository.get_by_source_url(git_url):
            raise ValueError(f"A module from {git_url} is already installed")
        
        zip_url =f"{git_url}/archive/refs/heads/{MAIN_BRANCH_NAME}.zip"
        zip_path = project_root / ADDONS_DIR / "temp.zip"
        urlretrieve(zip_url,zip_path)

        with zipfile.ZipFile(zip_path) as zip_file:
            root_dir = zip_file.namelist()[0].split('/')[0]
            zip_file.extractall(project_root / ADDONS_DIR)

        extracted_path = project_root / ADDONS_DIR / root_dir
        manifest = load_manifest(extracted_path)
        extracted_path.rename(project_root / ADDONS_DIR / manifest["name"].lower())

        # TODO: status set directly to "enabled" for auto-loading on restart.
        # To add a validation step, introduce an intermediate "installed" status
        # and an /modules/enable endpoint to handle the transition.

        modules_repository.add_module(
            name=manifest["name"],
            version=manifest.get("version", "1.0.0"),
            source_url=git_url,
            status="enabled"
        )
        
        os.remove(zip_path)
        
        
    
    def uninstall(self, module_name,  keep_data=True):
        loaded_addons = modules_repository.get_all_installed()
        
        found = any(module_name.lower() == m["name"].lower() for m in loaded_addons)
        
        if not found:
            raise ValueError(f"{module_name} not found in installed module, impossible to uninstall")
        
        for addon in loaded_addons:
            path = project_root / ADDONS_DIR / addon["name"].lower()
            manifest = load_manifest(path)
            if module_name.lower() in manifest.get("dependencies",[]):
                raise RuntimeError(f"{module_name} is a dependency of {manifest.get('name')}, impossible to uninstall")
        
        path_to_remove = project_root / ADDONS_DIR / (module_name.lower())

        if not keep_data:
            manifest = load_manifest(path_to_remove)
            db_schema_path = manifest["db_schema_path"]
            
            if db_schema_path:
                with open(path_to_remove/db_schema_path) as db_schema:
                    tables_schema = json.load(db_schema)
                    for table in tables_schema.get("tables", []):
                        database.drop_table_if_exists(f"{module_name.lower()}_{table['name']}")
        
        shutil.rmtree(path_to_remove)
        
        modules_repository.remove_module({"name" : module_name})

        
                