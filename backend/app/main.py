from datetime import date, datetime

from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.security import get_client_ip, is_ip_allowed
from app.schemas import (
    ActiveSessionResponse,
    CheckInRequest,
    CheckOutRequest,
    AttendanceResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Control Horario PED API",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Control Horario PED API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/db-check")
def db_check():
    return {
        "database": "connected"
    }


@app.get("/security/my-ip")
def get_my_ip(request: Request):
    client_ip = get_client_ip(request)

    return {
        "client_ip": client_ip
    }


@app.get(
    "/classrooms/{classroom_code}/active-session",
    response_model=ActiveSessionResponse
)
def get_active_session(
    classroom_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    client_ip = get_client_ip(request)

    active_session = (
        db.query(models.CourseSession)
        .join(models.Classroom)
        .join(models.Course)
        .join(models.Teacher)
        .filter(models.Classroom.code == classroom_code)
        .filter(models.CourseSession.session_date == date.today())
        .filter(models.CourseSession.is_active == True)
        .first()
    )

    if active_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found for this classroom today"
        )

    if not is_ip_allowed(
        client_ip=client_ip,
        allowed_ip_prefix=active_session.classroom.allowed_ip_prefix
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Access denied: network/IP not authorized for this classroom",
                "client_ip": client_ip,
                "classroom_code": active_session.classroom.code
            }
        )

    return ActiveSessionResponse(
        session_id=active_session.id,
        session_date=active_session.session_date,
        start_time=active_session.start_time,
        end_time=active_session.end_time,
        is_active=active_session.is_active,
        qr_token=active_session.qr_token,

        course_id=active_session.course.id,
        course_name=active_session.course.name,
        course_code=active_session.course.code,

        classroom_id=active_session.classroom.id,
        classroom_name=active_session.classroom.name,
        classroom_code=active_session.classroom.code,

        teacher_id=active_session.teacher.id,
        teacher_name=active_session.teacher.full_name,
    )


def find_student_for_attendance(
    db: Session,
    document_last4: str,
    personal_pin: str | None
):
    students_query = db.query(models.Student).filter(
        models.Student.document_last4 == document_last4
    )

    students = students_query.all()

    if len(students) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found with these document digits"
        )

    if len(students) == 1:
        student = students[0]

        if personal_pin is not None and student.personal_pin != personal_pin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid personal PIN"
            )

        return student

    if personal_pin is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="More than one student has these document digits. Personal PIN is required."
        )

    matching_students = [
        student for student in students
        if student.personal_pin == personal_pin
    ]

    if len(matching_students) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid personal PIN"
        )

    if len(matching_students) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="More than one student matches these credentials"
        )

    return matching_students[0]


def get_valid_active_session(
    db: Session,
    session_id: int,
    request: Request
):
    client_ip = get_client_ip(request)

    course_session = (
        db.query(models.CourseSession)
        .filter(models.CourseSession.id == session_id)
        .filter(models.CourseSession.session_date == date.today())
        .filter(models.CourseSession.is_active == True)
        .first()
    )

    if course_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found for today"
        )

    if not is_ip_allowed(
        client_ip=client_ip,
        allowed_ip_prefix=course_session.classroom.allowed_ip_prefix
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Access denied: network/IP not authorized for this classroom",
                "client_ip": client_ip,
                "classroom_code": course_session.classroom.code
            }
        )

    return course_session

def validate_qr_token(
    payload_qr_token: str,
    session_qr_token: str
):
    if payload_qr_token != session_qr_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid QR token for this session"
        )


@app.post(
    "/attendance/check-in",
    response_model=AttendanceResponse
)
def check_in(
    payload: CheckInRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    if payload.method not in ["qr", "manual_code"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid check-in method"
        )

    course_session = get_valid_active_session(
        db=db,
        session_id=payload.session_id,
        request=request
    )

    validate_qr_token(
        payload_qr_token=payload.qr_token,
        session_qr_token=course_session.qr_token
    )

    student = find_student_for_attendance(
        db=db,
        document_last4=payload.document_last4,
        personal_pin=payload.personal_pin
    )

    existing_attendance = (
        db.query(models.Attendance)
        .filter(models.Attendance.course_session_id == course_session.id)
        .filter(models.Attendance.student_id == student.id)
        .first()
    )

    if existing_attendance is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already checked in for this session"
        )

    now = datetime.now()
    is_late = now.time() > course_session.start_time

    attendance = models.Attendance(
        course_session_id=course_session.id,
        student_id=student.id,
        check_in_at=now,
        check_in_method=payload.method,
        is_late=is_late,
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return AttendanceResponse(
        attendance_id=attendance.id,
        session_id=course_session.id,
        student_id=student.id,
        student_name=student.full_name,

        check_in_at=attendance.check_in_at,
        check_out_at=attendance.check_out_at,

        check_in_method=attendance.check_in_method,
        check_out_method=attendance.check_out_method,

        is_late=attendance.is_late,
        message="Check-in registered successfully"
    )


@app.post(
    "/attendance/check-out",
    response_model=AttendanceResponse
)
def check_out(
    payload: CheckOutRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    if payload.method not in ["qr", "manual_code"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid check-out method"
        )

    course_session = get_valid_active_session(
        db=db,
        session_id=payload.session_id,
        request=request
    )

    validate_qr_token(
        payload_qr_token=payload.qr_token,
        session_qr_token=course_session.qr_token
    )

    student = find_student_for_attendance(
        db=db,
        document_last4=payload.document_last4,
        personal_pin=payload.personal_pin
    )

    attendance = (
        db.query(models.Attendance)
        .filter(models.Attendance.course_session_id == course_session.id)
        .filter(models.Attendance.student_id == student.id)
        .first()
    )

    if attendance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student has not checked in for this session"
        )

    if attendance.check_out_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already checked out for this session"
        )

    now = datetime.now()

    attendance.check_out_at = now
    attendance.check_out_method = payload.method

    db.commit()
    db.refresh(attendance)

    return AttendanceResponse(
        attendance_id=attendance.id,
        session_id=course_session.id,
        student_id=student.id,
        student_name=student.full_name,

        check_in_at=attendance.check_in_at,
        check_out_at=attendance.check_out_at,

        check_in_method=attendance.check_in_method,
        check_out_method=attendance.check_out_method,

        is_late=attendance.is_late,
        message="Check-out registered successfully"
    )