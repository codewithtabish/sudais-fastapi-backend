from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from db.database import Base


class PersonalInfo(Base):
    __tablename__ = "personal_info"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # One-to-Many relationship with translations
    translations = relationship(
        "PersonalInfoTranslation",
        back_populates="personal_info",
        cascade="all, delete-orphan"
    )
