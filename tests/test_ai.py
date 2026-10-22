import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status


def test_ai_status_endpoint(client):
    res = client.get("/ai/status")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "configured_model" in data
    assert "is_online" in data


def test_ai_query_with_mocked_ollama(client, sample_student_data):
    # Insert a student first
    client.post("/students", json=sample_student_data)

    mock_ollama_resp = AsyncMock()
    mock_ollama_resp.status_code = 200
    mock_ollama_resp.json = lambda: {
        "model": "llama3.2:1b",
        "response": "There is currently 1 student in the database, Jane Doe."
    }

    with patch("httpx.AsyncClient.post", return_value=mock_ollama_resp):
        res = client.post("/ai/query", json={"question": "How many students are there?"})
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["question"] == "How many students are there?"
        assert "1 student" in data["answer"]
        assert data["context_records_count"] == 1


def test_ai_query_offline_fallback(client, sample_student_data):
    # Insert student
    client.post("/students", json=sample_student_data)

    # When Ollama is offline or uncontactable, it safely falls back
    with patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
        res = client.post("/ai/query", json={"question": "How many students are there?"})
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["context_records_count"] == 1
        assert "1 student" in data["answer"]


def test_ai_query_blank_validation(client):
    res = client.post("/ai/query", json={"question": "   "})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
