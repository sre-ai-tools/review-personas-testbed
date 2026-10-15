"""Postgres access. Every query is parameterised: never build SQL from request data."""

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Any

import boto3
import psycopg
from psycopg import Cursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

# A Lambda instance serves one request at a time, so it keeps one connection.
_conn: psycopg.Connection | None = None


@lru_cache(maxsize=1)
def _credentials() -> dict[str, str]:
    secret = boto3.client("secretsmanager").get_secret_value(SecretId=os.environ["DB_SECRET_ARN"])
    return json.loads(secret["SecretString"])


def _connect() -> psycopg.Connection:
    creds = _credentials()
    return psycopg.connect(
        make_conninfo(
            host=os.environ["DB_HOST"],
            dbname=os.environ["DB_NAME"],
            user=creds["username"],
            password=creds["password"],
            sslmode="require",
            connect_timeout=5,
        )
    )


def _connection() -> psycopg.Connection:
    global _conn
    if _conn is None or _conn.closed or _conn.broken:
        try:
            _conn = _connect()
        except psycopg.OperationalError:
            # RDS rotates the managed secret; re-read it once in case the cached one is stale.
            _credentials.cache_clear()
            _conn = _connect()
    return _conn


@contextmanager
def transaction() -> Iterator[Cursor[dict[str, Any]]]:
    conn = _connection()
    with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        yield cur


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with transaction() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with transaction() as cur:
        cur.execute(sql, params)
        return cur.fetchall()
