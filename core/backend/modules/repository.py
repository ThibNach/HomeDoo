from database import database
from modules.installer_module import InstalledModule

MODULES_TABLE_NAME = "core_installed_modules"


class ModulesRepository:

    def get_all_installed(self) -> list[InstalledModule]:
        rows = database.fetch_all(MODULES_TABLE_NAME)
        return [InstalledModule.from_db_row(row) for row in rows]

    def get_by_name(self, name) -> InstalledModule | None:
        rows = database.fetch_where(MODULES_TABLE_NAME, {"name": name})
        return InstalledModule.from_db_row(rows[0]) if rows else None
    
    def get_by_source_url(self, source_url):
        return database.fetch_where(MODULES_TABLE_NAME, {"source_url" : source_url})

    def add_module(self, name, version, source_url, status="installed"):
        data = {"name": name, "version": version, "source_url": source_url, "status": status}
        return database.insert_item(MODULES_TABLE_NAME, data)

    def update_status(self, name, new_status):
        return database.update_item(MODULES_TABLE_NAME, {"status": new_status}, {"name": name})

    def remove_module(self, conditions):
        return database.delete_item(MODULES_TABLE_NAME, conditions)


modules_repository = ModulesRepository()
