# Control Horario PED

Backend proof of concept for attendance management in vocational training courses, built with FastAPI.

## What this project is

This repository is a backend proof of concept. It demonstrates a simple API for:

- checking whether an active classroom session exists;
- validating a QR token and classroom IP access;
- registering check-in and check-out for students;
- seeding demo data locally for manual testing.

It is intentionally not a full production system. The goal is to show backend fundamentals clearly and honestly.

## Current scope

### Implemented

- FastAPI REST API
- SQLite persistence via SQLAlchemy
- Session lookup by classroom and date
- IP-based access control for classroom sessions
- Check-in and check-out flow
- Demo seed data

### Not implemented

- Real authentication for admins
- Frontend UI
- Production-grade security hardening
- Advanced reporting or QR generation features

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- pytest

## Installation

From the backend folder:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Environment

Copy the example file and adjust the database URL if needed:

```bash
copy .env.example .env
```

The project uses DATABASE_URL from the environment. If it is not set, it falls back to a local SQLite file inside the backend folder.

## Run locally

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then open:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## Seed demo data

Run:

```bash
python app/seed.py
```

This creates demo data with synthetic names and identifiers.

## Example API flow

### Get active session

```bash
curl http://127.0.0.1:8000/classrooms/AULA-1/active-session
```

### Check in

```bash
curl -X POST http://127.0.0.1:8000/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "qr_token": "QR-AULA-1-DWFS-DEMO", "document_last4": "0001", "personal_pin": "1001", "method": "qr"}'
```

### Check out

```bash
curl -X POST http://127.0.0.1:8000/attendance/check-out \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "qr_token": "QR-AULA-1-DWFS-DEMO", "document_last4": "0001", "personal_pin": "1001", "method": "qr"}'
```

## Testing

Run:

```bash
pytest -q
```

## Status

Backend proof of concept, suitable for junior portfolio review.
