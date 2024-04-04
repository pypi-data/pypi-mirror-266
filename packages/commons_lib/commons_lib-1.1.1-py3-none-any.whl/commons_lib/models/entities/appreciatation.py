from sqlalchemy import Column, Integer, String, BIGINT, BOOLEAN, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from server_main.models.entities.base_entity import BaseEntity, Base


class AppreciationEntity(BaseEntity):
    __tablename__ = "appreciations"

    amount: Mapped[int] = Column(Integer, nullable=False)
    organization_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    message: str = Column(String, nullable=False)
    is_public = Column(BOOLEAN, nullable=False)
    from_employment_id = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"), )
    to_employment_id = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"), )
    behaviors = relationship("OrgBehaviorEntity", secondary="appreciationBehavior", back_populates="appreciations", lazy="select")
    organization_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    from_employment = relationship("EmploymentEntity", foreign_keys=[from_employment_id], back_populates="sent_appreciations", lazy="select")
    to_employment = relationship("EmploymentEntity", foreign_keys=[to_employment_id], back_populates="received_appreciations", lazy="select")


appreciation_behavior = Table(
    "appreciationBehavior",
    Base.metadata,
    Column("appreciation_pk_uuid", UUID(as_uuid=True), ForeignKey("appreciations.pk_uuid"), primary_key=True),
    Column("org_behavior_pk_uuid", UUID(as_uuid=True), ForeignKey("organizationBehaviors.pk_uuid"), primary_key=True),
)

