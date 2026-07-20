from datetime import date, time, datetime, timedelta

from app.database import Base, engine, SessionLocal
from app.models import (
    Course,
    Classroom,
    Teacher,
    Student,
    CourseSession,
    Attendance,
    AuditLog,
)


def reset_database(db):
    """
    Cancella i dati demo in ordine corretto.
    Prima le tabelle dipendenti, poi quelle principali.
    """

    db.query(AuditLog).delete()
    db.query(Attendance).delete()
    db.query(CourseSession).delete()
    db.query(Student).delete()
    db.query(Teacher).delete()
    db.query(Classroom).delete()
    db.query(Course).delete()

    db.commit()


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        reset_database(db)

        # -------------------------
        # CORSI
        # -------------------------

        course_1 = Course(
            name="Desarrollo Web Full Stack",
            code="DWFS-001",
        )

        course_2 = Course(
            name="Competencias Digitales Básicas",
            code="CDB-001",
        )

        db.add_all([course_1, course_2])
        db.commit()

        # -------------------------
        # AULE
        # -------------------------

        classroom_1 = Classroom(
            name="Aula 1",
            code="AULA-1",
            allowed_ip_prefix="192.168.1.",
        )

        classroom_2 = Classroom(
            name="Aula 2",
            code="AULA-2",
            allowed_ip_prefix="192.168.1.",
        )

        db.add_all([classroom_1, classroom_2])
        db.commit()

        # -------------------------
        # DOCENTI
        # -------------------------

        teacher_1 = Teacher(
            full_name="Docente Demo 01",
        )

        teacher_2 = Teacher(
            full_name="Docente Demo 02",
        )

        db.add_all([teacher_1, teacher_2])
        db.commit()

        # -------------------------
        # STUDENTI
        # -------------------------

        student_1 = Student(
            full_name="Aina Vega",
            document_last4="0001",
            personal_pin="1001",
        )

        student_2 = Student(
            full_name="Bruno Soler",
            document_last4="0002",
            personal_pin="1002",
        )

        student_3 = Student(
            full_name="Clara Miro",
            document_last4="0003",
            personal_pin="1003",
        )

        student_4 = Student(
            full_name="Dario Navas",
            document_last4="0004",
            personal_pin="1004",
        )

        student_5 = Student(
            full_name="Elena Roca",
            document_last4="0005",
            personal_pin="1005",
        )

        db.add_all([
            student_1,
            student_2,
            student_3,
            student_4,
            student_5,
        ])
        db.commit()

        # -------------------------
        # SESSIONI CALENDARIO
        # -------------------------

        today = date.today()

        session_1_today = CourseSession(
            course_id=course_1.id,
            classroom_id=classroom_1.id,
            teacher_id=teacher_1.id,
            session_date=today,
            start_time=time(9, 0),
            end_time=time(14, 0),
            is_active=True,
            qr_token="QR-AULA-1-DWFS-DEMO",
        )

        session_2_tomorrow = CourseSession(
            course_id=course_1.id,
            classroom_id=classroom_1.id,
            teacher_id=teacher_1.id,
            session_date=today + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(14, 0),
            is_active=False,
            qr_token="QR-AULA-1-DWFS-DEMO-TOMORROW",
        )

        session_3_today_afternoon = CourseSession(
            course_id=course_2.id,
            classroom_id=classroom_2.id,
            teacher_id=teacher_2.id,
            session_date=today,
            start_time=time(16, 0),
            end_time=time(19, 0),
            is_active=False,
            qr_token="QR-AULA-2-CDB-DEMO",
        )

        db.add_all([
            session_1_today,
            session_2_tomorrow,
            session_3_today_afternoon,
        ])
        db.commit()

        # -------------------------
        # PRESENZE DEMO
        # -------------------------
        # Ne mettiamo solo alcune, per testare dopo lista presenze/export.

        attendance_1 = Attendance(
            course_session_id=session_1_today.id,
            student_id=student_1.id,
            check_in_at=datetime.combine(today, time(9, 2)),
            check_out_at=None,
            check_in_method="qr",
            check_out_method=None,
            is_late=False,
            justification=None,
        )

        attendance_2 = Attendance(
            course_session_id=session_1_today.id,
            student_id=student_2.id,
            check_in_at=datetime.combine(today, time(9, 18)),
            check_out_at=None,
            check_in_method="manual_code",
            check_out_method=None,
            is_late=True,
            justification="Retraso justificado por transporte.",
        )

        db.add_all([attendance_1, attendance_2])
        db.commit()

        # -------------------------
        # AUDIT LOG DEMO
        # -------------------------

        audit_log = AuditLog(
            entity_type="attendance",
            entity_id=attendance_2.id,
            action="create_late_attendance_demo",
            old_value=None,
            new_value="Entrada con retraso justificado",
            admin_name="Sistema Demo",
        )

        db.add(audit_log)
        db.commit()

        print("Seed demo completato con successo.")
        print("")
        print("Dati creati:")
        print("- 2 corsi")
        print("- 2 aule")
        print("- 2 docenti")
        print("- 5 studenti")
        print("- 3 sessioni calendario")
        print("- 2 presenze demo")
        print("- 1 audit log demo")
        print("")
        print("Sessione attiva demo:")
        print("- Corso: Desarrollo Web Full Stack")
        print("- Aula: Aula 1")
        print("- Docente: Docente Demo 01")
        print("- QR token: QR-AULA-1-DWFS-DEMO")
        print("")
        print("Studenti demo utilizzabili:")
        print("- Aina Vega / ultime 4 cifre: 0001 / PIN: 1001")
        print("- Bruno Soler / ultime 4 cifre: 0002 / PIN: 1002")
        print("- Clara Miro / ultime 4 cifre: 0003 / PIN: 1003")
        print("- Dario Navas / ultime 4 cifre: 0004 / PIN: 1004")
        print("- Elena Roca / ultime 4 cifre: 0005 / PIN: 1005")

    except Exception as error:
        db.rollback()
        print("Errore durante il seed:")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()