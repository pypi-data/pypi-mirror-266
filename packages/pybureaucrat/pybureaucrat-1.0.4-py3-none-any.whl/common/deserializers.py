from typing import TypeVar
import json

T = TypeVar("T")

def default_deserializer(data:str) -> T:
    return json.loads(data)["result"]

def raw_deserializer(data) -> T:
    return data