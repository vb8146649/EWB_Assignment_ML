from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
)
from app import crud

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Add a new student record to the SQLite database. If `student_id` is omitted, one will be generated automatically."
)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db)
):
    # Check if custom student_id is already taken
    if student_in.student_id:
        existing = crud.get_student_by_student_id(db, student_in.student_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with ID '{student_in.student_id}' already exists."
            )

    # Check if email is already registered
    existing_email = crud.get_student_by_email(db, student_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with email '{student_in.email}' already exists."
        )

    return crud.create_student(db, student_in)


@router.get(
    "",
    response_model=StudentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List and filter students",
    description="Retrieve a paginated list of students with optional filtering by course, date of birth, enrollment date, or keyword search."
)
def list_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    course: Optional[str] = Query(None, description="Filter by course name (partial match)"),
    search: Optional[str] = Query(None, description="Search by name, student ID, email, or phone"),
    born_after: Optional[date] = Query(None, description="Filter students born on or after this date (YYYY-MM-DD)"),
    born_before: Optional[date] = Query(None, description="Filter students born on or before this date (YYYY-MM-DD)"),
    enrolled_after: Optional[date] = Query(None, description="Filter students enrolled on or after this date (YYYY-MM-DD)"),
    enrolled_before: Optional[date] = Query(None, description="Filter students enrolled on or before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    records, total = crud.get_students(
        db=db,
        skip=skip,
        limit=limit,
        course=course,
        search=search,
        born_after=born_after,
        born_before=born_before,
        enrolled_after=enrolled_after,
        enrolled_before=enrolled_before,
    )
    return StudentListResponse(
        total=total,
        skip=skip,
        limit=limit,
        students=records
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a student by ID",
    description="Retrieve individual student profile details using their unique student ID."
)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a student's details (Full Update)",
    description="Modify all or selected fields of an existing student record."
)
def update_student_put(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )

    # Check email uniqueness if email is being updated
    if student_update.email and student_update.email.lower() != student.email.lower():
        existing_email = crud.get_student_by_email(db, student_update.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with email '{student_update.email}' already exists."
            )

    return crud.update_student(db, student, student_update)


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a student's details",
    description="Modify specific fields of an existing student profile."
)
def update_student_patch(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    return update_student_put(student_id=student_id, student_update=student_update, db=db)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a student",
    description="Remove a student record from the database."
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    crud.delete_student(db, student)
    return {"message": f"Student '{student_id}' successfully removed from the database."}
