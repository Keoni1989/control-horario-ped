import os
import tempfile
from datetime import date, datetime, time

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base, get_db
from app.main import app


client = TestClient(app)


def _build_test_db():
    temp_dir = tempfile.mkdtemp(prefix="testdb-", dir=".")
    db_path = os.path.join(temp_dir, "test.sqlite")
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        course = models.Course(name="Corso Demo", code="DEMO-001")
        classroom = models.Classroom(name="Aula Demo", code="AULA-DEMO", allowed_ip_prefix="127.0.0.1")
        teacher = models.Teacher(full_name="Docente Demo 01")
        student = models.Student(full_name="Aina Vega", document_last4="0001", personal_pin="1001")
        db.add_all([course, classroom, teacher, student])
        db.commit()
        db.refresh(course)
        db.refresh(classroom)
        db.refresh(teacher)
        db.refresh(student)

        session = models.CourseSession(
            course_id=course.id,
            classroom_id=classroom.id,
            teacher_id=teacher.id,
            session_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_active=True,
            qr_token="TEST-TOKEN",
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        return db, engine, temp_dir
    finally:
        db.close()


def test_positive_check_in_and_check_out_flow():
    db, engine, temp_dir = _build_test_db()

    try:
        app.dependency_overrides[get_db] = lambda: db

        response = client.get(
            "/classrooms/AULA-DEMO/active-session",
            headers={"x-forwarded-for": "127.0.0.1"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["qr_token"] == "TEST-TOKEN"

        check_in_response = client.post(
            "/attendance/check-in",
            json={
                "session_id": payload["session_id"],
                "qr_token": payload["qr_token"],
                "document_last4": "0001",
                "personal_pin": "1001",
                "method": "qr",
            },
            headers={"x-forwarded-for": "127.0.0.1"},
        )
        assert check_in_response.status_code == 200
        attendance = check_in_response.json()
        assert attendance["message"] == "Check-in registered successfully"

        check_out_response = client.post(
            "/attendance/check-out",
            json={
                "session_id": payload["session_id"],
                "qr_token": payload["qr_token"],
                "document_last4": "0001",
                "personal_pin": "1001",
                "method": "qr",
            },
            headers={"x-forwarded-for": "127.0.0.1"},
        )
        assert check_out_response.status_code == 200
        assert check_out_response.json()["message"] == "Check-out registered successfully"
    finally:
        app.dependency_overrides.clear()
        db.close()
        engine.dispose()
        for root, _, files in os.walk(temp_dir, topdown=False):
            for file_name in files:
                os.remove(os.path.join(root, file_name))
            os.rmdir(root)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_active_session_endpoint_returns_404_for_missing_session():
    response = client.get("/classrooms/UNKNOWN/active-session")
    assert response.status_code == 404


def test_check_in_without_valid_payload_returns_422():
    response = client.post(
        "/attendance/check-in",
        json={"session_id": 1, "qr_token": "abc"},
    )
    assert response.status_code == 422
