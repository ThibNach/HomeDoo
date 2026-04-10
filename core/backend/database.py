import json
import psycopg2

from pathlib import Path
from psycopg2 import sql, OperationalError

from config import config


def connect_db(db_name = config.DB_NAME):
    try:
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=db_name,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
    except OperationalError as e:
        raise ConnectionError(f"Failed to connect to database {db_name} : {e}")


def create_db_if_not_exists():
    connection = connect_db("postgres")
    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s",(config.DB_NAME,))

    if not cursor.fetchone():
        cursor.execute(sql
                       .SQL("CREATE DATABASE {}")
                       .format(sql.Identifier(config.DB_NAME)))

    cursor.close()
    connection.close()


def create_tables_if_not_exist(schema_path):
    if Path(schema_path).suffix != ".json":
        raise ValueError("tried to create tables from bad extension file")
    
    schema = json.load(open(schema_path))

    connection = connect_db()
    cursor = connection.cursor()
    
    try:
        for table in schema["tables"]:
            columns = [
                sql.SQL("{} {}").format(
                    sql.Identifier(column["name"]),
                    sql.SQL(f"{column['type']} {column['constraints']}")
                )
                for column in table["columns"]
            ]
        
            query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table["name"]),
                sql.SQL(',').join(columns)
)       
            
            cursor.execute(query)
        
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error : {e}")
    finally:
        cursor.close()
        connection.close()
        
        
    
    