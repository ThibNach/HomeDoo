import json
import psycopg2

from pathlib import Path
from psycopg2 import sql, OperationalError
from psycopg2.extras import RealDictCursor

from config import config


class Database:

    def fetch_all(self, table_name):
        query = sql.SQL("SELECT * FROM {}").format(
            sql.Identifier(table_name)
        )
        return self._execute_query(query)


    def fetch_where(self, table_name, params=None):
        conditions = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(sql.Identifier(key), sql.Placeholder())
            for key in params.keys()
        )

        values = list(params.values())

        query = sql.SQL("SELECT * FROM {} WHERE {}").format(
            sql.Identifier(table_name),
            conditions
        )
        return self._execute_query(query, values)

    def insert_item(self, table_name, table_data: dict):
        fields = sql.SQL(', ').join(sql.Identifier(data) for data in table_data.keys())
        placeholders = sql.SQL(', ').join(sql.Placeholder() * len(table_data))
        values = list(table_data.values())

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            fields,
            placeholders
        )

        self._execute_command(query, values)

    def update_item(self, table_name, updates: dict, conditions: dict):
        update = sql.SQL(', ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(field),
                sql.Placeholder())
            for field in updates.keys())
        update_values = list(updates.values())

        where = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(sql.Identifier(key), sql.Placeholder())
            for key in conditions.keys())
        where_values = list(conditions.values())

        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(table_name),
            update,
            where
        )
        self._execute_command(query, update_values + where_values)

    def delete_item(self, table_name, conditions: dict):
        where = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(key)            ,
                sql.Placeholder())
                for key in conditions.keys() )
        values = list(conditions.values())
            
        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(table_name),
            where
        )
        
        self._execute_command(query, values)

    def create_db_if_not_exists(self):
        connection = self._connect("postgres")  # Cannot use with statement because create db can not be a transaction
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config.DB_NAME,))

            if not cursor.fetchone():
                cursor.execute(sql
                               .SQL("CREATE DATABASE {}")
                               .format(sql.Identifier(config.DB_NAME)))

            connection.close()

    def create_tables_if_not_exist(self, schema_path, module_name):
        if Path(schema_path).suffix != ".json":
            raise ValueError("tried to create tables from bad extension file")

        with(open(schema_path)) as schema_file:
            schema = json.load(schema_file)
            with self._connect() as connection:
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

    def drop_table_if_exists(self, table_name):
        query = sql.SQL("DROP TABLE IF EXISTS {}").format(
            sql.Identifier(table_name)
        )
        self._execute_command(query)

    def _connect(self, db_name=None):
        try:
            return psycopg2.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                dbname=db_name if db_name is not None else config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
        except OperationalError as e:
            raise ConnectionError(f"Failed to connect to database {db_name} : {e}")

    def _execute_query(self, query, values=None):
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                    return cursor.fetchall()
        except psycopg2.Error as e:
            raise (RuntimeError(f"Query execution failed on {query} : {e} "))

    def _execute_command(self, query, values=None):
        with self._connect() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                connection.commit()
            except psycopg2.Error as e:
                connection.rollback()
                raise (RuntimeError(f"Command execution failed on {query} : {e}"))


database = Database()
