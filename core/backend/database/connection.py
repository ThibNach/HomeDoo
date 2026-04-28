import json
import psycopg2

from pathlib import Path
from psycopg2 import sql, OperationalError
from psycopg2.extras import RealDictCursor

from config import config


class Database:

    def fetch_all(self, table_name, cursor=None):
        query = sql.SQL("SELECT * FROM {}").format(
            sql.Identifier(table_name)
        )
        return self._execute_query(query, cursor=cursor)

    def fetch_where(self, table_name, params=None, cursor=None):
        conditions = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(sql.Identifier(key), sql.Placeholder())
            for key in params.keys()
        )

        values = list(params.values())

        query = sql.SQL("SELECT * FROM {} WHERE {}").format(
            sql.Identifier(table_name),
            conditions
        )
        return self._execute_query(query, values, cursor)

    def fetch_join(self, table_1, table_2, column_1, column_2, conditions: dict, target='*', cursor=None):
        where = sql.SQL(" AND ").join(
            sql.SQL("{} = {}").format(
                sql.Identifier(key), sql.Placeholder()
            )
            for key in conditions.keys()
        )

        values = list(conditions.values())

        if target == "*":
            target_sql = sql.SQL('*')
        else:
            target_sql = sql.SQL(", ").join(sql.SQL("{}.{}").format(
                sql.Identifier(table), sql.Identifier(column))
                                            for table, column in target
                                            )

        query = sql.SQL("SELECT {} FROM {} JOIN {} ON {}.{} = {}.{} WHERE {}").format(
            target_sql,
            sql.Identifier(table_1),
            sql.Identifier(table_2),
            sql.Identifier(table_1), sql.Identifier(column_1),
            sql.Identifier(table_2), sql.Identifier(column_2),
            where
        )

        return self._execute_query(query, values, cursor=cursor)

    def insert_item(self, table_name, table_data: dict, cursor=None, returning=None):
        fields = sql.SQL(', ').join(sql.Identifier(data) for data in table_data.keys())
        placeholders = sql.SQL(', ').join(sql.Placeholder() * len(table_data))
        values = list(table_data.values())

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            fields,
            placeholders
        )

        if returning:
            query = query + sql.SQL(" RETURNING {}").format(sql.Identifier(returning))
            return self._execute_query(query, values, cursor=cursor)

        self._execute_command(query, values, cursor=cursor)

    def update_item(self, table_name, updates: dict, conditions: dict, cursor=None):
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
        self._execute_command(query, update_values + where_values, cursor)

    def delete_item(self, table_name, conditions: dict, cursor=None):
        where = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(key),
                sql.Placeholder())
            for key in conditions.keys())
        values = list(conditions.values())

        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(table_name),
            where
        )

        self._execute_command(query, values, cursor)

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
                            columns = []
                            for column in table["columns"]:
                                references_sql = ""
                                if column.get("references"):
                                    ref = column["references"]
                                    references_sql = f"REFERENCES {ref['module']}_{ref['table']}({ref['column']})"
                                    if ref.get("on_delete"):
                                        references_sql += f" ON DELETE {ref['on_delete']}"

                                columns.append(sql.SQL("{} {}").format(
                                    sql.Identifier(column["name"]),
                                    sql.SQL(f"{column['type']} {column['constraints']} {references_sql}")
                                ))

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

    def execute_transaction(self, callback):
        with self._connect() as connection:
            try:
                with connection.cursor() as cursor:
                    result = callback(cursor)
                connection.commit()
                return result
            except psycopg2.Error as e:
                connection.rollback()
                raise RuntimeError(f"transaction error : {e}")

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

    def _execute_query(self, query, values=None, cursor=None):
        if cursor is not None:
            cursor.execute(query, values)
            return cursor.fetchall()

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                    return cursor.fetchall()
        except psycopg2.Error as e:
            raise (RuntimeError(f"Query execution failed on {query} : {e} "))

    def _execute_command(self, query, values=None, cursor=None):
        if cursor is not None:
            cursor.execute(query, values)
            return

        with self._connect() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                connection.commit()
            except psycopg2.Error as e:
                connection.rollback()
                raise (RuntimeError(f"Command execution failed on {query} : {e}"))


database = Database()
