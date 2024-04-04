from sqlalchemy import Column, VARCHAR

from server_main.models.entities.base_entity import BaseEntity


class TransferCategoryEntity(BaseEntity):
    __tablename__ = "transfers_categories"

    title: str = Column(VARCHAR(256), nullable=True)
    # set enum
