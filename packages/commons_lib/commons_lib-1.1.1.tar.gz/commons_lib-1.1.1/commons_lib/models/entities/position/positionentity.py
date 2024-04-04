from sqlalchemy import Column, ForeignKey, BIGINT, VARCHAR
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from server_main.models.entities.base_entity import BaseEntity


class PositionEntity(BaseEntity):
    __tablename__ = "positions"

    position_type_id = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))
    positionType = relationship('PositionCategoryEntity', back_populates='positions')
    employees = relationship('EmploymentEntity', back_populates="position")

    positionName: Mapped[str] = Column(VARCHAR(255), nullable=False)
    description: Mapped[str] = Column(VARCHAR(1000))
    organization_id: Mapped[int] = mapped_column(BIGINT, nullable=False)


class PositionEmployment(BaseEntity):
    __tablename__ = "position_employment"

    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.pk_uuid"))
    employment_id = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"))
