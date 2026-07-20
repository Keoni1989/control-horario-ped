from datetime import date, time
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models import (
    Course,
    Classroom,
    Teacher,
    Student,
    CourseSession,
)


def get_doc_last4(document_number: str) -> str:
    """
    Estrae solo le ultime 4 cifre numeriche da un identificativo demo.
    Esempi:
    00000000A -> 0000
    11111111B -> 1111
    """
    digits = "".join(char for char in document_number if char.isdigit())
    return digits[-4:]


STUDENTS = [
    {
        "full_name": "Aina Vega",
        "document_number": "00000000A",
    },
    {
        "full_name": "Bruno Soler",
        "document_number": "11111111B",
    },
    {
        "full_name": "Clara Miro",
        "document_number": "22222222C",
    },
    {
        "full_name": "Dario Navas",
        "document_number": "33333333D",
    },
    {
        "full_name": "Elena Roca",
        "document_number": "44444444E",
    },
    {
        "full_name": "Ferran Vila",
        "document_number": "55555555F",
    },
    {
        "full_name": "Gala Serra",
        "document_number": "66666666G",
    },
    {
        "full_name": "Hugo Pons",
        "document_number": "77777777H",
    },
    {
        "full_name": "Iris Tena",
        "document_number": "88888888I",
    },
    {
        "full_name": "Jordi Bellver",
        "document_number": "99999999J",
    },
    {
        "full_name": "Kira Sala",
        "document_number": "10101010K",
    },
    {
        "full_name": "León Marí",
        "document_number": "12121212L",
    },
    {
        "full_name": "Marta Cerdà",
        "document_number": "13131313M",
    },
    {
        "full_name": "Nico Dalmau",
        "document_number": "14141414N",
    },
    {
        "full_name": "Olga Ferrer",
        "document_number": "15151515O",
    },
]


TEACHER = {
    "full_name": "Pau Romero",
    "document_number": "16161616P",
}


def seed_demo_data(db: Session):
    """
    Inserisce dati demo per la prova locale.

    Nota privacy:
    il seed usa solo placeholder sintetici e non contiene dati reali.
    Nel database viene salvato solo document_last4.
    """

    course = db.query(Course).filter(Course.code == "PED-DEMO-001").first()

    if course is None:
        course = Course(
            name="Curso demo Control Horario PED",
            code="PED-DEMO-001",
        )
        db.add(course)
        db.commit()
        db.refresh(course)

    classroom = db.query(Classroom).filter(Classroom.code == "AULA-DEMO-01").first()

    if classroom is None:
        classroom = Classroom(
            name="Aula Demo 01",
            code="AULA-DEMO-01",
            allowed_ip_prefix="127.0.0.1,::1,192.168.",
        )
        db.add(classroom)
        db.commit()
        db.refresh(classroom)

    teacher = db.query(Teacher).filter(Teacher.full_name == TEACHER["full_name"]).first()

    if teacher is None:
        teacher = Teacher(
            full_name=TEACHER["full_name"],
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

    for item in STUDENTS:
        doc_last4 = get_doc_last4(item["document_number"])

        student = (
            db.query(Student)
            .filter(
                Student.full_name == item["full_name"],
                Student.document_last4 == doc_last4,
            )
            .first()
        )

        if student is None:
            student = Student(
                full_name=item["full_name"],
                document_last4=doc_last4,
                personal_pin=None,
            )
            db.add(student)
            db.commit()
            db.refresh(student)

    demo_session = (
        db.query(CourseSession)
        .filter(
            CourseSession.course_id == course.id,
            CourseSession.classroom_id == classroom.id,
            CourseSession.teacher_id == teacher.id,
            CourseSession.session_date == date.today(),
        )
        .first()
    )

    if demo_session is None:
        demo_session = CourseSession(
            course_id=course.id,
            classroom_id=classroom.id,
            teacher_id=teacher.id,
            session_date=date.today(),
            start_time=time(9, 0),
            end_time=time(14, 0),
            is_active=True,
            qr_token=f"AULA-DEMO-01-{uuid4()}",
        )
        db.add(demo_session)
        db.commit()
        db.refresh(demo_session)

    print("Seed demo completato.")
    print(f"Curso: {course.name}")
    print(f"Aula: {classroom.name}")
    print(f"Docente: {teacher.full_name}")
    print(f"Alumnos insertados/verificados: {len(STUDENTS)}")
    print(f"Sesión activa de hoy: {demo_session.session_date}")
    print(f"QR token: {demo_session.qr_token}")


def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_demo_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()