from sqlalchemy import Column, BIGINT, ForeignKey, VARCHAR
from sqlalchemy.dialects.postgresql import UUID

from commons_lib.models.entities.base_entity import BaseEntity


class PermissionEntity(BaseEntity):
    __tablename__ = "permission"

    role_uuid = Column(UUID(as_uuid=True), ForeignKey("role.pk_uuid"))
    title = Column(VARCHAR(256), nullable=True)
    # key = Column(VARCHAR(256), nullable=True)
