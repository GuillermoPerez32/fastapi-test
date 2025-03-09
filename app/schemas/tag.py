from pydantic import BaseModel


class BaseTag(BaseModel):
    name: str


class TagResponse(BaseTag):
    id: int
    name: str


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str | None


class TagPost(BaseModel):
    id: int
    title: str
    content: str
