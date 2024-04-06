from typing import TypeVar
from .base import BaseHttpService, ServiceError
from .deserializers import raw_deserializer, default_deserializer\

T = TypeVar("T")

class QueueService(BaseHttpService):
    def __init__(self, baseUrl: str) -> None:
        super().__init__(baseUrl)

    def queues(self) -> list[str]:
        return self.get("queues/")
    
    def dequeue(self, queue_name) -> str|None:
        data:str = self.get(f"queues/{queue_name}", caster=raw_deserializer)
        return data if len(data) > 0 else None
    
    def enqueue(self, queue_name, data:T):
        return self.post(f"queues/{queue_name}", data, is_raw=True)
    
    def delete_queue(self, queue_name) -> bool:
        try:
            self.delete(f"queues/{queue_name}")
        except ServiceError as e:
            return False