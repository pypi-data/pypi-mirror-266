from sqlalchemy import Column, ForeignKey,VARCHAR
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID


from server_main.models.entities import BaseEntity


class WinningCategoryEntity(BaseEntity):
    __tablename__ = "winning_category"

    title = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(1000), nullable=True)
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))
    winnings = relationship("WinningEntity", back_populates="category")

