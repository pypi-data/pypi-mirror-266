from sqlalchemy.orm import relationship
from server_main.models.entities.user.user_entity import UserEntity


class EmployeeEntity(UserEntity):
    
    __tablename__ = "employees"

    employments = relationship("EmploymentEntity", back_populates="employee")


