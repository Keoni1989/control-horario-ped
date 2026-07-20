# Control Horario PED

Backend proof of concept for attendance management in vocational training courses, built with FastAPI.

## Why I built it

This project started from a real need: replacing paper attendance sheets with a digital system that could make attendance records more reliable and reduce invalid check-ins.

The idea was to combine classroom sessions, QR token validation, IP checks and a simple check-in/check-out flow.

## Overview

The API currently supports:

- checking whether an active classroom session exists;
- validating a QR token and classroom IP access;
- registering student check-in and check-out;
- storing attendance records in a relational database;
- generating synthetic demo data for local testing.

## Current scope

### Implemented

- FastAPI REST API
- SQLite persistence with SQLAlchemy
- Classroom and session management
- Active session lookup
- IP-based access validation
- QR token validation
- Student check-in and check-out
- Synthetic demo seed data
- Automated tests for the main attendance flow

### Not implemented

- Frontend interface
- Administrator authentication
- QR code generation
- Advanced reporting
- Production deployment and security hardening

This repository should be considered a backend proof of concept, not a production-ready attendance system.

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- pytest

## Installation

Clone the repository and open the backend folder:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

To run the tests, also install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Environment

Copy the example environment file:

```bash
copy .env.example .env
```

The application reads `DATABASE_URL` from the environment.

When the variable is not configured, it uses a local SQLite database inside the backend folder.

## Run locally

Start the API with:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Available endpoints:

- API health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

## Seed demo data

Run:

```bash
python app/seed.py
```

The seed creates fictional courses, classrooms, teachers and students for local testing.

All names and identifiers included in the repository are synthetic.

## Example API flow

### Get the active classroom session

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

Run the automated tests from the backend folder:

```bash
pytest -q
```

The test suite covers:

- API health check;
- root endpoint;
- invalid attendance requests;
- missing active sessions;
- the complete active session, check-in and check-out flow using an isolated temporary database.

## Status

Working backend proof of concept.

The main attendance flow is implemented and tested. Future development could include an administration interface, reporting tools and stronger authentication.
pytest -q
```

## Status

Backend proof of concept, suitable for junior portfolio review.
