from functools import wraps
from inspect import iscoroutinefunction as iscoroutine

import hashlib
import json as js
import yaml as ym

from typing import Any, Union

from redis.commands.json.path import Path
from redis.commands.search.field import TagField, TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from .pickles import Redis
from .utensils import queryRecord, getRecord

class Generator:
    field_map = {
        'tag': TagField,
        'text': TextField,
        'number': NumericField
        # more to come
    }
    def __init__(self, yaml_path: str = None, connection = None):
        if yaml_path is None and connection is None:
            raise ValueError("Must provide either a path to a yaml file or a connection object.")
        if yaml_path is not None:
            self.yaml = ym.safe_load(open(yaml_path))
        elif connection is not None:
            self.yaml = {'redis': {'connection': connection}}
        self.dbs = {}
        self.connection = self.yaml['redis'].pop('connection')
        self.load()
    
    def formatIndex(self, index: dict) -> IndexDefinition:
        id = IndexDefinition(prefix=index['prefix'], index_type=getattr(IndexType, index['type']))
        return id
    def formatSchema(self, schema: dict) -> dict:
        fields = list(map(lambda x: self.field_map[x['type'].lower()](x['path'], as_name=x['name']), schema))
        for f in fields:
            print(dir(f))
            print(f.name, f.as_name, f)
        return fields
        
    def load(self):
        dbs = dict(filter(lambda x: 'db' in x[0], self.yaml['redis'].items()))
        for db, spec in dbs.items():
            self.dbs[int(db.strip('db'))] = {
                'index': self.formatIndex(spec['index']),
                'schema': self.formatSchema(spec['schema'])
            }
    
    def __call__(self, db: int):
        conn = {**self.connection, 'db': db}
        si = self.dbs[db] if db == 0 else {} # Set error log to indicate that db 0 is reserved for the default database and for indexes
        return GlobalServices(conn, **si)


class GlobalServices:
    def __init__(self, connection, index=None, schema=None):
        self.connection = connection
        self.redis = Redis(**connection)
        if schema is not None and index is not None:
            try:
                self.redis.ft().dropindex()
            except:
                pass
            self.redis.ft().create_index(schema, definition=index)
    
    def search(self) -> Any:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # TODO: Handle Coroutines
                query = func(*args, **kwargs)
                return queryRecord(query, self.redis)
            return wrapper
        return decorator
    
    def cache(self, endpoint = "cache", ttl=None, json=False) -> Any:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                red = self.redis if not json else self.redis.json()
                key = f"{endpoint}:{hashlib.md5(js.dumps(kwargs).encode()).hexdigest()}"
                if self.redis.exists(key):
                    return getRecord(key, red)
                # TODO: Handle Coroutines
                result = func(*args, **kwargs)
                red.set(key, Path.root_path(), result)
                if ttl is not None:
                    self.redis.expire(key, ttl)
            return wrapper
        return decorator

__all__ = ['Generator', 'GlobalServices']