from sqlalchemy import Column, VARCHAR

from commons_lib.models.entities.base_entity import BaseEntity


class TransferCategoryEntity(BaseEntity):
    __tablename__ = "transfers_categories"

    title: str = Column(VARCHAR(256), nullable=True)
    # set enum
