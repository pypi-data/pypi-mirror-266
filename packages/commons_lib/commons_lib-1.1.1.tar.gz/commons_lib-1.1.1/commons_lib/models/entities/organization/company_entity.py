from sqlalchemy import Column, VARCHAR, BIGINT, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


from server_main.models.entities.base_entity import BaseEntity


class CompanyEntity(BaseEntity):
    __tablename__ = "company"

    name: str = Column(VARCHAR(256), nullable=False)
    description: str = Column(VARCHAR(1000), nullable=True)
    website:str=Column(VARCHAR(1000),nullable=True)
    employee_scale:str=Column(VARCHAR(1000),nullable=True)
    logo:str=Column(VARCHAR(1000), nullable=True)


class ChargeConfigurationEntity(BaseEntity):

    __tablename__ = "charge_configuration"

    amount: int = Column(BIGINT, nullable=False)
    charge_day: int = Column(BIGINT, nullable=False, default=1)
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey("company.pk_uuid"))
