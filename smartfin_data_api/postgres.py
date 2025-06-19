'''Postgres Schema Management
'''
from threading import Event

import psycopg
from psycopg.rows import dict_row
from utils import do_query


class PostgresSchema:
    VERSION = 1
    def __init__(self, host: str, user: str, password: str, database: str):
        self.__pg_conn = f'postgresql://{user}:{password}@{host}/{database}'
        self.__ready_event = Event()

    def migrate(self):
        with psycopg.connect(self.__pg_conn, row_factory=dict_row) as con, con.cursor() as cur:
            try:
                do_query(
                    path='sql/select_schema_version.sql',
                    cur=cur
                )
                version = cur.fetchone()['version']
            except Exception:
                do_query(
                    path='sql/create_tables_0001.sql',
                    cur=cur
                )
        self.__ready_event.set()
    
    def wait_ready(self, **kwargs):
        """Waits for the database to be ready
        """
        self.__ready_event.wait(**kwargs)
