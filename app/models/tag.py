from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.database import Base
from app.mixins import SoftDeleteMixin, TimestampMixin
from .post_tag import post_tag_table


class Tag(TimestampMixin, SoftDeleteMixin, Base, AsyncAttrs):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    posts = relationship("Post", secondary=post_tag_table,
                         back_populates="tags")
