from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student")
    date_of_birth: date = Field(..., description="Date of birth in YYYY-MM-DD format")
    email: EmailStr = Field(..., description="Valid contact email address")
    phone: str = Field(..., min_length=5, max_length=30, description="Contact phone number")
    course: Optional[str] = Field(None, max_length=100, description="Enrolled course / department")
    address: Optional[str] = Field(None, max_length=255, description="Residential or postal address")
    enrollment_date: Optional[date] = Field(None, description="Date of enrollment (defaults to current date if omitted)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Student name cannot be empty or only whitespace")
        return trimmed

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        today = date.today()
        if v > today:
            raise ValueError("Date of birth cannot be in the future")
        if (today.year - v.year) > 120:
            raise ValueError("Date of birth is invalid (exceeds reasonable lifespan)")
        return v


class StudentCreate(StudentBase):
    student_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Unique Student ID (e.g. STU101). If omitted, an ID will be generated automatically."
    )

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Student ID cannot be empty or only whitespace")
            return trimmed
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=30)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Student name cannot be empty or only whitespace")
            return trimmed
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            today = date.today()
            if v > today:
                raise ValueError("Date of birth cannot be in the future")
        return v


class StudentResponse(StudentBase):
    id: int
    student_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    students: List[StudentResponse]


class AIQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Natural-language question about the student records")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or blank")
        return trimmed


class AIQueryResponse(BaseModel):
    question: str
    answer: str
    context_records_count: int
    model: str
