import json
import psycopg2
from pathlib import Path

from config import config


def connect_db(db_name = config.DB_NAME):
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=db_name,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )


def create_db_if_not_exists():
    connection = connect_db("postgres")
    connection.autocommit = True
    cursor = connection.cursor()

    db_exist_query = f"SELECT 1 FROM pg_database WHERE datname = '{config.DB_NAME}'"
    cursor.execute(db_exist_query)

    if not cursor.fetchone():
        create_db_query = f"CREATE DATABASE {config.DB_NAME}"
        cursor.execute(create_db_query)

    cursor.close()
    connection.close()


def create_tables_if_not_exist(schema_path):
    if Path(schema_path).suffix != ".json":
        raise ValueError("tried to create tables from bad extension file")
    
    schema = json.load(open(schema_path))

    connection = connect_db()
    connection.autocommit= True
    cursor = connection.cursor()
    
    for table in schema["tables"]:
        columns = [' '.join(column.values()) for column in table["columns"]]
        query = f"CREATE TABLE IF NOT EXISTS {table["name"]} ({','.join(columns)})"
    
        cursor.execute(query)

    cursor.close()
    connection.close()
        
        
    
    