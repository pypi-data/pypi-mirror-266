# RedSauce

RedSauce integrates with FastAPI, leveraging Redis to provide caching functionality with minimal overhead.
The foundation of the project was to reduce code overhead for caching endpoints and logging. 
Using this structure you can expect to enable caching with a simple decorator.

**Note: FastAPI is NOT a dependency of this repo**

## TL;DR
```Python
from fastapi import FastAPI
from models import DemoModel
app = FastAPI()

from redsauce import Generator

db = Generator(connection = {
    'host':'localhost',
    'port':'6379',
    'decode_responses':False
})
cache = db()
# Caching is now available

@app.get("demo/rawtypes")
@cache.cache()
def my_endpoint(test:str):
    # Do stuff
    return test

@app.post("/demo/json")
@cache.cache(ttl=180, json=True)
def post_endpoint(model: DataModel):
    return model.model_dump()

```

## Generator
```Python
__init__(
    yaml_path:str = None # Path to the YAML configuration file
    connection: dict = None # Connection specification to the Redis instance (optional if specified in YAML, will override YAML)
)
```

The Generator class enables users to dynamically initialize databases. Recieving parameters from either the configuration yaml file, or explicitly in the constructor. It returns the `GlobalServices` class which hosts functions like `search` and `cache`. 
### Cache Events
Specify callbacks for cache hits and misses on the Generator class. These will be the defaults for all of the GlobalServices classes that are generated.
```Python
from redsauce import Generator
import my_callbacks

db = Generator('config.yaml')

db.on_cache_hit = my_callbacks.on_cache_hit
db.on_cache_miss = my_callbacks.on_cache_miss
```
## GlobalServices
`GlobalSevices` hosts the functions of each instance. Caching and Searching are its primary utilities. Later this will also spawn a Message Queue through `rq`.
```Python
__init__(
    connection:dict, # Database connection speicification (db is 0 by default)
    index:redis.IndexDefinition = None, # Optional - Required for searching
    schema:List[<redis fields>] = None, # Optional - Required for searching
    event_handlers:dict = None # Optional - Dictionary of callbacks (on_cache_hit/miss)
)
```

### Caching
By default the caching utility will use the MD5 checksum of the underlying function's KWARGS to generate an index key from the `endpoint` parameter and the checksum: example `demo:aaaBBBccc`.
```Python
cache = GlobalServices(**kwargs)

@fast.method("/endpoint", **api_wargs)
@cache.cache(
        endpoint:string = 'cache', # the index key's prefix
        ttl:int = None, # Expiration of stored record in seconds
        json:bool = False, # Whether or not to expect dict output from wrapped function
        logger = rootLogger # Specify the logger to be used by internal logging calls and callbacks
    )
def underlying_function(mayparm: Any = None): # Works with pydantic models too
    return "Bleh"
```


### Searching
A fun idea; this function turns the endpoint into a search function. The underlying function should specify the `Query` redis should use for searching its database. The one documented here uses `@index` specification for searching JSON documents.

```Python
cache = GlobalServices(**kwargs)

@fast.method("/endpoint", **api_wargs)
@cache.search()
def return_query(param1:int, param2: str): # Works with pydantic models too
    p = {"parm1":parm1, "parm2":parm2}
    c = lambda x: f"[{x} {x}]" if isinstance(x, int) else f"{x}"
    q = ' '.join(
                map(
                    lambda x: f'@{x[0]}:{c(x[1])}', 
                    filter(
                        lambda x: x[1] is not None, 
                        p.items()
                        )
                    )
                )
    q = '*' if not q else q
    print(f'Query: {q}')
    return q
```

## YAML Configuration

```YAML filename="saucy.yaml"
redis:
  connection:
    host: localhost
    port: 6379
    # Anything specified by [https://redis-py.readthedocs.io/en/stable/connections.html]
  db0: # Optional - required for search
    schema:
      - name: identifier
        path: $.doc.term
        type: text # also supports: number, tag (More to come!)
      # more schema fields ...
    index:
      prefix:
        - "name:"
        - "another:"
      type: JSON # Also supports: HASH
  # db[1-15] ??? Untested beyond this point
  # DO NOT SPECIFY SCHEMA OR INDEX BEYOND THIS POINT
```
