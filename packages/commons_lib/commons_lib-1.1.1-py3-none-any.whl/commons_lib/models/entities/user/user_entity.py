from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlmodel import VARCHAR
from datetime import datetime

from server_main.models.entities.base_entity import BaseEntity


class UserEntity(BaseEntity):
    __abstract__ = True

    first_name: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    birth_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    gender: Mapped[bool] = mapped_column(Boolean, nullable=False)
    password_hash: Mapped[str] = mapped_column(VARCHAR(1000), nullable=False)
    password: Mapped[str] = mapped_column(VARCHAR(1000), nullable=False)
    phone_number: Mapped[str] = mapped_column(VARCHAR(11), nullable=False)
    otp_code: Mapped[str] = mapped_column(VARCHAR(6), nullable=True)
    otp_expire_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
