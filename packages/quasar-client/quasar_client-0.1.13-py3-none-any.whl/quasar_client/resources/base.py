from abc import ABC, abstractmethod
from typing import Dict
from urllib.parse import urljoin

import httpx
import requests


# Abstract base class
class ResourceBase(ABC):
    """Base class for Quasar resources."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.prediction_endpoint = urljoin(self.base_url, "/predictions/")

    @abstractmethod
    def _post(self, data: Dict):
        pass


class SyncResource(ResourceBase):
    """Synchronous resource."""

    def _post(self, data: Dict):
        return requests.post(self.prediction_endpoint, json=data)


class AsyncResource(ResourceBase):
    """Asynchronous resource."""

    async def _post(self, data: Dict, timeout: float = 180.0, read_timeout: float = 10.0):
        timeout = httpx.Timeout(timeout=timeout, read=read_timeout)
        async with httpx.AsyncClient() as client:
            return await client.post(self.prediction_endpoint, json=data, timeout=timeout)
