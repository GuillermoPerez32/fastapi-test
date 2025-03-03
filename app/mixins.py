from sqlalchemy import Boolean, Column, TIMESTAMP, func
from sqlalchemy.orm import declared_attr

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)

    @declared_attr
    def __mapper_args__(cls):
        return {"eager_defaults": True}
    
class TimestampMixin:
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def __mapper_args__(cls):
        return {"eager_defaults": True}