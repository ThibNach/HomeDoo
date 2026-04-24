from database import database

MODULES_TABLE_NAME = "core_installed_modules"


class ModulesRepository:

    def get_all_installed(self):
        return database.fetch_all(MODULES_TABLE_NAME)

    def get_by_name(self, name):
        return database.fetch_where(MODULES_TABLE_NAME, {"name": name})
    
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
