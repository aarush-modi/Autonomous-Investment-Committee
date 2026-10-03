import sqlite3
import json
import time
import os
import inspect
import functools
from pydantic import TypeAdapter


class Cache:
    def __init__(self, db_path: str = "cache.db", default_ttl: int = 3600):
        self.db_path = db_path
        self.default_ttl = default_ttl
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS cache "
            "(key TEXT PRIMARY KEY, value TEXT, expires_at REAL)"
        )
        self.conn.commit()

    def get(self, key: str):
        row = self.conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()

        if row is None:
            return None

        value, expires_at = row
        if time.time() > expires_at:
            self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            self.conn.commit()
            return None

        return json.loads(value)

    def set(self, key: str, value, ttl: int = None):
        expires_at = time.time() + (ttl or self.default_ttl)
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), expires_at),
        )
        self.conn.commit()

    def clear(self):
        self.conn.execute("DELETE FROM cache")
        self.conn.commit()

#Singleton instance of cache, created on first use so importing this module has no side effects.
#Tests can point it elsewhere by assigning cache._cache = Cache(tmp_path / "cache.db")
_cache = None

def get_cache() -> Cache:
    global _cache
    if _cache is None:
        from config.settings import settings
        os.makedirs(os.path.dirname(settings.CACHE_DB_PATH) or ".", exist_ok=True)
        _cache = Cache(settings.CACHE_DB_PATH, settings.CACHE_TTL)
    return _cache

def cached(key_prefix: str, ttl: int, model_name):
    def decorator(func):
        sig = inspect.signature(func)
        adapter = TypeAdapter(model_name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            parts = [str(v) for k, v in bound.arguments.items() if k != "self"]
            key = "_".join([key_prefix] + parts)

            value = get_cache().get(key)
            if value is not None:
                return adapter.validate_python(value)

            result = func(*args, **kwargs)
            #Don't cache empty responses ([], {}, "") — they're often transient provider failures
            if result:
                get_cache().set(key, adapter.dump_python(result, mode="json"), ttl)
            return result
        return wrapper
    return decorator
    