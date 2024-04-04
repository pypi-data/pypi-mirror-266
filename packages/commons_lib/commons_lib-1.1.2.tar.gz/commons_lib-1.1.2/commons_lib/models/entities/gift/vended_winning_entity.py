from sqlmodel import VARCHAR, Integer
from sqlalchemy import Column, BIGINT, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
import uuid

from commons_lib.models.entities.base_entity import BaseEntity


class VendedWinningEntity(BaseEntity):
    __tablename__ = "vended_winnings"

    pk_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(255), nullable=False)
    image = Column(VARCHAR(512), nullable=True)
    description = Column(VARCHAR(1000))
    vendor_uuid = Column(BIGINT, ForeignKey("winning_vendors.pk_uuid"))
    # winning: Mapped['WinningEntity'] = relationship("WinningEntity", back_populates="vended_winning")


