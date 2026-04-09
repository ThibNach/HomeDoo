from core.backend import connect_db, create_db_if_not_exists

DBNAME = "db_calendar"


def init_db():
    create_db_if_not_exists(DBNAME)

    connection = connect_db(DBNAME)
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
