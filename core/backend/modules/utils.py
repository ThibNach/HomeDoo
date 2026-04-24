import json
from pathlib import Path

def load_manifest(module_path: Path) -> dict:
    manifest_path = module_path / "module.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No module.json in {module_path}")

    with open(manifest_path) as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {manifest_path}: {e}")