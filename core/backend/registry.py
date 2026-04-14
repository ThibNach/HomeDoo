import importlib
import json
import sys
from pathlib import Path
from database import create_tables_if_not_exist

ADDONSDIR = "addons"
MODULEFILE = "module.json"
BACKENDDIR = "backend"

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def fetch_addons():
    path = project_root / ADDONSDIR
    modules = []
    for directory in Path.iterdir(path):
        if directory.is_dir():
            manifest = directory / MODULEFILE
            if manifest.exists():
                modules.append(directory)
    return modules


def register_addons(app):
    loaded_addons = []
    for module in fetch_addons():
        try:
            with open( module / MODULEFILE) as file: #with statement handle the file close
                manifest = json.load(file)
                if manifest.get("db_schema_path"):
                    create_tables_if_not_exist(module / manifest["db_schema_path"], module.parts[-1])
                
                loaded_addons.append(file)

                parts = Path(module / BACKENDDIR).parts
                module_name = '.'.join(parts[parts.index(ADDONSDIR):])
                importlib.import_module(module_name).setup(app)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found : {module / MODULEFILE}")
        except json.JSONDecodeError as e:
            raise ValueError(f"invalid Json file : {e}")
                    
    return loaded_addons