import json as js
from typing import Any, Union
from redis.commands.search.query import Query

def RedisJsonResponse(data: Any) -> dict:
    if isinstance(data, list):
        return list(map(lambda x: js.loads(x.json),data))
    try:
        return js.loads(data.json)
    except:
        return data # ! Check on this, may not be necessary
    
def queryRecord(query: str, cur, json=True ) -> Union[dict, list]:
    try:
        print(f"Query: *{query}*")
        records = cur.ft().search(Query(query))
        print(records)
        if json:
            return RedisJsonResponse(records.docs)
        return records.docs
    except Exception as e:
        raise NonExistentIndex(f"Index does not exist: {e}")
    
def getRecord(id: str, cur, json=True) -> Union[dict, list]:
    response = cur.get(id)
    if json:
        return RedisJsonResponse(response)
    return response


class NonExistentIndex(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)