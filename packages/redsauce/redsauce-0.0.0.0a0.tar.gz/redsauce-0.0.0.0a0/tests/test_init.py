import unittest
from unittest.mock import patch, mock_open, MagicMock
import hashlib
import json as js

class MockRedis:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        pass
    def ft(self):
        return self
    def dropindex(self):
        pass
    def create_index(self, schema, definition):
        pass
    def search(self, query):
        return MockResult(query)
    def exists(self, key):
        return True
    def get(self, key):
        return self.__dict__[key]
    def set(self, key, value):
        self.__dict__[key] = value
    def json(self):
        return self
    def expire(self, key, ttl):
        pass
class MockResult:
    def __init__(self, query):
        self.query = query
    @property
    def docs(self):
        return []

class Test_GlobalServices(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
        self.index = {'prefix': ['test'], 'type': 'JSON'}
        self.schema = [{'type': 'text', 'path': '$.a', 'name': 'a'}]
    def on_cache_hit(self, *args, **kwargs):
        return (args, kwargs)
    def on_cache_miss(self, *args, **kwargs):
        return (args, kwargs)
    
    def test_init_noHandlers(self):
        from redsauce import GlobalServices
        # mock initialization of redsauce.pickles.Redis class
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())):
            g = GlobalServices(self.connection, self.index, self.schema)
            self.assertIsInstance(g, GlobalServices)

    def test_init_noHandlers_noIndex(self):
        from redsauce import GlobalServices
        # mock initialization of redsauce.pickles.Redis class
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())):
            g = GlobalServices(self.connection, None, self.schema)
            self.assertIsInstance(g, GlobalServices)

    def test_init_noHandlers_noSchema(self):
        from redsauce import GlobalServices
        # mock initialization of redsauce.pickles.Redis class
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())):
            g = GlobalServices(self.connection, self.index, None)
            self.assertIsInstance(g, GlobalServices)
    
    def test_init_withHandlers(self):
        from redsauce import GlobalServices
        # mock initialization of redsauce.pickles.Redis class
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())):
            g = GlobalServices(self.connection, self.index, self.schema, event_handlers={
                'on_cache_hit': self.on_cache_hit,
                'on_cache_miss': self.on_cache_miss
            })
            self.assertIsInstance(g, GlobalServices)
    

