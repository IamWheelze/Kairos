from pydantic import BaseModel


class Song(BaseModel):
    id: int
    title: str
    identifier: str


class SongCreate(BaseModel):n+    title: str
    identifier: str

