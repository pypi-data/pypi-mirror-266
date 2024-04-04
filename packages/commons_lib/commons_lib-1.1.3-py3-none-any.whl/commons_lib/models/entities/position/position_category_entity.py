from typing import List

from sqlalchemy import String, Column
from sqlalchemy.orm import relationship, Mapped

from commons_lib.models.entities.base_entity import BaseEntity


class PositionCategoryEntity(BaseEntity):
    __tablename__ = "positiontypes"

    title = Column(String(255), nullable=False)
    description = Column(String(1000))

    # Define the relationship after both classes have been defined
    positions = relationship('PositionEntity', back_populates='position_type', primaryjoin="PositionCategoryEntity.pk_uuid == PositionEntity.position_type_uuid")
