import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, BIGINT, DateTime, BOOLEAN, BigInteger, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseRecord(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: int = Column(UUID(as_uuid=True), ForeignKey("company.id"))
    remote_id = Column(UUID(BigInteger),nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    json_data = Column(Text, nullable=False)



    @staticmethod
    def get_id_field_name()->str:
        return "id"
