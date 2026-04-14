import json
import psycopg2

from pathlib import Path
from psycopg2 import sql, OperationalError
from psycopg2.sql import Identifier

from config import config


def connect_db(db_name=config.DB_NAME):
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
    connection  = connect_db("postgres") #Cannot use with statement because create db can not be a transaction
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config.DB_NAME,))

        if not cursor.fetchone():
            cursor.execute(sql
                           .SQL("CREATE DATABASE {}")
                           .format(sql.Identifier(config.DB_NAME)))
            
    connection.close()


def create_tables_if_not_exist(schema_path, module_name):
    if Path(schema_path).suffix != ".json":
        raise ValueError("tried to create tables from bad extension file")

    with(open(schema_path)) as schema_file:
        schema = json.load(schema_file)
        with connect_db() as connection:
            with connection.cursor() as cursor:
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
                            sql.Identifier(f"{module_name.lower()}_{table["name"].lower()}"),
                            sql.SQL(',').join(columns)
                        )

                        cursor.execute(query)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    raise Exception(f"Error : {e}")


def fetch_all(table_name, params=None):
    query = sql.SQL("SELECT * FROM {}").format(
        sql.Identifier(table_name)
    )
    try:
        return _execute_query(query)
    except psycopg2.Error as e:
        raise (RuntimeError(f"Fetch failed on {table_name} : {e}"))


def insert_item(table_name,table_data:dict):
    fields = sql.SQL(', ').join(sql.Identifier(data) for data in table_data.keys())
    placeholders = sql.SQL(', ').join(sql.Placeholder() * len(table_data))
    values = list(table_data.values())
    
    
    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table_name),
        fields,
        placeholders        
    )    
        
    with connect_db() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query,values)
            connection.commit()
        except psycopg2.Error as e:
            connection.rollback()
            raise (RuntimeError(f"Insertion failed on {table_name} : {e}"))
    
    
    

def _execute_query(query):
    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
    except psycopg2.Error as e:
        raise (RuntimeError(f"Query execution failed on {query} : {e} "))

