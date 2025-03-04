from fastapi import APIRouter, HTTPException
from fastapi import Depends
from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from typing import List
from pydantic import BaseModel
from app.database.models import Post, User, Tag
from app.auth import get_current_user

class PostTag(BaseModel):
    name: str

class BasePost(BaseModel):
    title: str
    content: str
    tags: List[PostTag]

class PostResponse(BasePost):
    id: int
    tags: List[PostTag]


class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[int]

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.post("/", response_model=None)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    tags = (await db.execute(select(Tag).filter(Tag.id.in_(post.tags)))).scalars().all()
    db_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
        tags=tags
    )

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        tags=[PostTag(name=tag.name) for tag in tags]
    )

@router.get("/", response_model=List[BasePost])
async def read_posts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_session)):
    posts = (await db.execute(select(Post).offset(skip).limit(limit))).scalars().all()
    return posts

@router.get("/{post_id}", response_model=BasePost)
async def read_post(post_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalars().first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return BasePost(
        title=post.title,
        content=post.content,
        tags=[PostTag(name=tag.name) for tag in post.tags]
    )

@router.put("/{post_id}", response_model=BasePost)
async def update_post(post_id: int, post: PostCreate, db: AsyncSession = Depends(get_session)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post.model_dump().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}", response_model=BasePost)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_session)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return db_post