import psycopg2

from config import config


def connect_db(db_name):
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=db_name,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )


def create_db_if_not_exists(db_name):
    connection = connect_db("postgres")
    connection.autocommit = True
    cursor = connection.cursor()

    db_exist_query = f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
    cursor.execute(db_exist_query)

    if not cursor.fetchone():
        create_db_query = f"CREATE DATABASE {db_name}"
        cursor.execute(create_db_query)

    cursor.close()
    connection.close()
