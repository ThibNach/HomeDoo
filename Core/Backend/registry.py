import json
from pathlib import Path

ADDONSDIR = "AddOns"
MODULEFILE = "module.json"

def fetch_addons():
    path = Path(__file__).parent.parent.parent / ADDONSDIR
    modules = []
    for directory in Path.iterdir(path):
        if directory.is_dir():
            manifest = directory / MODULEFILE
            if manifest.exists():
                modules.append(directory)
    return modules


def load_addons( directory ):
    return json.load(open(directory / MODULEFILE))


def register_addons():
    loaded_addons = []
    for module in fetch_addons():
        loaded_addons.append(load_addons(module))
    return loaded_addons