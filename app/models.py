from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    instructor = Column(String(255), nullable=False)
    material = Column(String(512), nullable=False)  # S3 filename
    material_name = Column(String(255), nullable=False)
    thumbnail = Column(String(512), nullable=True)  # S3 filename
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructor": self.instructor,
            "material": self.material,
            "material_name": self.material_name,
            "thumbnail": self.thumbnail,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
