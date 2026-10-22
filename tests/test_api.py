import pytest
from fastapi import status


def test_create_student_success(client, sample_student_data):
    response = client.post("/students", json=sample_student_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["student_id"] == "TEST-001"
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_student_duplicate_student_id(client, sample_student_data):
    # First creation
    res1 = client.post("/students", json=sample_student_data)
    assert res1.status_code == status.HTTP_201_CREATED

    # Second creation with same student_id
    duplicate_data = sample_student_data.copy()
    duplicate_data["email"] = "different@example.com"
    res2 = client.post("/students", json=duplicate_data)
    assert res2.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in res2.json()["detail"]


def test_create_student_duplicate_email(client, sample_student_data):
    res1 = client.post("/students", json=sample_student_data)
    assert res1.status_code == status.HTTP_201_CREATED

    duplicate_data = sample_student_data.copy()
    duplicate_data["student_id"] = "TEST-002"
    res2 = client.post("/students", json=duplicate_data)
    assert res2.status_code == status.HTTP_409_CONFLICT
    assert "email" in res2.json()["detail"].lower()


def test_create_student_validation_errors(client):
    # Invalid email
    bad_payload = {
        "name": "Invalid Student",
        "date_of_birth": "2005-01-01",
        "email": "not-an-email",
        "phone": "12345"
    }
    res = client.post("/students", json=bad_payload)
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Future date of birth
    future_dob = {
        "name": "Time Traveler",
        "date_of_birth": "2099-01-01",
        "email": "timetraveler@example.com",
        "phone": "12345"
    }
    res2 = client.post("/students", json=future_dob)
    assert res2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Blank name
    blank_name = {
        "name": "   ",
        "date_of_birth": "2000-01-01",
        "email": "blank@example.com",
        "phone": "12345"
    }
    res3 = client.post("/students", json=blank_name)
    assert res3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_student_by_id(client, sample_student_data):
    client.post("/students", json=sample_student_data)

    # Success
    res = client.get("/students/TEST-001")
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["name"] == "Jane Doe"

    # Not found
    res_404 = client.get("/students/NON_EXISTENT")
    assert res_404.status_code == status.HTTP_404_NOT_FOUND


def test_list_and_filter_students(client, sample_student_data):
    client.post("/students", json=sample_student_data)

    student2 = sample_student_data.copy()
    student2["student_id"] = "TEST-002"
    student2["name"] = "Alice Wonderland"
    student2["email"] = "alice@wonder.com"
    student2["course"] = "Arts"
    student2["date_of_birth"] = "2007-06-15"
    client.post("/students", json=student2)

    # List all
    res = client.get("/students")
    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert body["total"] == 2
    assert len(body["students"]) == 2

    # Filter by course
    res_course = client.get("/students?course=Arts")
    assert res_course.status_code == status.HTTP_200_OK
    assert res_course.json()["total"] == 1
    assert res_course.json()["students"][0]["student_id"] == "TEST-002"

    # Filter by born_after
    res_dob = client.get("/students?born_after=2006-01-01")
    assert res_dob.json()["total"] == 1
    assert res_dob.json()["students"][0]["student_id"] == "TEST-002"

    # Search keyword
    res_search = client.get("/students?search=Wonderland")
    assert res_search.json()["total"] == 1


def test_update_student_put_and_patch(client, sample_student_data):
    client.post("/students", json=sample_student_data)

    # PUT update
    update_payload = {"name": "Jane Updated", "course": "Robotics"}
    res_put = client.put("/students/TEST-001", json=update_payload)
    assert res_put.status_code == status.HTTP_200_OK
    assert res_put.json()["name"] == "Jane Updated"
    assert res_put.json()["course"] == "Robotics"

    # PATCH update
    patch_payload = {"phone": "+1-999-0000"}
    res_patch = client.patch("/students/TEST-001", json=patch_payload)
    assert res_patch.status_code == status.HTTP_200_OK
    assert res_patch.json()["phone"] == "+1-999-0000"
    assert res_patch.json()["name"] == "Jane Updated"

    # 404 on missing
    res_404 = client.put("/students/UNKNOWN", json={"name": "Nobody"})
    assert res_404.status_code == status.HTTP_404_NOT_FOUND


def test_delete_student(client, sample_student_data):
    client.post("/students", json=sample_student_data)

    # Delete
    del_res = client.delete("/students/TEST-001")
    assert del_res.status_code == status.HTTP_200_OK

    # Ensure removed
    get_res = client.get("/students/TEST-001")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

    # Delete non-existent gives 404
    del_404 = client.delete("/students/TEST-001")
    assert del_404.status_code == status.HTTP_404_NOT_FOUND
