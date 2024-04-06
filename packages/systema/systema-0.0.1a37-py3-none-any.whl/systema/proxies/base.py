from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Generator, Generic, TypeVar

import httpx
from sqlmodel import create_engine

from systema.management import InstanceType, Settings

T = TypeVar("T")


class Proxy(ABC, Generic[T]):
    @cached_property
    def engine(self):
        return create_engine(Settings().db_address)

    @cached_property
    def client(self):
        if token := Settings().token:
            return httpx.Client(
                headers={"Authorization": f"Bearer {token}"}, follow_redirects=True
            )
        raise ValueError("No token")

    @property
    def base_url(self) -> str:
        return str(Settings().server_base_url)

    def is_set_as_server(self):
        return Settings().instance_type == InstanceType.SERVER

    @abstractmethod
    def get(self, id: str) -> T:
        pass

    @abstractmethod
    def all(self) -> Generator[T, None, None]:
        pass

    @abstractmethod
    def create(self, data: Any) -> T:
        pass

    @abstractmethod
    def update(self, id: str, data: Any) -> T:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass
