
from typing import List
from pydantic import BaseModel


class PostTag(BaseModel):
    id: int
    name: str


class BasePost(BaseModel):
    title: str
    content: str
    tags: List[PostTag] = []


class PostResponse(BasePost):
    id: int
    tags: List[PostTag]


class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[int]


class PostUpdate(BaseModel):
    title: str | None
    content: str | None
    tags: List[int] | None
