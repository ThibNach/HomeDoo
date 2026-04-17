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
    _instance = None
    
    def __post_init__(self):
        self.FLASK_PORT : str = _require_env_variable("FLASK_PORT")
        self.DB_NAME :str = _require_env_variable("DB_NAME")
        self.DB_HOST :str = _require_env_variable("DB_HOST")
        self.DB_PORT :str = _require_env_variable("DB_PORT")
        self.DB_USER :str = _require_env_variable("DB_USER")
        self.DB_PASSWORD :str = _require_env_variable("DB_PASSWORD")

    @classmethod
    def get_config(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return
        super().__new__(cls)
        cls._instance.__init__()



def get_config():
    return Config.get_config()