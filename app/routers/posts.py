from fastapi import APIRouter, HTTPException
from fastapi import Depends
from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel
from app.database.models import Post, User, Tag
from app.auth import get_current_user

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
        tags=[PostTag(name=tag.name, id=tag.id) for tag in tags]
    )

@router.get("/", response_model=List[BasePost])
async def read_posts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_session)):
    posts_query = await db.execute(select(Post).options(selectinload(Post.tags)).offset(skip).limit(limit))
    posts = posts_query.scalars().all()
    return posts

@router.get("/{post_id}", response_model=BasePost)
async def read_post(post_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Post).options(selectinload(Post.tags)).filter(Post.id == post_id))
    post = result.scalars().first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int, post: PostUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Post).options(selectinload(Post.tags))
                              .filter(Post.id == post_id, Post.user_id == current_user.id)
    )
    db_post = result.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    tags_query = await db.execute(select(Tag).filter(Tag.id.in_(post.tags)))
    tags = tags_query.scalars().all()
    db_post.title = post.title or db_post.title
    db_post.content = post.content or db_post.content
    db_post.tags = tags or db_post.tags
    await db.commit()
    await db.refresh(db_post)
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        tags=[PostTag(name=tag.name, id=tag.id) for tag in tags]
    )

@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    post_query = await db.execute(select(Post).filter(Post.id == post_id, Post.user_id == current_user.id))
    db_post = post_query.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(db_post)
    await db.commit()
    return