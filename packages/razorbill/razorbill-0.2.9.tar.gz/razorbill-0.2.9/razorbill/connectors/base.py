from abc import ABC, abstractmethod
from typing import Any, Type
from pydantic import BaseModel


class BaseConnector(ABC):
    @property
    @abstractmethod
    def schema(self) -> Type[BaseModel]:
        pass

    @property
    @abstractmethod
    def pk_name(self) -> str:
        pass

    @property
    @abstractmethod
    def type_pk(self) -> Type[str|int]:
        pass

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        pass

    @abstractmethod
    async def get_many(
        self, *,
        skip: int, 
        limit: int,
        populate: bool = False, 
        filters: dict[str, Any]|None = None,
        sorting: tuple[str, bool]|None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_one(self, obj_id: str | int, populate: bool | str = False) -> dict[str, Any]:
        pass

    @abstractmethod
    async def create_one(self, obj: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    async def update_one(self, obj_id: str | int, obj: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    async def delete_one(self, obj_id: str | int) -> dict[str, Any] | None:
        pass
