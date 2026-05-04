from dotenv import load_dotenv
import os


env_file = load_dotenv()

if not env_file:
    raise EnvironmentError(f"Missing environment file")

def _require_env_variable(variable :str)-> str:
    value = os.getenv(variable)
    if value is None:
        raise EnvironmentError(f"missing required environment variable : {variable}")
    return value

class Config:
    
    def __init__(self):     
        self.FLASK_PORT : str = _require_env_variable("FLASK_PORT")
        self.DB_NAME :str = _require_env_variable("DB_NAME")
        self.DB_HOST :str = _require_env_variable("DB_HOST")
        self.DB_PORT :str = _require_env_variable("DB_PORT")
        self.DB_USER :str = _require_env_variable("DB_USER")
        self.DB_PASSWORD :str = _require_env_variable("DB_PASSWORD")
        self.ENVIRONMENT : str = _require_env_variable("ENVIRONMENT")
        self.JWT_SECRET : str = _require_env_variable("JWT_SECRET")


config = Config()