from datetime import date
import pytest
from app import crud
from app.schemas import StudentCreate, StudentUpdate


def test_create_and_get_student(db_session):
    student_in = StudentCreate(
        student_id="STU-001",
        name="John Smith",
        date_of_birth=date(2003, 1, 1),
        email="john@example.com",
        phone="1234567890",
        course="Physics",
        address="Campus Dorm 1",
        enrollment_date=date(2022, 9, 1),
    )
    student = crud.create_student(db_session, student_in)
    assert student.id is not None
    assert student.student_id == "STU-001"
    assert student.name == "John Smith"

    # Fetch by student_id
    fetched = crud.get_student_by_student_id(db_session, "STU-001")
    assert fetched is not None
    assert fetched.email == "john@example.com"

    # Fetch by email
    by_email = crud.get_student_by_email(db_session, "john@example.com")
    assert by_email is not None
    assert by_email.id == student.id


def test_auto_generate_student_id(db_session):
    student_in = StudentCreate(
        name="Auto ID Student",
        date_of_birth=date(2004, 2, 2),
        email="auto@example.com",
        phone="9876543210",
        course="Mathematics",
    )
    student = crud.create_student(db_session, student_in)
    assert student.student_id is not None
    assert student.student_id.startswith("STU-")


def test_update_student(db_session):
    student_in = StudentCreate(
        student_id="STU-002",
        name="Alice Old",
        date_of_birth=date(2002, 3, 3),
        email="alice@example.com",
        phone="1112223333",
        course="Biology",
    )
    student = crud.create_student(db_session, student_in)
    
    update_data = StudentUpdate(name="Alice New", course="Genetics")
    updated = crud.update_student(db_session, student, update_data)
    assert updated.name == "Alice New"
    assert updated.course == "Genetics"
    assert updated.email == "alice@example.com"


def test_delete_student(db_session):
    student_in = StudentCreate(
        student_id="STU-003",
        name="Bob Delete",
        date_of_birth=date(2001, 5, 5),
        email="bob@example.com",
        phone="9998887777",
    )
    student = crud.create_student(db_session, student_in)
    assert crud.get_student_by_student_id(db_session, "STU-003") is not None

    crud.delete_student(db_session, student)
    assert crud.get_student_by_student_id(db_session, "STU-003") is None


def test_list_and_filter_students(db_session):
    crud.create_student(db_session, StudentCreate(
        student_id="S1", name="Alpha Student", date_of_birth=date(2000, 1, 1),
        email="alpha@test.com", phone="12345", course="CS"
    ))
    crud.create_student(db_session, StudentCreate(
        student_id="S2", name="Beta Student", date_of_birth=date(2006, 6, 1),
        email="beta@test.com", phone="12346", course="Mechanical"
    ))

    # All
    records, total = crud.get_students(db_session)
    assert total == 2
    assert len(records) == 2

    # Filter by course
    cs_records, cs_total = crud.get_students(db_session, course="CS")
    assert cs_total == 1
    assert cs_records[0].student_id == "S1"

    # Filter born after 2005-01-01
    born_after, born_total = crud.get_students(db_session, born_after=date(2005, 1, 1))
    assert born_total == 1
    assert born_after[0].student_id == "S2"

    # Search keyword
    searched, search_total = crud.get_students(db_session, search="beta")
    assert search_total == 1
    assert searched[0].name == "Beta Student"
