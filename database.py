"""Database connection using psycopg2. Use get_cursor() for queries."""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

_connection = None


def get_connection():
    """Return a connection. Uses Flask g per-request when in app context to avoid 'cursor already closed'."""
    try:
        from flask import g
        if not hasattr(g, "_db_connection"):
            g._db_connection = psycopg2.connect(DATABASE_URL)
        return g._db_connection
    except (ImportError, RuntimeError):
        pass
    global _connection
    if _connection is None or _connection.closed:
        _connection = psycopg2.connect(DATABASE_URL)
    return _connection


def get_cursor():
    """Return a dict cursor (rows as dicts). Use with 'with get_cursor() as cur:'."""
    return get_connection().cursor(cursor_factory=RealDictCursor)


def close_connection():
    """Close connection for current request (Flask g) or global fallback."""
    try:
        from flask import g
        if hasattr(g, "_db_connection") and g._db_connection and not g._db_connection.closed:
            g._db_connection.close()
            g._db_connection = None
    except (ImportError, RuntimeError, AttributeError):
        pass
    global _connection
    if _connection and not _connection.closed:
        _connection.close()
        _connection = None
