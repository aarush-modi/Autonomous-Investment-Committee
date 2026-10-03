import sqlite3
import json
import time
import inspect
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

#Sinbgleton instance of cache
_cache = Cache("cache.db")

def cached(key_prefix: str, ttl: int, model_name):
    def decorator(func):
        sig = inspect.signature(func)
        adapter = TypeAdapter(model_name)

        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            parts = [str(v) for k, v in bound.arguments.items() if k != "self"]
            key = "_".join([key_prefix] + parts)

            value = _cache.get(key)
            if value != None:
                return adapter.validate_python(value)
            
            result = func(*args, **kwargs)
            _cache.set(key, adapter.dump_python(result, mode="json"), ttl)
            return result
        return wrapper
    return decorator
    