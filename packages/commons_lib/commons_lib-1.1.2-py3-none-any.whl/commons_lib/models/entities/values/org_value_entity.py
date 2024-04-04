from sqlalchemy import Column, VARCHAR, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from commons_lib.models.entities.base_entity import BaseEntity


class OrgValueEntity(BaseEntity):
    __tablename__ = "organizationvalues"

    title: Mapped[str] = Column(VARCHAR(255), nullable=False)
    description: Mapped[str] = Column(VARCHAR(1000))

    behaviors = relationship("OrgBehaviorEntity", secondary="orgvaluebehavior", back_populates="values")
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))



