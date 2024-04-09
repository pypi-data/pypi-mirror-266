from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ContextProvider(ABC):

    @abstractmethod
    def set(self, key: str, value: Any):
        pass

    @abstractmethod
    def unset(self, key: str):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def context(self) -> dict[str, Any]:
        pass


class SimpleContextProvider(ContextProvider):

    def __init__(self, initial: dict[str, Any] | None = None):
        self.values: dict[str, Any] = initial or {}

    def set(self, key: str, value: Any):
        self.values[key] = value

    def unset(self, key: str):
        del self.values[key]

    def clear(self):
        self.values.clear()

    def context(self) -> dict[str, Any]:
        return self.values
