from sqlalchemy import Column, Integer, String, BIGINT, BOOLEAN, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from server_main.models.entities.base_entity import BaseEntity, Base


class AppreciationEntity(BaseEntity):
    __tablename__ = "appreciations"

    amount: Mapped[int] = Column(Integer, nullable=False)
    message: str = Column(String, nullable=False)
    is_public = Column(BOOLEAN, nullable=False)
    from_employment_uuid = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"), )
    to_employment_uuid = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"), )
    behaviors = relationship("OrgBehaviorEntity", secondary="appreciationbehavior", back_populates="appreciations", lazy="select")
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))
    from_employment = relationship("EmploymentEntity", foreign_keys=[from_employment_uuid], back_populates="sent_appreciations", lazy="select")
    to_employment = relationship("EmploymentEntity", foreign_keys=[to_employment_uuid], back_populates="received_appreciations", lazy="select")


appreciation_behavior = Table(
    "appreciationbehavior",
    Base.metadata,
    Column("appreciation_pk_uuid", UUID(as_uuid=True), ForeignKey("appreciations.pk_uuid"), primary_key=True),
    Column("org_behavior_pk_uuid", UUID(as_uuid=True), ForeignKey("organizationbehaviors.pk_uuid"), primary_key=True),
)

