from dulwich.porcelain import status

from database import database


class Repository:

    def get_all_installed(self):
        return database.fetch_all("core_installed_modules")

    def get_by_name(self, name):
        return database.fetch_where({"name": name})

    def add_module(self, name, version, source_url, status="installed"):
        data = {"name": name, "version": version, "source_url": source_url, "status": status}
        return database.insert_item("core_installed_modules", data)

    def update_status(self):
        pass

    def remove_module(self):
        pass


repository = Repository()
