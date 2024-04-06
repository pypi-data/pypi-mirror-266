from blobs import BlobsService
from tables import TablesService
from queues import QueueService

class BureaucratConnection:
    def __init__(self, url:str) -> None:
        self.url = url
        self.queues:QueueService = QueueService(url)
        self.blobs:BlobsService = BlobsService(url)
        self.tables:TablesService = TablesService(url)