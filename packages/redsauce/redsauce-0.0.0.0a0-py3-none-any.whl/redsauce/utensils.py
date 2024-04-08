import json as js
from typing import Any, Union
from redis.commands.search.query import Query
from pydantic import BaseModel

def RedisJsonResponse(data: Any) -> dict:
    if isinstance(data, list):
        print(data)
        elem = lambda x: x if not hasattr(x, 'json') and not isinstance(x,str) else js.loads(x.json)
        return list(map(lambda x: elem(x),data))
    try:
        return js.loads(data.json)
    except:
        return data # ! Check on this, may not be necessary
    
def queryRecord(query: str, cur, json=True ) -> Union[dict, list]:
    try:
        records = cur.ft().search(Query(query))
        print(records)
        if json:
            return RedisJsonResponse(records.docs)
        return records.docs
    except Exception as e:
        raise NonExistentIndex(f"Index does not exist, please ensure that the database has been properly configured.\nThere should be both a schema and an index for the database.")
    
def getRecord(id: str, cur, json=True) -> Union[dict, list]:
    response = cur.get(id)
    if json:
        return RedisJsonResponse(response)
    return response

def baseModelDump(data: BaseModel) -> dict:
        if hasattr(data, 'model_dump'):
            return getattr(data, 'model_dump')()
        elif hasattr(data, 'dict'):
            return getattr(data, 'dict')()
        else:
            return data

def makeSerializable(data: Any) -> str:
    if isinstance(data, BaseModel):
        return baseModelDump(data)
    if isinstance(data, dict):
        return {k: makeSerializable(v) for k, v in data.items()}
    if isinstance(data, list):
        return [makeSerializable(x) for x in data]
    return data

class NonExistentIndex(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)