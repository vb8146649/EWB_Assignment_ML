"""
Database seeding script.
Populates the SQLite database with diverse dummy student records for demonstration and AI testing.
"""
from datetime import date
from app.database import SessionLocal, engine, Base
from app.models import Student

DUMMY_STUDENTS = [
    {
        "student_id": "STU-1001",
        "name": "Aarav Sharma",
        "date_of_birth": date(2003, 4, 15),
        "email": "aarav.sharma@example.com",
        "phone": "+91-9876543210",
        "course": "Computer Science",
        "address": "42 MG Road, Bengaluru, Karnataka",
        "enrollment_date": date(2022, 8, 1),
    },
    {
        "student_id": "STU-1002",
        "name": "Diya Patel",
        "date_of_birth": date(2006, 11, 22),
        "email": "diya.patel@example.com",
        "phone": "+91-9812345678",
        "course": "Data Science",
        "address": "15 Ring Road, Ahmedabad, Gujarat",
        "enrollment_date": date(2024, 7, 15),
    },
    {
        "student_id": "STU-1003",
        "name": "Rohan Gupta",
        "date_of_birth": date(2002, 9, 5),
        "email": "rohan.gupta@example.com",
        "phone": "+91-9723456789",
        "course": "Mechanical Engineering",
        "address": "88 Park Street, Kolkata, West Bengal",
        "enrollment_date": date(2021, 8, 10),
    },
    {
        "student_id": "STU-1004",
        "name": "Ananya Iyer",
        "date_of_birth": date(2007, 1, 18),
        "email": "ananya.iyer@example.com",
        "phone": "+91-9634567890",
        "course": "Computer Science",
        "address": "12 Anna Salai, Chennai, Tamil Nadu",
        "enrollment_date": date(2024, 8, 5),
    },
    {
        "student_id": "STU-1005",
        "name": "Karan Verma",
        "date_of_birth": date(2004, 7, 30),
        "email": "karan.verma@example.com",
        "phone": "+91-9545678901",
        "course": "Electrical Engineering",
        "address": "77 Civil Lines, Jaipur, Rajasthan",
        "enrollment_date": date(2023, 7, 20),
    },
    {
        "student_id": "STU-1006",
        "name": "Sneha Roy",
        "date_of_birth": date(2006, 3, 14),
        "email": "sneha.roy@example.com",
        "phone": "+91-9456789012",
        "course": "Data Science",
        "address": "33 VIP Road, Pune, Maharashtra",
        "enrollment_date": date(2024, 9, 1),
    },
    {
        "student_id": "STU-1007",
        "name": "Vikram Singh",
        "date_of_birth": date(2001, 12, 10),
        "email": "vikram.singh@example.com",
        "phone": "+91-9367890123",
        "course": "Civil Engineering",
        "address": "104 Mall Road, Shimla, Himachal Pradesh",
        "enrollment_date": date(2020, 8, 12),
    },
    {
        "student_id": "STU-1008",
        "name": "Pooja Nair",
        "date_of_birth": date(2007, 8, 25),
        "email": "pooja.nair@example.com",
        "phone": "+91-9278901234",
        "course": "Computer Science",
        "address": "56 Marine Drive, Kochi, Kerala",
        "enrollment_date": date(2024, 8, 20),
    }
]


def seed_database():
    """Populates the database with dummy students if not already present."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        added_count = 0
        for data in DUMMY_STUDENTS:
            existing = db.query(Student).filter(
                (Student.student_id == data["student_id"]) | (Student.email == data["email"])
            ).first()
            if not existing:
                student = Student(**data)
                db.add(student)
                added_count += 1
        db.commit()
        print(f"Successfully seeded {added_count} dummy student records into SQLite database.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