class Test_Generator_Manual(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    
    def test_manualInit_noRedisKey(self):
        from redsauce import Generator
        self.assertRaises(ValueError, Generator)

    def test_manualInit_noConnection(self):
        from redsauce import Generator
        with patch('builtins.open', mock_open(read_data='')) as m:
            self.assertRaises(ValueError, Generator, yaml_path=self.yaml_path)

    def test_manualInit(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        self.assertIsInstance(g, Generator)


class Test_Generator_IndexFormatter(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_formatIndex_Hash(self):
        from redsauce import Generator, IndexDefinition
        g = Generator(connection=self.connection)
        pre = ['test']
        index = {'prefix': pre, 'type': 'HASH'}
        id = g.formatIndex(index)
        self.assertIsInstance(id, IndexDefinition)
        self.assertListEqual(
            id.args,
            ['ON','HASH','PREFIX',len(pre),*(pre),'SCORE', 1.0]
        )

    def test_formatIndex_Json(self):
        from redsauce import Generator, IndexDefinition
        g = Generator(connection=self.connection)
        pre = ['test']
        index = {'prefix': pre, 'type': 'JSON'}
        id = g.formatIndex(index)
        self.assertIsInstance(id, IndexDefinition)
        self.assertListEqual(
            id.args,
            ['ON','JSON','PREFIX',len(pre),*(pre),'SCORE', 1.0]
        )

class Test_Generator_SchemaFormatter(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_formatSchema_knownTypes(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        schema = [
            {'type': 'text', 'path': '.', 'name': 'alower'},
            {'type':'TEXT', 'path': '.', 'name': 'aUpper'},
            {'type':'Text', 'path': '.', 'name': 'aMixed'},
            {'type':'NUMBER', 'path': '.', 'name': 'bUpper'},
            {'type':'number', 'path': '.', 'name': 'bLower'},
            {'type':'Number', 'path': '.', 'name': 'bMixed'},
            {'type':'TAG', 'path': '.', 'name': 'cUpper'},
            {'type':'tag', 'path': '.', 'name': 'cLower'},
            {'type':'Tag', 'path': '.', 'name': 'cMixed'}
        ]
        fields = g.formatSchema(schema)
        self.assertIsInstance(fields, list)
        self.assertEqual(len(fields), 9)
    
    def test_formatSchema_unknownTypes(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        schema = [
            {'type': 'text', 'path': '.', 'name': 'alower'},
            {'type':'TEXT', 'path': '.', 'name': 'aUpper'},
            {'type':'Text', 'path': '.', 'name': 'aMixed'},
            {'type':'NUMBER', 'path': '.', 'name': 'bUpper'},
            {'type':'number', 'path': '.', 'name': 'bLower'},
            {'type':'Number', 'path': '.', 'name': 'bMixed'},
            {'type':'TAG', 'path': '.', 'name': 'cUpper'},
            {'type':'tag', 'path': '.', 'name': 'cLower'},
            {'type':'Tag', 'path': '.', 'name': 'cMixed'},
            {'type':'unknown', 'path': '.', 'name': 'd'}
        ]
        self.assertRaises(KeyError, g.formatSchema, schema)

class Test_Generator_Load(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_load_noDbs(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {'connection': self.connection}})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            self.assertIsInstance(Generator(yaml_path=self.yaml_path), Generator)
    def test_load_withDbs_noSchema(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {'connection': self.connection, 'db0': {'index': {'prefix': ['test'], 'type': 'HASH'}}}})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path)
            self.assertIsInstance(g, Generator)
            self.assertEqual(len(g.dbs), 1)
            self.assertEqual(g.dbs[0]['index'].args, ['ON','HASH','PREFIX',1,'test','SCORE',1.0])
            self.assertEqual(g.dbs[0]['schema'], [])
    def test_load_withDbs_withSchema(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {'connection': self.connection, 'db0': {'index': {'prefix': ['test'], 'type': 'HASH'}, 'schema': [{'type': 'text', 'path': '$.a', 'name': 'a'}]}}})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path)
            self.assertIsInstance(g, Generator)
            self.assertEqual(len(g.dbs), 1)
            self.assertEqual(g.dbs[0]['index'].args, ['ON','HASH','PREFIX',1,'test','SCORE',1.0])
            self.assertEqual(len(g.dbs[0]['schema']), 1)
            self.assertIsInstance(g.dbs[0]['schema'][0], g.field_map['text'])

class Test_Generator_CacheHandlers(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_cacheHitHandler_callable(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        g.on_cache_hit = lambda x: x
        self.assertEqual(g.on_cache_hit(1), 1)
    
    def test_cacheHitHandler_staticType(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        def do():
            g.on_cache_hit = 1
        self.assertRaises(TypeError, do)
    
    def test_cacheMissHandler_callable(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        g.on_cache_miss = lambda x: x
        self.assertEqual(g.on_cache_miss(1), 1)

    def test_cacheMissHandler_staticType(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        def do():
            g.on_cache_miss = 1
        self.assertRaises(TypeError, do)
    
class Test_Generator_YAMLInit(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_initYamlPath_noRedisKey(self):
        from redsauce import Generator
        with patch('builtins.open', mock_open(read_data='')) as m:
            self.assertRaises(ValueError, Generator, yaml_path=self.yaml_path)
    
    def test_initYamlPath_noYamlPath(self):
        from redsauce import Generator
        self.assertRaises(ValueError, Generator)
    
    def test_initYamlPath_noConnectionInYaml(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {}})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            self.assertRaises(KeyError, Generator, yaml_path=self.yaml_path)
    
    def test_initYamlPath_withConnection(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {'connection': self.connection}})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path)
            self.assertIsInstance(g, Generator)

    def test_initYamlPath(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {'connection': self.connection}})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path)
            self.assertIsInstance(g, Generator)
            self.assertDictEqual(g.connection, self.connection)
    
    def test_initYamlPath_connectionOverride(self):
        from redsauce import Generator
        import yaml as ym
        data = ym.dump({'redis': {'connection': {
            'host': 'localhoster', 'port': 6379, 'db': 1
        }}})
        ## self.connection is localhost:6379
        # Connection should override the yaml connection if it is provided
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path, connection=self.connection)
            self.assertIsInstance(g, Generator)
            self.assertDictEqual(g.connection, self.connection)

class Test_Generator_Extras(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_nullHandler(self):
        from redsauce import Generator
        g = Generator(connection=self.connection)
        self.assertIsNone(g._Generator__null_handler())

class Test_Generator_Call(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
        self.big_yaml = lambda x: {
            'redis': {
                'connection': self.connection,
                f'db{x}': {
                    'index': {'prefix': ['test'], 'type': 'HASH'},
                    'schema': [
                        {'type': 'text', 'path': '$.a', 'name': 'a'}
                    ]
                }
            }
        }

    def test_call_defaultDb(self):
        from redsauce import Generator, GlobalServices
        g = Generator(connection=self.connection)
        self.assertIsInstance(g(), GlobalServices)
    
    def test_call_nonDefaultDb(self):
        from redsauce import Generator, GlobalServices
        g = Generator(connection=self.connection)
        self.assertIsInstance(g(1), GlobalServices)
    
    def test_call_defaultDb_withIndex(self):
        from redsauce import Generator, GlobalServices
        import redis.exceptions
        import yaml as ym
        data = ym.dump(self.big_yaml(0))
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path)
            def do():
                try:
                    g()
                except redis.exceptions.ConnectionError as e:
                    return True
                return True
            self.assertTrue(do())
    
    def test_call_nonDefaultDb_withIndex(self):
        from redsauce import Generator, GlobalServices
        import yaml as ym
        data = ym.dump(self.big_yaml(1))
        with patch('builtins.open', mock_open(read_data=data)) as m:
            g = Generator(yaml_path=self.yaml_path)
            self.assertIsInstance(g(1), GlobalServices)

class Test_GlobalServices_SearchDecorator(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
    def test_searchDecorator(self):
        from redsauce import Generator
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())):
            g = Generator(connection=self.connection)
            c = g()
            @c.search()
            def someFunc():
                return 'hello'
            self.assertEqual(someFunc(), [])

class Test_GlobalServices_CacheDecorator(unittest.TestCase):
    def setUp(self):
        self.yaml_path = 'yaml/some.yaml'
        self.connection = {'host': 'localhost', 'port': 6379}
        self.hit_buffer = None
        self.miss_buffer = None
    def on_cache_hit(self, *args, **kwargs):
        self.hit_buffer = (args, kwargs)

    def on_cache_miss(self, *args, **kwargs):
        self.miss_buffer = (args, kwargs)

    def test_cacheDecorator_hit_noArgs(self):
        self.hit_buffer, self.miss_buffer = None, None
        from redsauce import Generator
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())),\
            patch('redsauce.pickles.Redis.exists', MagicMock(return_value=True)),\
            patch('redsauce.pickles.Redis.get', MagicMock(return_value='hello')),\
            patch('redsauce.pickles.Redis.set', MagicMock()):
            g = Generator(connection=self.connection)
            g.on_cache_hit = self.on_cache_hit
            g.on_cache_miss = self.on_cache_miss
            c = g()
            @c.cache()
            def someFunc():
                return 'hello'
            self.assertEqual(someFunc(), 'hello')
            self.assertIsNotNone(self.hit_buffer)
            self.assertIsNone(self.miss_buffer)

    def test_cacheDecorator_miss_noArgs(self):
        self.hit_buffer, self.miss_buffer = None, None
        from redsauce import Generator
        with patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis())),\
            patch('redsauce.pickles.Redis.exists', MagicMock(return_value=False)),\
            patch('redsauce.pickles.Redis.get', MagicMock(return_value='hello')),\
            patch('redsauce.pickles.Redis.set', MagicMock()):
            g = Generator(connection=self.connection)
            g.on_cache_hit = self.on_cache_hit
            g.on_cache_miss = self.on_cache_miss
            c = g()
            @c.cache()
            def someFunc():
                return 'hello'
            self.assertEqual(someFunc(), 'hello')
            self.assertIsNone(self.hit_buffer)
            self.assertIsNotNone(self.miss_buffer)
    def test_cacheDecorator_hit_withArgs(self):
        self.hit_buffer, self.miss_buffer = None, None
        self.value = {"a": 1, "b": 2}
        self.key = f'cache:{hashlib.md5(js.dumps(self.value).encode()).hexdigest()}'
        from redsauce import Generator
        with patch('redsauce.pickles.Redis.__init__', MagicMock(return_value=None)),\
        patch('redsauce.pickles.Redis.ft', MagicMock(return_value=MockRedis(**{self.key:self.value}))),\
        patch('redsauce.pickles.Redis.json', MagicMock(return_value=MockRedis(**{self.key:self.value}))),\
        patch('redsauce.pickles.Redis.exists', MagicMock(return_value=True)):
            g = Generator(connection=self.connection)
            g.on_cache_hit = self.on_cache_hit
            g.on_cache_miss = self.on_cache_miss
            c = g()
            @c.cache(ttl=10, json=True)
            def someFunc(a, b):
                return {"a": a, "b": b}
            self.assertEqual(someFunc(a=1, b=2), self.value)
            self.assertIsNotNone(self.hit_buffer)
            self.assertIsNone(self.miss_buffer)

if __name__ == '__main__':
    unittest.main()