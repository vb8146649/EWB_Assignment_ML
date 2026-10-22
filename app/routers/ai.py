from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import httpx

from app.database import get_db
from app.schemas import AIQueryRequest, AIQueryResponse
from app.services.ai_service import query_ollama
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL

router = APIRouter(prefix="/ai", tags=["AI Extension (Ollama)"])


@router.post(
    "/query",
    response_model=AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask questions about student records",
    description="Ask natural-language questions (e.g. 'How many students are there?' or 'List students born after 2005'). Database records are safely fetched in Python and grounded in the prompt context sent to Ollama."
)
async def ask_ai_about_students(
    payload: AIQueryRequest,
    db: Session = Depends(get_db)
):
    result = await query_ollama(payload.question, db)
    return AIQueryResponse(**result)


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Check Ollama service status",
    description="Check connectivity to the local Ollama daemon and verify configured model."
)
async def check_ollama_status():
    ollama_online = False
    details = ""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                ollama_online = True
                details = resp.json()
    except Exception as exc:
        details = str(exc)

    return {
        "ollama_base_url": OLLAMA_BASE_URL,
        "configured_model": OLLAMA_MODEL,
        "is_online": ollama_online,
        "details": details
    }
