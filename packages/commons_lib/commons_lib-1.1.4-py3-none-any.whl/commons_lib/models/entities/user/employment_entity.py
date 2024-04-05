from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Boolean, Column, VARCHAR,  BIGINT
from sqlalchemy.dialects.postgresql import UUID


from commons_lib.models.entities.base_entity import BaseEntity


class EmploymentEntity(BaseEntity):
    __tablename__ = "employment"

    employee_uuid = Column(UUID(as_uuid=True), ForeignKey('employees.pk_uuid'))
    employee = relationship('EmployeeEntity', back_populates='employments')
    profile = Column(VARCHAR(1000), nullable=True)
    org_email = Column(VARCHAR(320), nullable=True, unique=True)

    # Adjust the relationship definition with explicit primaryjoin
    position = relationship("PositionEntity", back_populates="employees", secondary="position_employment",
                            primaryjoin="EmploymentEntity.pk_uuid == PositionEmployment.employment_uuid",
                            secondaryjoin="PositionEntity.pk_uuid == PositionEmployment.position_uuid")

    accounts = relationship('AccountEntity', back_populates='employee')
    redeems = relationship('RedeemEntity', back_populates='employment')
    transactions = relationship('TransactionEntity', back_populates='employee')
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))

    sent_appreciations = relationship("AppreciationEntity", back_populates="from_employment",
                                      foreign_keys="AppreciationEntity.from_employment_uuid")
    received_appreciations = relationship("AppreciationEntity", back_populates="to_employment",
                                          foreign_keys="AppreciationEntity.to_employment_uuid")
    is_manager: bool = Column(Boolean, default=False)

