from sqlalchemy import Column, VARCHAR
from commons_lib.models.entities.base_entity import BaseEntity
import enum


class TransactionCategoryEntity(BaseEntity):
    __tablename__ = "transactions_category"

    title: str = Column(VARCHAR(256), nullable=True)
    # slug: str = enum()
