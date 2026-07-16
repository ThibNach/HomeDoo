import json
from pathlib import Path

from modules.manifest import Manifest


def load_manifest(module_path: Path):
    manifest_path = module_path / "module.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No module.json in {module_path}")

    with open(manifest_path) as file:
        try:
            data = json.load(file)
            return Manifest.from_json(data, module_path)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {manifest_path}: {e}")