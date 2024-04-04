from datetime import date
from sqlalchemy import ForeignKey, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from server_main.models.entities.base_entity import BaseEntity


class TransferEntity(BaseEntity):
    __tablename__ = "transfers"

    from_appreciation_account_uuid: UUID = Column(UUID(as_uuid=True), ForeignKey("account.pk_uuid"),)
    to_appreciation_account_uuid: UUID = Column(UUID(as_uuid=True), ForeignKey("account.pk_uuid"),)
    from_personal_account_uuid: UUID = Column(UUID(as_uuid=True), ForeignKey("account.pk_uuid"),)
    to_personal_account_uuid: UUID = Column(UUID(as_uuid=True), ForeignKey("account.pk_uuid"),)
    expire_at: Mapped[date] = Column(DateTime,nullable=False)
