'''Postgres Schema Management
'''
import datetime as dt
import logging
from threading import Event

import psycopg
from psycopg.rows import dict_row

from smartfin_data_api.utils import do_query


class PostgresSchema:
    """Postgres Management tool
    """
    VERSION = 1

    def __init__(self, host: str, user: str, password: str, database: str):
        self.__pg_conn = f'postgresql://{user}:{password}@{host}/{database}'
        self.__ready_event = Event()
        self.__log = logging.getLogger('PostgresSchema')

    def migrate(self):
        """Migrate table definition
        """
        with psycopg.connect(self.__pg_conn, row_factory=dict_row) as con, con.cursor() as cur:
            try:
                with con.transaction():
                    do_query(
                        path='sql/select_schema_version.sql',
                        cur=cur
                    )
                    version = cur.fetchone()['version']
            except psycopg.Error:
                do_query(
                    path='sql/create_tables_0001.sql',
                    cur=cur
                )
                self.__log.info('Upgrading DB to version 1')
                version = 1
        self.__log.info('db at version %d', version)
        self.__ready_event.set()

    def wait_ready(self, **kwargs):
        """Waits for the database to be ready
        """
        self.__ready_event.wait(**kwargs)

    def insert_record(self,
                      published_at: dt.datetime,
                      event: str,
                      data: str,
                      coreid: str,
                      fw_version: int) -> None:
        with psycopg.connect(self.__pg_conn, row_factory=dict_row) as con, con.cursor() as cur:
            do_query(
                path='sql/insert_record.sql',
                cur=cur,
                params={
                    'published_at': published_at,
                    'event': event,
                    'data': data,
                    'coreid': coreid,
                    'fw_version': fw_version
                }
            )
