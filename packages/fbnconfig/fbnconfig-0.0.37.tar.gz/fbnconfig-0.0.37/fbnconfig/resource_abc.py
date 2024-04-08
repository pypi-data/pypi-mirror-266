from types import SimpleNamespace
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List, Optional


class Ref(ABC):
    @abstractmethod
    def attach(self, client: httpx.Client) -> None:
        pass

    def deps(self):
        return []


class Resource(ABC):
    @abstractmethod
    def read(self, client: httpx.Client, old_state: SimpleNamespace) -> None:
        pass

    @abstractmethod
    def create(self, client) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(self, client, old_state) -> Union[None, Dict[str, Any]]:
        pass

    @staticmethod
    @abstractmethod
    def delete(client, old_state) -> None:
        pass

    @abstractmethod
    def deps(self) -> List[Any]:
        pass
