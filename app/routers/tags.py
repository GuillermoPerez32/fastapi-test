from fastapi import APIRouter, HTTPException
from fastapi import Depends
from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload
from typing import List
from app.models import User, Tag
from app.auth import get_current_user
from app.schemas.tag import TagCreate, TagResponse, BaseTag, TagUpdate, TagPost


router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


@router.post("/", response_model=None)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user)
):
    db_tag = Tag(
        name=tag.name,
    )

    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return TagResponse(
        id=db_tag.id,
        name=db_tag.name,
    )


@router.get("/", response_model=List[BaseTag])
async def read_tags(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_session)):
    tags_query = await db.execute(select(Tag).offset(skip).limit(limit))
    tags = tags_query.scalars().all()
    return tags


@router.get("/{tag_id}", response_model=BaseTag)
async def read_tag(tag_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Tag).filter(Tag.id == tag_id))
    post = result.scalars().first()
    if post is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return post


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int, post: TagUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user)
):
    result = await db.execute(select(Tag).filter(Tag.id == tag_id))
    db_tag = result.scalars().first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    db_tag.name = post.name
    await db.commit()
    await db.refresh(db_tag)

    return TagResponse(
        id=db_tag.id,
        name=db_tag.name
    )


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user)
):
    tag_query = await db.execute(select(Tag).filter(Tag.id == tag_id))
    db_tag = tag_query.scalars().first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(db_tag)
    await db.commit()
    return


@router.get("/{tag_id}/posts", response_model=List[TagPost])
async def read_tag_post(tag_id, db: AsyncSession = Depends(get_session)):
    tag_query = await db.execute(select(Tag).options(selectinload(Tag.posts)).filter(Tag.id == tag_id))
    tag = tag_query.scalars().first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    return tag.posts
