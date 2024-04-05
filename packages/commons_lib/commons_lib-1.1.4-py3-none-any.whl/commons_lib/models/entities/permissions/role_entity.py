from sqlalchemy import Column, VARCHAR


from commons_lib.models.entities.base_entity import BaseEntity


class RoleEntity(BaseEntity):
    __tablename__ = "role"

    title = Column(VARCHAR(256), nullable=False)
    description = Column(VARCHAR(1000), nullable=True)