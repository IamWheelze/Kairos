from abc import ABC, abstractmethod
from typing import AsyncIterable


class STTResult:
    def __init__(self, text: str, is_final: bool, stability: float | None = None):
        self.text = text
        self.is_final = is_final
        self.stability = stability


class STTClient(ABC):
    @abstractmethod
    async def stream_recognize(self, pcm_iter: AsyncIterable[bytes]) -> AsyncIterable[STTResult]:
        """Consume PCM chunks and yield interim/final results."""
        raise NotImplementedError

