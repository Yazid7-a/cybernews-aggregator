from __future__ import annotations
from abc import ABC, abstractmethod

class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str:
        raise NotImplementedError
