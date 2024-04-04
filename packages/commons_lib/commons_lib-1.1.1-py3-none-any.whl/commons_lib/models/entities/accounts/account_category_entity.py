from sqlalchemy import VARCHAR, Column
from sqlalchemy.orm import relationship
from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from server_main.models.entities.base_entity import BaseEntity


class AccountCategoryEntity(BaseEntity):

    __tablename__ = "accounts_type"

    title: str = Column(VARCHAR(256), nullable=False)
    slug: str = Column(VARCHAR(512), nullable=True)
    accounts = relationship(argument='AccountEntity', back_populates="account_type")
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))
