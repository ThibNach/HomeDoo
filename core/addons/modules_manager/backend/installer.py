import json
import os
import zipfile
import shutil
import subprocess
from urllib.request import urlretrieve
from pathlib import Path

from database import database
from modules.repository import modules_repository
from modules.utils import load_manifest
from utils import singleton

from core.backend import config

MAIN_BRANCH_NAME = "main"
ADDONS_DIR = "addons"

project_root = Path(__file__).parent.parent.parent.parent.parent


@singleton
class ModuleInstaller:

    def install(self, git_url, name=None):

        if modules_repository.get_by_source_url(git_url):
            raise ValueError(f"A module from {git_url} is already installed")

        if config.ENVIRONMENT == 'development' and name:
            manifest = self._install_submodule(git_url, name)
        else:
            manifest = self._install_zip(git_url)

        # TODO: status set directly to "enabled" for auto-loading on restart.
        # To add a validation step, introduce an intermediate "installed" status
        # and an /modules/enable endpoint to handle the transition.

        modules_repository.add_module(
            name=manifest["name"],
            version=manifest.get("version", "1.0.0"),
            source_url=git_url,
            status="enabled"
        )

    def uninstall(self, module_name, keep_data=True):

        loaded_addons = modules_repository.get_all_installed()

        found = any(module_name.lower() == m["name"].lower() for m in loaded_addons)

        if not found:
            raise ValueError(f"{module_name} not found in installed module, impossible to uninstall")

        for addon in loaded_addons:
            path = project_root / ADDONS_DIR / addon["name"].lower()
            manifest = load_manifest(path)
            if module_name.lower() in manifest.get("dependencies", []):
                raise RuntimeError(f"{module_name} is a dependency of {manifest.get('name')}, impossible to uninstall")

        path_to_remove = project_root / ADDONS_DIR / (module_name.lower())

        if not keep_data:
            manifest = load_manifest(path_to_remove)
            db_schema_path = manifest["db_schema_path"]

            if db_schema_path:
                with open(path_to_remove / db_schema_path) as db_schema:
                    tables_schema = json.load(db_schema)
                    for table in tables_schema.get("tables", []):
                        database.drop_table_if_exists(f"{module_name.lower()}_{table['name']}")
        
        if config.ENVIRONMENT == "development" and self._is_submodule(module_name):
            self._uninstall_submodule(module_name)
        else:
            self._uninstall_zip(module_name)

        modules_repository.remove_module({"name": module_name})

    def _install_zip(self, git_url):

        zip_url = f"{git_url}/archive/refs/heads/{MAIN_BRANCH_NAME}.zip"
        zip_path = project_root / ADDONS_DIR / "temp.zip"
        urlretrieve(zip_url, zip_path)

        with zipfile.ZipFile(zip_path) as zip_file:
            root_dir = zip_file.namelist()[0].split('/')[0]
            zip_file.extractall(project_root / ADDONS_DIR)

        extracted_path = project_root / ADDONS_DIR / root_dir
        manifest = load_manifest(extracted_path)
        extracted_path.rename(project_root / ADDONS_DIR / manifest["name"].lower())

        os.remove(zip_path)

        return manifest

    def _install_submodule(self, git_url, name):

        relative_path = f"{ADDONS_DIR}/{name.lower()}"

        subprocess.run(
            ["git", "submodule", "add", git_url, str(relative_path)],
            cwd=str(project_root),
            check=True
        )

        return load_manifest( project_root / relative_path)

    def _is_submodule(self, module_name):

        git_modules_file = project_root / ".gitmodules"

        if not git_modules_file.exists():
            return False

        with open(git_modules_file) as modules_file:
            return f"{ADDONS_DIR}/{module_name.lower()}" in modules_file.read()

    def _uninstall_zip(self, module_name):

        path = project_root / ADDONS_DIR / module_name.lower()
        shutil.rmtree(path)

    def _uninstall_submodule(self, module_name):

        path = f"{ADDONS_DIR}/{module_name.lower()}"

        subprocess.run(
            ["git", "submodule", "deinit", "-f", path],
            cwd=str(project_root), check=True
        )
        subprocess.run(
            ["git", "config", "-f", ".gitmodules", "--remove-section", f"submodule.{path}"],
            cwd=str(project_root), check=False
        )
        subprocess.run(
            ["git", "add", ".gitmodules"],
            cwd=str(project_root), check=True
        )
        subprocess.run(
            ["git", "rm", "-f", path],
            cwd=str(project_root), check=True
        )

        git_module_path = project_root / ".git" / "modules" / ADDONS_DIR / module_name.lower()
        shutil.rmtree(git_module_path, ignore_errors=True)
