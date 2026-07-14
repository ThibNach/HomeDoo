from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Manifest:
    """
    Represents a module's manifest, loaded from its module.json file.
    Enriched with the runtime path (where the module lives on disk).
    """

    name: str
    version: str
    core_module: bool = False
    display_name: str | None = None
    db_schema_path: str | None = None
    frontend_path: str | None = None
    frontend_init: str | None = None
    dependencies: list[str] = field(default_factory=list)
    path: Path | None = None

    @classmethod
    def from_json(cls, data: dict, module_path: Path) -> "Manifest":
        """Builds a Manifest from a parsed module.json content and its filesystem path."""
        return cls(
            name=data["name"],
            version=data.get("version", "0.0.0"),
            core_module=data.get("core_module", False),
            display_name=data.get("display_name"),
            db_schema_path=data.get("db_schema_path"),
            frontend_path=data.get("frontend_path"),
            frontend_init=data.get("frontend_init"),
            dependencies=data.get("dependencies", []),
            path=module_path
        )

    def to_json_dict(self) -> dict:
        """Serializable dict for API responses. Excludes backend-only fields."""
        return {
            "name": self.name,
            "version": self.version,
            "core_module": self.core_module,
            "display_name": self.display_name,
            "frontend_path": self.frontend_path,
            "frontend_init": self.frontend_init,
            "dependencies": self.dependencies,
        }
    