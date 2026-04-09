from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()

@dataclass
class Config:
    FLASK_PORT : str = os.getenv("FLASK_PORT")
    DB_NAME :str = os.getenv("DB_NAME")
    DB_HOST :str = os.getenv("DB_HOST")
    DB_PORT :str = os.getenv("DB_PORT")
    DB_USER :str = os.getenv("DB_USER")
    DB_PASSWORD :str = os.getenv("DB_PASSWORD")

config = Config()