from sqlalchemy.orm import relationship
from commons_lib.models.entities.user.user_entity import UserEntity


class EmployeeEntity(UserEntity):

    __tablename__ = "employees"

    employments = relationship("EmploymentEntity", back_populates="employee")


