import json
import logging
from typing import Dict, Any, List
import httpx
from sqlalchemy.orm import Session

from app.models import Student
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


def build_student_context(students: List[Student]) -> str:
    """Format student records into structured context for the LLM."""
    if not students:
        return "Database currently contains 0 student records."

    lines = [f"Total student records: {len(students)}\n"]
    lines.append("Student Records List:")
    for s in students:
        lines.append(
            f"- Student ID: {s.student_id} | Name: {s.name} | "
            f"DOB: {s.date_of_birth} | Course: {s.course or 'N/A'} | "
            f"Enrollment Date: {s.enrollment_date or 'N/A'} | "
            f"Email: {s.email} | Phone: {s.phone}"
        )
    return "\n".join(lines)


def answer_locally_as_fallback(question: str, students: List[Student]) -> str:
    """Provide a reliable fallback response if Ollama is offline."""
    q_lower = question.lower()
    total = len(students)
    
    if "how many" in q_lower or "count" in q_lower or "total" in q_lower:
        return f"There are currently {total} student(s) in the database."

    if "born after" in q_lower:
        import re
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', q_lower)
        if year_match:
            year = int(year_match.group(1))
            matched = [s for s in students if s.date_of_birth and s.date_of_birth.year > year]
            if not matched:
                return f"No students found born after {year}."
            names = ", ".join([f"{s.name} (ID: {s.student_id}, DOB: {s.date_of_birth})" for s in matched])
            return f"Students born after {year} ({len(matched)}): {names}."

    return (
        f"Database has {total} records. (Ollama service unavailable. "
        f"To enable AI generation, start Ollama with 'ollama serve' and pull '{OLLAMA_MODEL}')."
    )


async def query_ollama(question: str, db: Session) -> Dict[str, Any]:
    """
    Fetch student database context and query Ollama model.
    Ensures safe, grounded answers without exposing raw SQL execution.
    """
    # Fetch all records safely via ORM
    students = db.query(Student).order_by(Student.id.asc()).all()
    context = build_student_context(students)

    system_prompt = (
        "You are a helpful, precise database assistant for a school's Student Records System.\n"
        "Your task is to answer user questions using ONLY the verified database records provided below.\n"
        "CRITICAL RULES:\n"
        "1. Never invent or hallucinate student information, IDs, courses, or numbers.\n"
        "2. Only reference facts directly stated in the Database Records context.\n"
        "3. Pay strict attention to numeric and date comparisons (e.g. 'born after 2005' means year > 2005 such as 2006, 2007; do not include 2004 or 2005).\n"
        "4. If the answer cannot be determined from the records, clearly say you don't have that information.\n"
        "5. Be concise, direct, and professional.\n\n"
        f"--- DATABASE RECORDS ---\n{context}\n----------------------\n\n"
        f"User Question: {question}\nAnswer:"
    )

    ollama_endpoint = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(ollama_endpoint, json=payload)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "").strip()
                return {
                    "question": question,
                    "answer": answer,
                    "context_records_count": len(students),
                    "model": OLLAMA_MODEL
                }
            else:
                logger.warning("Ollama returned status code %s: %s", response.status_code, response.text)
                fallback = answer_locally_as_fallback(question, students)
                return {
                    "question": question,
                    "answer": fallback,
                    "context_records_count": len(students),
                    "model": f"{OLLAMA_MODEL} (fallback: HTTP {response.status_code})"
                }
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        logger.warning("Ollama connection failed: %s. Using safe fallback.", exc)
        fallback = answer_locally_as_fallback(question, students)
        return {
            "question": question,
            "answer": fallback,
            "context_records_count": len(students),
            "model": f"{OLLAMA_MODEL} (offline fallback)"
        }
    except Exception as exc:
        logger.error("Unexpected error querying Ollama: %s", exc)
        fallback = answer_locally_as_fallback(question, students)
        return {
            "question": question,
            "answer": fallback,
            "context_records_count": len(students),
            "model": f"{OLLAMA_MODEL} (error fallback)"
        }
