from sqlalchemy import VARCHAR, Integer
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from commons_lib.models.entities.base_entity import BaseEntity


class WinningEntity(BaseEntity):
    __tablename__ = "winnings"

    title = Column(VARCHAR(255), nullable=False)
    image = Column(VARCHAR(512), nullable=True)
    description = Column(VARCHAR(1000))
    price = Column(Integer, nullable=False)
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))
    category_uuid = Column(UUID(as_uuid=True), ForeignKey("winning_category.pk_uuid", ondelete="CASCADE"),
                           nullable=True)
    category = relationship("WinningCategoryEntity", back_populates="winnings")
    redeems = relationship("RedeemEntity", back_populates="winning")
    vended_winning_uuid = Column(UUID, ForeignKey("vended_winnings.pk_uuid"), nullable=True)
    # vended_winning: Mapped['VendedWinningEntity'] = relationship("VendedWinningEntity", back_populates="winning")

