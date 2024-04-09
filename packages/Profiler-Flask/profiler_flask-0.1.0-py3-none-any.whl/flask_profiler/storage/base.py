import typing as tp
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping


class BaseStorage(ABC):
    @abstractmethod
    def filter(self: tp.Self) -> Iterator[dict[str, tp.Any]]: ...

    @abstractmethod
    def get_summary(self: tp.Self) -> list[tp.Any]: ...

    @abstractmethod
    def insert(self: tp.Self, kwds: Mapping[str, tp.Any]) -> None: ...

    @abstractmethod
    def delete(self: tp.Self, measurementId: int) -> None: ...

    @abstractmethod
    def truncate(self: tp.Self) -> bool: ...
