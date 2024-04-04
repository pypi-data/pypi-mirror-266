from server_main.models.entities import BaseEntity

from sqlalchemy import VARCHAR, Column


class WinningVendors(BaseEntity):
    __tablename__ = "winning_vendors"

    name = Column(VARCHAR(255), nullable=False)
    image = Column(VARCHAR(512), nullable=True)
    description = Column(VARCHAR(1000))
    website: str = Column(VARCHAR(512), nullable=True)
