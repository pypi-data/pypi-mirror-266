from sqlalchemy import BIGINT
from sqlalchemy import Column
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from commons_lib.models.entities.base_entity import BaseEntity


class TransactionEntity(BaseEntity):
    
    __tablename__ = "transactions"

    employee_uuid = Column(UUID(as_uuid=True), ForeignKey("employment.pk_uuid"))
    employee = relationship(argument='EmploymentEntity', back_populates='transactions')

    redeem_uuid = Column(UUID(as_uuid=True), ForeignKey("redeems.pk_uuid"),)
    appreciation_id = Column(UUID(as_uuid=True), ForeignKey("appreciations.pk_uuid"),)
    transfer_id = Column(UUID(as_uuid=True), ForeignKey("transfers.pk_uuid"),)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.pk_uuid"),)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.pk_uuid"),)
