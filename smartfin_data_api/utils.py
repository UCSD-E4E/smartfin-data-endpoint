'''SQL Utilities
'''
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psycopg

from smartfin_data_api.metrics import get_summary

__log = logging.getLogger('SQL')


def load_query(path: Path) -> str:
    """Loads query from path

    Args:
        path (Path): Path to query file

    Returns:
        str: Query contents
    """
    with open(path, 'r', encoding='utf-8') as handle:
        return handle.read(int(1e9))


def do_query(path: Union[Path, str], cur: psycopg.Cursor, params: Optional[Dict[str, Any]] = None):
    """Convenience function to time and execute a query

    Args:
        path (Union[Path, str]): Path to query file
        cur (psycopg.Cursor): Cursor
        params (Optional[Dict[str, Any]]): Query parameters.  Defaults to None
    """
    path = Path(path)
    query_timer = get_summary('query_duration')
    with query_timer.labels(query=path.stem).time():
        cur.execute(
            query=load_query(path),
            params=params
        )


def do_dynamic_query(path: Union[Path, str], cur: psycopg.Cursor, params: Optional[Dict[str, Any]]):
    """Convenience function to time and execute a query parameterized using Python format_map

    Args:
        path (Union[Path, str]): Path to query file
        cur (psycopg.Cursor): Cursor
        params (Optional[Dict[str, Any]]): Query parameters.
    """
    path = Path(path)
    query_timer = get_summary('query_duration')
    query_template = load_query(path)
    query = query_template.format_map(params)
    try:
        with query_timer.labels(query=path.stem).time():
            cur.execute(
                query=query
            )
    except psycopg.errors.Error as exc:
        __log.exception('Query during failure: %s', query)
        raise exc


def do_many_query(path: Union[Path, str],
                  cur: psycopg.Cursor,
                  param_seq: List[Dict[str, Any]],
                  returning: bool = False) -> None:
    """Convenience function to time and executemany

    Args:
        path (Union[Path, str]): Path to query file
        cur (psycopg.Cursor): Cursor
        param_seq (List[Dict[str, Any]]): Query parameters
        returning (bool, optional): Flag indicating whether or not this query returns data. Defaults
        to False.
    """
    path = Path(path)
    query_timer = get_summary('query_duration')
    with query_timer.labels(query=path.stem).time():
        cur.executemany(
            query=load_query(path),
            params_seq=param_seq,
            returning=returning
        )
