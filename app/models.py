from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=False)
    
    # Optional fields
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True)
    
    # Metadata timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.name}', course='{self.course}')>"
