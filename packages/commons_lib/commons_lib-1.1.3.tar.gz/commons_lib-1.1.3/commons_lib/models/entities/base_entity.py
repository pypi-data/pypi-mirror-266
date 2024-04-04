import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, BIGINT, DateTime, BOOLEAN, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseEntity(Base):
    __abstract__ = True

    pk_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, nullable=True)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=True, default=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)




    @staticmethod
    def get_id_field_name()->str:
        return "pk_uuid"
