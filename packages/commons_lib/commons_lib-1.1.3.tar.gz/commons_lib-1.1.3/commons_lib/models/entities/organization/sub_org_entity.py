from sqlalchemy import VARCHAR, Column

from commons_lib.models.entities.base_entity import BaseEntity


class SubOrganizationEntity(BaseEntity):
    __tablename__ = "subOrganization"

    title = Column(VARCHAR(256), nullable=False)
    description = Column(VARCHAR(1000), nullable=True)
