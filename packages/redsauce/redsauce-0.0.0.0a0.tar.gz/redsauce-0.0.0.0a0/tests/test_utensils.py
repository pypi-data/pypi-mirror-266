import unittest
from unittest.mock import patch, MagicMock
import json

from pydantic import BaseModel
from redis.commands.search.result import Result
from redis.commands.search.document import Document
import redis

import redsauce.utensils as utensils

class TestModel(BaseModel):
    a: int
    b: int
    c: int

class MockDocument(Document):
    def __init__(self, id, dict_):
        super().__init__(id, None, **{'json':json.dumps(dict_)})

class MockResult(Result):
    def __init__(self, docs):
        self.total = len(docs)
        self.docs = docs


class Test_BaseModelDump(unittest.TestCase):
    def setUp(self):
        self.data = TestModel(a=1, b=2, c=3)
    def test_baseModelDump(self):
        self.assertEqual(utensils.baseModelDump(self.data), {'a': 1, 'b': 2, 'c': 3})

class Test_MakeSerializable(unittest.TestCase):
    def setUp(self):
        self.data_dict = {'data':{'deep': TestModel(a=1, b=2, c=3)}}
        self.data_list = [TestModel(a=1, b=2, c=3), {'wee': 'woo'}, 'AHHHH']
        self.data_model = TestModel(a=1, b=2, c=3)
    def test_makeSerializable_dict(self):
        self.assertEqual(
            utensils.makeSerializable(self.data_dict), 
            {'data': {'deep': {'a': 1, 'b': 2, 'c': 3}}}
        )
    def test_makeSerializable_list(self):
        self.assertEqual(
            utensils.makeSerializable(self.data_list), 
            [{'a': 1, 'b': 2, 'c': 3}, {'wee': 'woo'}, 'AHHHH']
        )
    def test_makeSerializable_model(self):
        self.assertEqual(
            utensils.makeSerializable(self.data_model), 
            {'a': 1, 'b': 2, 'c': 3}
        )

class Test_RedisJsonResponse(unittest.TestCase):
    def setUp(self):
        self.data_many = MockResult([
            MockDocument('1', {'a': 1, 'b': 2, 'c': 3}),
            MockDocument('2', {'a': 7, 'b': 8, 'c': 9}),
            MockDocument('3', {'a': 4, 'b': 5, 'c': 6})
        ])
        self.data_one = MockResult([MockDocument('1', {'a': 1, 'b': 2, 'c': 3})])
    def test_RedisJsonResponse_many(self):
        self.assertListEqual(
            utensils.RedisJsonResponse(self.data_many.docs), 
            [{'a': 1, 'b': 2, 'c': 3}, 
            {'a': 7, 'b': 8, 'c': 9},
            {'a': 4, 'b': 5, 'c': 6}]
        )
    def test_RedisJsonResponse_one(self):
        self.assertListEqual(
            utensils.RedisJsonResponse(self.data_one.docs), 
            [{'a': 1, 'b': 2, 'c': 3}]
        )
    
class Test_QueryRecord(unittest.TestCase):
    def setUp(self):
        self.cur = MagicMock()
        self.query = '@a:1'
        self.query_fail = '@b:1'
        self.cur.ft().search.return_value = MockResult([MockDocument('1', {'a': 1, 'b': 2, 'c': 3})])
    def test_queryRecord_json(self):
        self.assertEqual(
            utensils.queryRecord(self.query, self.cur, json=True), 
            [{'a': 1, 'b': 2, 'c': 3}]
        )
    def test_queryRecord_no_json(self):
        self.assertEqual(
            utensils.queryRecord(self.query, self.cur, json=False).__repr__(), 
            ([MockDocument('1', {'a': 1, 'b': 2, 'c': 3})]).__repr__()
        )

class Test_GetRecord(unittest.TestCase):
    def setUp(self):
        self.cur = MagicMock()
        self.id_ = '1'
        self.cur.get.return_value = MockDocument('1', {'a': 1, 'b': 2, 'c': 3})

    def test_getRecord_json(self):
        self.assertEqual(
            utensils.getRecord(self.id_, self.cur, json=True), 
            {'a': 1, 'b': 2, 'c': 3}
        )
    def test_getRecord_no_json(self):
        self.assertEqual(
            utensils.getRecord(self.id_, self.cur, json=False).__repr__(), 
            (MockDocument('1', {'a': 1, 'b': 2, 'c': 3})).__repr__()
        )



if __name__ == '__main__':
    unittest.main()