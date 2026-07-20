from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)

    sessions = relationship("CourseSession", back_populates="course")


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    allowed_ip_prefix = Column(String, nullable=True)

    sessions = relationship("CourseSession", back_populates="classroom")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)

    sessions = relationship("CourseSession", back_populates="teacher")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)

    document_last4 = Column(String, nullable=False)
    personal_pin = Column(String, nullable=True)

    attendances = relationship("Attendance", back_populates="student")


class CourseSession(Base):
    __tablename__ = "course_sessions"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    is_active = Column(Boolean, default=True)
    qr_token = Column(String, unique=True, nullable=False)

    course = relationship("Course", back_populates="sessions")
    classroom = relationship("Classroom", back_populates="sessions")
    teacher = relationship("Teacher", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="course_session")


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)

    course_session_id = Column(Integer, ForeignKey("course_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    check_in_at = Column(DateTime, nullable=True)
    check_out_at = Column(DateTime, nullable=True)

    check_in_method = Column(String, nullable=True)
    check_out_method = Column(String, nullable=True)

    is_late = Column(Boolean, default=False)
    justification = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    course_session = relationship("CourseSession", back_populates="attendances")
    student = relationship("Student", back_populates="attendances")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)

    action = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)

    admin_name = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)