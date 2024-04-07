from logging.config import dictConfig
from typing import Callable
from functools import wraps
import logging
import yaml
import time


class Sawyer:
    def __init__(self, config_yaml:str = None):
        if config_yaml:
            dictConfig(yaml.safe_load(open(config_yaml, 'r'))['sawyer'])

    def track(self, name:str, on_entry:Callable = None, on_exit:Callable = None, on_error:Callable = None, **kwargs):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger = logging.getLogger(name)
                start = time.time()
                if on_entry:
                    on_entry(logger, func.__name__, start=start, *args, **kwargs)
                try:
                    result = func(*args, **kwargs)
                    if on_exit:
                        on_exit(logger, func.__name__, start=start, end=time.time(), *args, **kwargs)
                    return result
                except Exception as e:
                    if on_error:
                        on_error(logger, func.__name__, start=start, end=time.time(), error=e, *args, **kwargs)
                    raise e
            return wrapper
        return decorator
    
    def __call__(self, name:str):
        return logging.getLogger(name)
