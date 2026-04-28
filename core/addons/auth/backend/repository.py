import bcrypt

from .tokens import token_manager
from core.backend import database


class AuthRepository:
    def get_persons(self):
        return database.fetch_all("auth_persons")
        
    def create_person_with_account(self, name, email, password):
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        def operations(cursor):
            result = database.insert_item(
                "auth_persons",
                {"name": name},
                cursor=cursor,
                returning='id'
            )

            person_id = result[0]["id"]
            database.insert_item("auth_accounts", {
                "person_id": person_id,
                "email": email,
                "password_hash": password_hash
            }, cursor=cursor)

            return person_id

        return database.execute_transaction(operations)

    def create_person(self, person_name):
        database.insert_item("auth_persons", {"name": person_name})

    def delete_person(self, person_id):
        database.delete_item("auth_persons", {"id": person_id})

    def login(self, email, password):
        result = database.fetch_join(
            "auth_persons",
            "auth_accounts",
            "id",
            "person_id",
            {"email": email},
            "*"
        )

        if not result:
            return None  # account not found from given name

        account = result[0]

        if not bcrypt.checkpw(password.encode("utf-8"), account["password_hash"].encode("utf-8")):
            return None

        token = token_manager.generate({
            "person_id": account["id"],
            "name": account["name"]
        })

        return {
            "token": token,
            "person": {
                "id": account["id"],
                "name": account["name"],
                "email": account["email"]
            }
        }


auth_repository = AuthRepository()
