from sqlalchemy import Column, ForeignKey, BIGINT, VARCHAR
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from server_main.models.entities.base_entity import BaseEntity


class PositionEntity(BaseEntity):
    __tablename__ = "positions"

    position_type_uuid = Column(UUID(as_uuid=True), ForeignKey("positiontypes.pk_uuid"))  # Foreign key constraint added
    position_type = relationship('PositionCategoryEntity', back_populates='positions')

    # Adjust the relationship definition with explicit primaryjoin
    employees = relationship('EmploymentEntity',
                             secondary='position_employment',
                             primaryjoin="PositionEntity.pk_uuid == PositionEmployment.position_uuid",
                             secondaryjoin="EmploymentEntity.pk_uuid == PositionEmployment.employment_uuid",
                             back_populates="position")

    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(1000))
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))


class PositionEmployment(BaseEntity):
    __tablename__ = "position_employment"

    position_uuid = Column(UUID(as_uuid=True), ForeignKey("positions.pk_uuid"))
    employment_uuid = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"))
