import bcrypt

from core.backend import database


class AuthRepository:
    
    def create_person_with_account(self, name, email, password):
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        def operations(cursor):
            result = database.insert_item(
                "auth_persons",
                {"name" : name },
                cursor = cursor,
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
    
    def create_person(self):
        pass
    
    def create_account(self):
        pass
    
    
auth_repository = AuthRepository()