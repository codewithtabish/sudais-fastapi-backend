from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class PersonalInfoTranslation(Base):
    __tablename__ = "personal_info_translation"

    id = Column(Integer, primary_key=True, index=True)
    personal_info_id = Column(Integer, ForeignKey("personal_info.id", ondelete="CASCADE"))
    language = Column(String, nullable=False)  # e.g., "English", "Urdu", "French"
    name = Column(String, nullable=False)
    short_info = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    # Back reference to parent
    personal_info = relationship("PersonalInfo", back_populates="translations")
