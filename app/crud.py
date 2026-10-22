from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def get_student_by_student_id(db: Session, student_id: str) -> Optional[Student]:
    """Retrieve a student record by student_id or internal numeric primary key."""
    # First search by exact student_id string
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student:
        return student
    
    # If student_id is an integer, also check numeric primary key id
    if student_id.isdigit():
        return db.query(Student).filter(Student.id == int(student_id)).first()
    
    return None


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Retrieve a student by email address."""
    return db.query(Student).filter(Student.email.ilike(email)).first()


def generate_unique_student_id(db: Session) -> str:
    """Generate next sequential student ID like STU-1001."""
    # Find maximum ID
    max_id = db.query(func.max(Student.id)).scalar() or 0
    candidate_num = max_id + 1
    candidate = f"STU-{candidate_num:04d}"
    
    # Ensure uniqueness in case user created custom STU-xxxx
    while db.query(Student).filter(Student.student_id == candidate).first():
        candidate_num += 1
        candidate = f"STU-{candidate_num:04d}"
    return candidate


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create and persist a new student record."""
    student_id = student_in.student_id
    if not student_id:
        student_id = generate_unique_student_id(db)

    enrollment_date = student_in.enrollment_date or date.today()

    db_student = Student(
        student_id=student_id,
        name=student_in.name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email,
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=enrollment_date,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    course: Optional[str] = None,
    search: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    enrolled_after: Optional[date] = None,
    enrolled_before: Optional[date] = None,
) -> Tuple[List[Student], int]:
    """List students with optional search, filtering, and pagination."""
    query = db.query(Student)

    if course:
        query = query.filter(Student.course.ilike(f"%{course}%"))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Student.name.ilike(search_pattern),
                Student.email.ilike(search_pattern),
                Student.student_id.ilike(search_pattern),
                Student.phone.ilike(search_pattern),
            )
        )

    if born_after:
        query = query.filter(Student.date_of_birth >= born_after)

    if born_before:
        query = query.filter(Student.date_of_birth <= born_before)

    if enrolled_after:
        query = query.filter(Student.enrollment_date >= enrolled_after)

    if enrolled_before:
        query = query.filter(Student.enrollment_date <= enrolled_before)

    total = query.count()
    records = query.order_by(Student.id.asc()).offset(skip).limit(limit).all()
    return records, total


def update_student(
    db: Session,
    db_student: Student,
    update_data: StudentUpdate
) -> Student:
    """Update fields of an existing student."""
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_student, field, value)

    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> None:
    """Delete a student record from the database."""
    db.delete(db_student)
    db.commit()
