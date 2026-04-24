import os
import zipfile
from urllib.request import urlretrieve
from pathlib import Path

from utils import singleton

MAIN_BRANCH_NAME = "main"
ADDONS_DIR = "addons"

project_root = Path(__file__).parent.parent.parent.parent

@singleton
class ModuleInstaller:
    
    def install(self, git_url):
        zip_url =f"{git_url}/archive/refs/heads/{MAIN_BRANCH_NAME}.zip"
        zip_path = project_root / ADDONS_DIR / "temp.zip"
        urlretrieve(zip_url,zip_path)
        
        zipfile.ZipFile(zip_path).extractall(project_root / ADDONS_DIR)
        
        os.remove(zip_path)
    
    def uninstall(self, module_name):
        pass