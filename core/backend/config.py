from dotenv import load_dotenv
from dataclasses import dataclass
import os

env_file = load_dotenv()

if not env_file:
    raise EnvironmentError(f"Missing environment file")

def _require_env_variable(variable :str)-> str:
    value = os.getenv(variable)
    if value is None:
        raise EnvironmentError(f"missing required environment variable : {variable}")
    return value


@dataclass
class Config:
    
    def __post_init__(self):
        self.FLASK_PORT : str = _require_env_variable("FLASK_PORT")
        self.DB_NAME :str = _require_env_variable("DB_NAME")
        self.DB_HOST :str = _require_env_variable("DB_HOST")
        self.DB_PORT :str = _require_env_variable("DB_PORT")
        self.DB_USER :str = _require_env_variable("DB_USER")
        self.DB_PASSWORD :str = _require_env_variable("DB_PASSWORD")


config = Config()