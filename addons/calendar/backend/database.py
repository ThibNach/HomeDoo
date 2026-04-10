from pathlib import Path

from core.backend import connect_db,create_tables_if_not_exist


def init_db():
    create_tables_if_not_exist( Path(__file__).parent / "tables_schema.json" )

    