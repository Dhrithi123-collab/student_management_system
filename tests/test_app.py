import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    database = tmp_path / "test_students.db"

    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "DATABASE": str(database),
    })


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin123!",
        },
    )

    assert response.status_code == 302
    return client


def test_home_redirects_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Login" in response.data


def test_valid_login(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin123!",
        },
    )

    assert response.status_code == 302
    assert "/students" in response.location


def test_invalid_login(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_student_api_requires_login(client):
    response = client.get("/api/students")

    assert response.status_code == 401


def test_add_student(logged_in_client):
    response = logged_in_client.post(
        "/api/students",
        json={
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "course": "Computer Engineering",
        },
    )

    assert response.status_code == 201
    assert response.json["message"] == "Student added"


def test_add_student_rejects_invalid_data(logged_in_client):
    response = logged_in_client.post(
        "/api/students",
        json={
            "name": "",
            "email": "invalid",
            "course": "",
        },
    )

    assert response.status_code == 400


def test_list_students(logged_in_client):
    logged_in_client.post(
        "/api/students",
        json={
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "course": "Computer Engineering",
        },
    )

    response = logged_in_client.get("/api/students")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Rahul Sharma"


def test_edit_student(logged_in_client):
    created = logged_in_client.post(
        "/api/students",
        json={
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "course": "Computer Engineering",
        },
    )

    student_id = created.json["id"]

    response = logged_in_client.put(
        f"/api/students/{student_id}",
        json={
            "name": "Rahul Patil",
            "email": "rahul.patil@example.com",
            "course": "Information Technology",
        },
    )

    assert response.status_code == 200

    students = logged_in_client.get("/api/students").json

    assert students[0]["name"] == "Rahul Patil"
    assert students[0]["course"] == "Information Technology"


def test_edit_nonexistent_student(logged_in_client):
    response = logged_in_client.put(
        "/api/students/999",
        json={
            "name": "Rahul",
            "email": "rahul@example.com",
            "course": "Computer Engineering",
        },
    )

    assert response.status_code == 404


def test_delete_student(logged_in_client):
    created = logged_in_client.post(
        "/api/students",
        json={
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "course": "Computer Engineering",
        },
    )

    student_id = created.json["id"]

    response = logged_in_client.delete(
        f"/api/students/{student_id}"
    )

    assert response.status_code == 200
    assert logged_in_client.get("/api/students").json == []


def test_staff_cannot_delete_students(client):
    client.post(
        "/login",
        data={
            "username": "staff",
            "password": "Staff123!",
        },
    )

    created = client.post(
        "/api/students",
        json={
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "course": "Computer Engineering",
        },
    )

    response = client.delete(
        f"/api/students/{created.json['id']}"
    )

    assert response.status_code == 403


def test_duplicate_email_is_rejected(logged_in_client):
    student = {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "course": "Computer Engineering",
    }

    first = logged_in_client.post("/api/students", json=student)
    second = logged_in_client.post("/api/students", json=student)

    assert first.status_code == 201
    assert second.status_code == 409

def test_static_assets_are_available(client):
    css_response = client.get("/static/css/style.css")
    js_response = client.get("/static/js/app.js")

    assert css_response.status_code == 200
    assert b".login-shell" in css_response.data
    assert js_response.status_code == 200
    assert b"refreshStudents" in js_response.data


def test_student_page_references_static_assets(logged_in_client):
    response = logged_in_client.get("/students")

    assert response.status_code == 200
    assert b"/static/css/style.css" in response.data
    assert b"/static/js/app.js" in response.data
