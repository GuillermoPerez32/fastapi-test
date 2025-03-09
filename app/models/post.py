from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.database import Base
from app.mixins import SoftDeleteMixin, TimestampMixin
from .post_tag import post_tag_table


class Post(TimestampMixin, SoftDeleteMixin, Base, AsyncAttrs):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tag_table,
                        back_populates="posts")
