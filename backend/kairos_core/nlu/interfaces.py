from abc import ABC, abstractmethod
from typing import Optional


class NLUResult:
    def __init__(self, intent: str, params: dict | None = None, confidence: float | None = None):
        self.intent = intent
        self.params = params or {}
        self.confidence = confidence


class NLUClient(ABC):
    @abstractmethod
    async def detect_intent(self, text: str, context: Optional[dict] = None) -> NLUResult:
        raise NotImplementedError

