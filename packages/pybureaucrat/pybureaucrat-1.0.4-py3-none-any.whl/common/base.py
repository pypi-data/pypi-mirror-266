from typing import TypeVar, Callable
from enum import IntEnum
import requests

from .deserializers import default_deserializer

T = TypeVar("T")
TResult = TypeVar("TResult")

class ResultStatus(IntEnum):
    Unknown = 0
    Information = 1
    Success = 2
    Redirect = 3
    ClientError = 4
    ServerError = 5

def get_result_status(status_code:int) -> ResultStatus:
    match status_code:
        case x if x < 100:
            return ResultStatus.Unknown
        case x if x < 200:
            return ResultStatus.Information
        case x if x < 300:
            return ResultStatus.Success
        case x if x < 400:
            return ResultStatus.Redirect
        case x if x < 500:
            return ResultStatus.ClientError
        case _:
            return ResultStatus.ServerError

class ServiceError(Exception):
    def __init__(self, status:ResultStatus, *args: object) -> None:
        super().__init__(*args)
        self.status = status

class BaseHttpService:
    def __init__(self, baseUrl:str) -> None:
        self.baseUrl = baseUrl

    def get(self, url:str, headers:dict[str, str] = None, caster:Callable[[str,], T] = None, stream:bool = False) -> T:
        caster = caster or default_deserializer
        response = requests.get(f"{self.baseUrl}/{url}", headers=headers, stream=stream)
        status = get_result_status(response.status_code)
        if status == ResultStatus.Success:
            return caster(response.text)
        else:
            raise ServiceError(status, response.text)

    def post(self, url:str, parameter:T, 
             headers:dict[str, str] = None, caster:Callable[[str,], TResult] = None,
             is_raw:bool = False
             ) -> TResult:
        caster = caster or default_deserializer
        params = {
            "headers": headers,
            "data" if is_raw else "json":parameter
        }
        response = requests.post(f"{self.baseUrl}/{url}",  **params)
        status = get_result_status(response.status_code)
        if status == ResultStatus.Success:
            return caster(response.text)
        else:
            raise ServiceError(status, response.text)
        
    def delete(self, url:str, headers:dict[str, str] = None, caster:Callable[[str,], T] = None) -> T:
        caster = caster or default_deserializer
        print(f"{self.baseUrl}/{url}")
        response = requests.delete(f"{self.baseUrl}/{url}", headers=headers)
        status = get_result_status(response.status_code)
        if status == ResultStatus.Success:
            return caster(response.text)
        else:
            raise ServiceError(status, response.text)