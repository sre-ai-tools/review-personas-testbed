"""Postgres access. Every query is parameterised: never build SQL from request data."""

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Any

import boto3
from psycopg import Cursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


@lru_cache(maxsize=1)
def _pool() -> ConnectionPool:
    secret = boto3.client("secretsmanager").get_secret_value(SecretId=os.environ["DB_SECRET_ARN"])
    creds = json.loads(secret["SecretString"])
    conninfo = make_conninfo(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=creds["username"],
        password=creds["password"],
        sslmode="require",
        connect_timeout=5,
    )
    # One Lambda instance serves one request at a time, so a tiny pool is enough.
    return ConnectionPool(conninfo, min_size=1, max_size=2, open=True)


@contextmanager
def transaction() -> Iterator[Cursor[dict[str, Any]]]:
    with _pool().connection() as conn, conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        yield cur


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with transaction() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with transaction() as cur:
        cur.execute(sql, params)
        return cur.fetchall()
