from abc import ABC, abstractmethod
from typing import Optional


class MusicIDResult:
    def __init__(self, title: Optional[str], artist: Optional[str], confidence: float):
        self.title = title
        self.artist = artist
        self.confidence = confidence


class MusicIDClient(ABC):
    @abstractmethod
    async def identify(self, pcm_bytes: bytes) -> MusicIDResult:
        raise NotImplementedError

