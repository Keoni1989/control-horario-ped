from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel


class ActiveSessionResponse(BaseModel):
    session_id: int
    session_date: date
    start_time: time
    end_time: time
    is_active: bool
    qr_token: str

    course_id: int
    course_name: str
    course_code: str

    classroom_id: int
    classroom_name: str
    classroom_code: str

    teacher_id: int
    teacher_name: str


class CheckInRequest(BaseModel):
    session_id: int
    qr_token: str
    document_last4: str
    personal_pin: Optional[str] = None
    method: str = "qr"


class CheckOutRequest(BaseModel):
    session_id: int
    qr_token: str
    document_last4: str
    personal_pin: Optional[str] = None
    method: str = "qr"


class AttendanceResponse(BaseModel):
    attendance_id: int
    session_id: int
    student_id: int
    student_name: str

    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None

    check_in_method: Optional[str] = None
    check_out_method: Optional[str] = None

    is_late: bool
    message: str