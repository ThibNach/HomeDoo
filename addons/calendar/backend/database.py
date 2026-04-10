from core.backend import connect_db


def init_db():
    create_tables_if_not_exists()


def create_tables_if_not_exists():
    connection = connect_db()
    connection.autocommit= True
    cursor = connection.cursor()

    entries_table_query = """
                        CREATE TABLE IF NOT EXISTS entries
                        (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            start_datetime TIMESTAMP NOT NULL,
                            end_datetime TIMESTAMP,
                            all_day BOOLEAN DEFAULT FALSE
                        ) 
                        """

    cursor.execute(entries_table_query)
    cursor.close()
    connection.close()
    