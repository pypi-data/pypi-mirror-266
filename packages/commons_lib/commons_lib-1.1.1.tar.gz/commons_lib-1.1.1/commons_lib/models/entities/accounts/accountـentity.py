from datetime import date
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, BIGINT, ForeignKey, VARCHAR, DateTime
from sqlalchemy.orm import relationship, Mapped

from server_main.models.entities.base_entity import BaseEntity


class AccountEntity(BaseEntity):

    __tablename__ = "accounts"
    employee = relationship('EmploymentEntity', back_populates="accounts",)
    employee_uuid = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"),)
    appreciation_balance: int = Column(BIGINT, nullable=True)
    personal_balance: int = Column(BIGINT, nullable=True)
    balance: int = Column(BIGINT, nullable=True)
    account_type = relationship('AccountCategoryEntity', back_populates="accounts",)
    account_type_uuid = Column(UUID(as_uuid=True), ForeignKey("accounts_type.pk_uuid"),)
    expire_date: Mapped[date] = Column(DateTime, nullable=True)
