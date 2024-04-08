from functools import wraps
from inspect import iscoroutinefunction as iscoroutine

import hashlib
import json as js
import yaml as ym
import logging

from typing import Any, Callable

from redis.commands.json.path import Path
from redis.commands.search.field import TagField, TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.exceptions import DataError

from .pickles import Redis
from .utensils import queryRecord, getRecord, makeSerializable
from .utility.logging import Sawyer


class Generator:
    field_map = {
        'tag': TagField,
        'text': TextField,
        'number': NumericField
        # more to come
    }

    def __init__(self, yaml_path: str = None, connection = None):
        self.__on_cache_hit = self.__null_handler
        self.__on_cache_miss = self.__null_handler
        self.yaml = None
        if not yaml_path and not connection:
            raise ValueError("Must provide either a path to a yaml file or a connection object.")
        if yaml_path:
            self.yaml = ym.safe_load(open(yaml_path))
        if connection:
            if self.yaml:
                self.yaml['redis']['connection'] = connection
            else:
                self.yaml = {'redis': {'connection': connection}}
        if not self.yaml or 'redis' not in self.yaml:
            raise ValueError("YAML file must contain a 'redis' key.")
        self.dbs = {}
        self.connection = self.yaml['redis'].pop('connection')
        self.load()
    
    def __null_handler(self, *args, **kwargs):
        pass

    def formatIndex(self, index: dict) -> IndexDefinition:
        id = IndexDefinition(prefix=index['prefix'], index_type=getattr(IndexType, index['type']))
        return id
    def formatSchema(self, schema: dict) -> dict:
        fields = list(map(lambda x: self.field_map[x['type'].lower()](x['path'], as_name=x['name']), schema))
        return fields
        
    def load(self):
        dbs = dict(filter(lambda x: 'db' in x[0], self.yaml['redis'].items()))
        for db, spec in dbs.items():
            self.dbs[int(db.strip('db'))] = {
                'index': self.formatIndex(spec['index']),
                'schema': self.formatSchema(spec.get('schema', []))
            }
    
    def __call__(self, db: int = 0):
        conn = {**self.connection, 'db': db}
        event_handlers = {
            'on_cache_hit': self.on_cache_hit,
            'on_cache_miss': self.on_cache_miss
        }
        if db in self.dbs:
            si = self.dbs[db] if db == 0 else {} # Set error log to indicate that db 0 is reserved for the default database and for indexes
            return GlobalServices(conn, event_handlers=event_handlers, **si)
        return GlobalServices(conn, event_handlers=event_handlers)
    
    @property
    def on_cache_hit(self):
        return self.__on_cache_hit
    
    @on_cache_hit.setter
    def on_cache_hit(self, handler: Callable):
        if not callable(handler):
            raise TypeError("Handler \"on_cache_hit\" must be a callable object.")
        self.__on_cache_hit = handler
    
    @property
    def on_cache_miss(self):
        return self.__on_cache_miss
    
    @on_cache_miss.setter
    def on_cache_miss(self, handler: Callable):
        if not callable(handler):
            raise TypeError("Handler \"on_cache_miss\" must be a callable object.")
        self.__on_cache_miss = handler


class GlobalServices:
    def __init__(self, connection, index=None, schema=None, event_handlers=None):
        self.default_event_handlers = {
            'on_cache_hit': self.__null_handler,
            'on_cache_miss': self.__null_handler
        }
        self.event_handlers = event_handlers if event_handlers else self.default_event_handlers
        self.connection = connection
        self.redis = Redis(**connection)
        if schema is not None and index is not None:
            try:
                self.redis.ft().dropindex()
            except:
                pass
            self.redis.ft().create_index(schema, definition=index)
    
    def __null_handler(self, *args, **kwargs):
        pass
    
    def search(self) -> Any:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # TODO: Handle Coroutines
                query = func(*args, **kwargs)
                return queryRecord(query, self.redis)
            return wrapper
        return decorator
    
    def cache(self, endpoint = "cache", ttl=None, json=False, logger=logging.getLogger(__name__)) -> Any:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                red = self.redis if not json else self.redis.json()
                kw = makeSerializable(kwargs)
                key = f"{endpoint}:{hashlib.md5(js.dumps(kw).encode()).hexdigest()}"
                if self.redis.exists(key):
                    self.event_handlers['on_cache_hit'](logger=logger, source=func.__name__, key=key, *args, **kwargs)
                    return getRecord(key, red)
                self.event_handlers['on_cache_miss'](logger=logger, source=func.__name__, key=key, *args, **kwargs)
                # TODO: Handle Coroutines
                result = func(*args, **kwargs)
                if not json:
                    try:
                        red.set(key, result)
                    except:
                        raise DataError("A tuple item must be str, int, float or bytes.")
                else:
                    red.set(key, Path.root_path(), result)
                if ttl:
                    self.redis.expire(key, ttl)
                return result
            return wrapper
        return decorator

__all__ = [
    'Generator', 
    'GlobalServices',
    'Sawyer'
    ]