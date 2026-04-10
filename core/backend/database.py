import psycopg2

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
