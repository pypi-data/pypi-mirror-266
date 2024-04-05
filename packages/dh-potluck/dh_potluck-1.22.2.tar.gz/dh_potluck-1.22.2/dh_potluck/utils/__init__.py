from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from flask import current_app


def get_db():
    return current_app.extensions['dh-potluck']._db


def is_truthy(value):
    if isinstance(value, str):
        return value.lower() in ['true', '1']
    return bool(value)


def ensure_charset_in_uri(db_uri: str, *, charset: str = 'utf8mb4') -> str:
    parts = urlparse(db_uri)
    query = parse_qs(parts.query)
    query['charset'] = [charset]
    return urlunparse(parts._replace(query=urlencode(query, doseq=True)))
