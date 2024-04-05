from sqlalchemy import BIGINT, Column, VARCHAR
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID


from commons_lib.models.entities.base_entity import BaseEntity


class RedeemEntity(BaseEntity):
    __tablename__ = "redeems"
    employment_uuid = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"))
    employment = relationship('EmploymentEntity', back_populates='redeems')
    winning_uuid = Column(UUID(as_uuid=True), ForeignKey("winnings.pk_uuid"))
    winning: Mapped['WinningEntity'] = relationship("WinningEntity", back_populates='redeems')
    # image: str = Column(VARCHAR(512), nullable=True)
    # description: str = Column(VARCHAR(1000))
