from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class InstalledModule:
    name: str
    version: str
    source_url: str
    status: str  # 'enabled', 'disabled', 'pending_removal'
    id: int | None = None
    installed_at: datetime | None = None

    @classmethod
    def from_db_row(cls, row: dict) -> "InstalledModule":
        return cls(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            source_url=row["source_url"],
            status=row["status"],
            installed_at=row.get("installed_at")
        )

    def to_json_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "source_url": self.source_url,
            "status": self.status,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None
        }
