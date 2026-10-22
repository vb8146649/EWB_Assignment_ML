# Students Database CRUD Application (+ AI Extension)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama-black.svg)](https://ollama.ai/)
[![Tests](https://img.shields.io/badge/Tests-17%20Passed-brightgreen.svg)]()

Backend application built for **EWB Edu Tech Pvt. Ltd. Internship Project Assignment**.  
This project implements a complete CRUD (Create, Read, Update, Delete) RESTful API for managing student profiles using **FastAPI** and **SQLite**, alongside an optional local AI question-answering extension powered by **Ollama**.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Project Architecture](#-project-architecture)
- [Database Schema](#-database-schema)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [Seeding Sample Data](#-seeding-sample-data)
- [API Endpoints & Documentation](#-api-endpoints--documentation)
- [Sample Requests & Responses](#-sample-requests--responses)
- [Local AI Extension (Ollama)](#-local-ai-extension-ollama)
- [Running Automated Tests](#-running-automated-tests)
- [Project Review Checklist](#-project-review-checklist)

---

## 🎯 Project Overview

The objective is to provide a clean, secure, and production-ready backend service to manage student records:
- **FastAPI** provides fast, auto-documented asynchronous HTTP endpoints.
- **SQLite** delivers persistent, lightweight relational storage with zero external database dependencies.
- **SQLAlchemy 2.0 ORM** structures database access, migrations, and relationship handling.
- **Pydantic V2** enforces strict data validation (email formatting, date validations, string sanitization).
- **Ollama AI Assistant** safely queries student records using context grounding (RAG), strictly avoiding unconstrained SQL execution.

---

## ✨ Key Features

1. **Complete CRUD Operations**:
   - **Create**: Add student records with auto-generated or custom student IDs and validation.
   - **Read**: List students with pagination, search, and multidimensional filters (course, date of birth, enrollment date).
   - **Update**: Full (`PUT`) and partial (`PATCH`) profile updates with conflict detection.
   - **Delete**: Safely delete records by student ID.
2. **Robust Input Validation**:
   - Proper date validation (rejects future dates of birth and unrealistic lifespans).
   - Email format validation with uniqueness verification.
   - Non-blank string sanitation for names and student IDs.
3. **Local AI Extension (Section 05 Bonus)**:
   - Connects to local Ollama (`llama3.1:latest`, `llama3.2:1b`, etc.).
   - Answers questions like *"How many students are there?"* or *"List students born after 2005"*.
   - Safely grounded in retrieved database records.
   - Built-in graceful offline fallback if Ollama is not running.
4. **Interactive Swagger & ReDoc Documentation**:
   - Auto-generated interactive Swagger UI at `/docs`.
   - ReDoc alternative documentation at `/redoc`.

---

## 🏗️ Project Architecture

```
.
├── app/
│   ├── __init__.py
│   ├── config.py             # Environment configurations and defaults
│   ├── database.py           # SQLite engine, SessionLocal, Base, get_db dependency
│   ├── models.py             # SQLAlchemy ORM student model
│   ├── schemas.py            # Pydantic request/response validation schemas
│   ├── crud.py               # Database query and persistence layer
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py       # CRUD REST endpoints (/students)
│   │   └── ai.py             # AI query endpoints (/ai)
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py     # Ollama API client & database context grounding
│   └── main.py               # FastAPI entry point, CORS, lifespan handler
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Test fixtures (isolated in-memory SQLite, client)
│   ├── test_crud.py          # CRUD unit tests
│   ├── test_api.py           # API endpoint integration tests
│   └── test_ai.py            # AI integration & fallback tests
├── seed_data.py              # Realistic dummy data population script
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Complete documentation
```

---

## 🗄️ Database Schema

The `students` table contains the following fields:

| Field | Type | Description | Mandatory / Optional |
|---|---|---|---|
| `id` | `INTEGER` | Primary key (auto-increment) | System Generated |
| `student_id` | `VARCHAR(50)` | Unique student ID (e.g. `STU-1001`) | **Mandatory** (auto-generated if omitted) |
| `name` | `VARCHAR(100)` | Full student name | **Mandatory** |
| `date_of_birth` | `DATE` | Birth date (`YYYY-MM-DD`) | **Mandatory** |
| `email` | `VARCHAR(100)` | Unique contact email | **Mandatory** |
| `phone` | `VARCHAR(30)` | Contact phone number | **Mandatory** |
| `course` | `VARCHAR(100)` | Department / Course of study | *Optional* |
| `address` | `VARCHAR(255)` | Address | *Optional* |
| `enrollment_date`| `DATE` | Enrollment date | *Optional* (defaults to today) |
| `created_at` | `DATETIME` | Timestamp of creation | Auto |
| `updated_at` | `DATETIME` | Timestamp of last modification | Auto |

---

## 📦 Prerequisites

- **Python 3.10+** (Tested on Python 3.12)
- **Git**
- *(Optional for AI Extension)*: **Ollama** installed locally (`curl -fsSL https://ollama.com/install.sh | sh`)

---

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏃 Running the Application

Start the FastAPI development server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **API Root / Health Check**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🌱 Seeding Sample Data

Populate the database with realistic dummy student records (across various courses, birth years, and dates):

```bash
python seed_data.py
```

*Output:*
```
Successfully seeded 8 dummy student records into SQLite database.
```

---

## 📡 Suggested API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/students` | Create a new student record |
| `GET` | `/students` | List all students with pagination & filters |
| `GET` | `/students/{student_id}` | Retrieve profile for a single student |
| `PUT` | `/students/{student_id}` | Full update of student details |
| `PATCH` | `/students/{student_id}` | Partial update of student details |
| `DELETE` | `/students/{student_id}` | Delete student record |
| `POST` | `/ai/query` | Natural-language query about student records |
| `GET` | `/ai/status` | Check local Ollama status & configured model |

---

## 💡 Sample Requests & Responses

### 1. Create a Student (`POST /students`)

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/students" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": "STU-2001",
       "name": "Meera Rao",
       "date_of_birth": "2005-06-14",
       "email": "meera.rao@example.com",
       "phone": "+91-9876500000",
       "course": "Artificial Intelligence",
       "address": "45 Tech Boulevard, Hyderabad",
       "enrollment_date": "2024-08-01"
     }'
```

**Response (`201 Created`):**
```json
{
  "id": 9,
  "student_id": "STU-2001",
  "name": "Meera Rao",
  "date_of_birth": "2005-06-14",
  "email": "meera.rao@example.com",
  "phone": "+91-9876500000",
  "course": "Artificial Intelligence",
  "address": "45 Tech Boulevard, Hyderabad",
  "enrollment_date": "2024-08-01",
  "created_at": "2026-10-22T14:30:00Z",
  "updated_at": "2026-10-22T14:30:00Z"
}
```

---

### 2. List & Filter Students (`GET /students`)

Filter by course or date:
```bash
curl -X GET "http://127.0.0.1:8000/students?course=Computer%20Science&born_after=2004-01-01"
```

**Response (`200 OK`):**
```json
{
  "total": 2,
  "skip": 0,
  "limit": 20,
  "students": [
    {
      "id": 4,
      "student_id": "STU-1004",
      "name": "Ananya Iyer",
      "date_of_birth": "2007-01-18",
      "email": "ananya.iyer@example.com",
      "phone": "+91-9634567890",
      "course": "Computer Science",
      "address": "12 Anna Salai, Chennai, Tamil Nadu",
      "enrollment_date": "2024-08-05",
      "created_at": "2026-10-22T09:02:36Z",
      "updated_at": "2026-10-22T09:02:36Z"
    },
    {
      "id": 8,
      "student_id": "STU-1008",
      "name": "Pooja Nair",
      "date_of_birth": "2007-08-25",
      "email": "pooja.nair@example.com",
      "phone": "+91-9278901234",
      "course": "Computer Science",
      "address": "56 Marine Drive, Kochi, Kerala",
      "enrollment_date": "2024-08-20",
      "created_at": "2026-10-22T09:02:36Z",
      "updated_at": "2026-10-22T09:02:36Z"
    }
  ]
}
```

---

### 3. Retrieve Student by ID (`GET /students/{student_id}`)

```bash
curl -X GET "http://127.0.0.1:8000/students/STU-1001"
```

---

### 4. Update Student Details (`PATCH /students/{student_id}`)

```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU-1001" \
     -H "Content-Type: application/json" \
     -d '{"phone": "+91-9999988888", "course": "Advanced Computer Science"}'
```

---

### 5. Delete a Student (`DELETE /students/{student_id}`)

```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU-2001"
```

**Response (`200 OK`):**
```json
{
  "message": "Student 'STU-2001' successfully removed from the database."
}
```

---

## 🤖 Local AI Extension (Ollama)

### How It Works:
1. Natural language questions are submitted to `POST /ai/query`.
2. The backend fetches verified records from SQLite via SQLAlchemy ORM.
3. The records are structured into an authoritative prompt context (RAG pattern).
4. Ollama generates a factual, grounded response based **solely** on the data.
5. **Security**: The LLM has **zero** direct SQL execution access, preventing any SQL injection or accidental database modification.

### Configuration:
By default, the application connects to:
- `OLLAMA_BASE_URL`: `http://localhost:11434`
- `OLLAMA_MODEL`: `llama3.1:latest` (or `llama3.2:1b`)

You can customize this via environment variables:
```bash
export OLLAMA_MODEL="llama3.2:1b"
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Sample AI Query:

```bash
curl -X POST "http://127.0.0.1:8000/ai/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "How many students are there, and who is studying Computer Science?"}'
```

**Sample AI Response:**
```json
{
  "question": "How many students are there, and who is studying Computer Science?",
  "answer": "There are a total of 8 students in the database. The students studying Computer Science are:\n1. Aarav Sharma (Student ID: STU-1001)\n2. Ananya Iyer (Student ID: STU-1004)\n3. Pooja Nair (Student ID: STU-1008)",
  "context_records_count": 8,
  "model": "llama3.1:latest"
}
```

---

## 🧪 Running Automated Tests

A comprehensive test suite with 17 unit and integration tests is included under `tests/`, covering:
- Database CRUD functions
- API validation and error handling (404, 409, 422)
- Query parameters, filtering, pagination
- AI service grounding and fallback handling

Run the test suite using `pytest`:

```bash
pytest -v
```

---

## ✅ Project Review Checklist

- [x] **All four CRUD operations work correctly**: (Create, Read, Update, Delete verified via pytest & API).
- [x] **SQLite data persists and can be retrieved accurately**: (Tested with persistent `students.db`).
- [x] **Input validation and missing-record handling work properly**: (Validates DOB, email format, duplicate keys, 404 for missing records).
- [x] **Code is organized and README instructions are reproducible**: (Clean modular structure, clear step-by-step instructions).
- [x] **Optional AI answers are grounded in retrieved records**: (Grounded context prompt sent to local Ollama with security restrictions).
