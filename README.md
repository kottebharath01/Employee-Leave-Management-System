# Employee Leave & Approval Workflow Management System

A full-stack, role-based leave request and approval system built with **FastAPI + PostgreSQL** on the backend
and **React + Vite** on the frontend. Designed as a clean, beginner-friendly but production-structured
portfolio project.

---

## 1. Project Overview

Employees submit leave requests, which are automatically routed up a configurable approval hierarchy
(Team Lead → Manager → Senior Manager → Director → CEO, or the parallel HR hierarchy). Approvers can
approve or reject, balances are automatically tracked (paid vs. unpaid days), and everyone gets
notified of what happens to their requests. HR and Admin have separate, non-overlapping responsibilities.

## 2. Problem Statement

Manual leave tracking (spreadsheets, email chains) is error-prone: approvers don't know who is
next in line, balances get out of sync, and there's no audit trail of who approved what and why.
This system solves that with enforced business rules, a clear approval chain, and a full history log.

## 3. Features

- JWT authentication with bcrypt password hashing (no plaintext passwords, ever)
- Role-based authorization enforced **on the backend** (10 roles across 2 hierarchies + Admin)
- Full leave-request lifecycle: apply → route → approve/reject → balance update → notify
- Paid + unpaid day splitting with an explicit "do you want to continue?" confirmation step
- Weekend + company-holiday exclusion from working-day counts
- Overlap detection between leave requests
- Edit/cancel rules (only while pending / only before the leave starts)
- Full approval audit trail (immutable history)
- In-app notifications with read/unread state
- HR tools: employees, leave types, balances, holidays
- Admin tools: system users, roles, account activation/deactivation

## 4. Tech Stack

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| Backend        | Python 3.11 / 3.13, FastAPI, SQLAlchemy 2.0   |
| Database       | PostgreSQL 18 (Local Windows Service)         |
| Migrations     | Alembic                                       |
| Auth           | bcrypt (password hashing) + JWT (python-jose) |
| Validation     | Pydantic v2                                   |
| Frontend       | React 19, Vite, plain CSS                     |
| Testing        | pytest + FastAPI TestClient (81 tests)        |
| Containerization | Docker, docker-compose (Optional alternative) |

## 5. Architecture

```
Browser (React SPA)
      │  REST/JSON + JWT bearer token
      ▼
FastAPI app (routes → services → models)
      │  SQLAlchemy ORM
      ▼
PostgreSQL
```

- **Routes** (`app/routes/`): thin HTTP layer — parse input, call a service, return the result.
- **Services** (`app/services/`): all business rules live here (approval routing, balance math,
  overlap checks, etc.). This is the layer you'd unit test most heavily.
- **Models** (`app/models/`): SQLAlchemy ORM tables.
- **Schemas** (`app/schemas/`): Pydantic request/response contracts (never leak `password_hash`).
- **Dependencies** (`app/dependencies/`): `get_current_user`, `require_hr`, `require_admin`, etc.

## 6. Folder Structure

```
employee-leave-system/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app, router registration, exception handlers
│   │   ├── core/                  # config, enums/constants, security (hash/JWT)
│   │   ├── database/               # SQLAlchemy engine/session
│   │   ├── models/                 # ORM models (8 tables)
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── services/                # business logic
│   │   ├── routes/                  # FastAPI routers
│   │   ├── dependencies/            # auth dependencies
│   │   └── utils/                   # date math, exceptions, DB seed script
│   ├── alembic/                     # migrations
│   ├── tests/                       # 79 pytest tests
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── api/client.js            # axios instance + JWT interceptor
│   │   ├── context/AuthContext.jsx  # login/logout/current-user state
│   │   ├── components/              # Layout, ProtectedRoute
│   │   ├── pages/
│   │   │   ├── employee/            # apply/edit/list/detail leave requests
│   │   │   ├── approver/            # pending approvals
│   │   │   ├── hr/                  # employees, leave types, balances, holidays
│   │   │   └── admin/               # users, roles
│   │   ├── roles.js
│   │   └── App.jsx                  # routing
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md   (this file)
```

## 7. Database Setup
 
The primary database runs **locally on Windows PostgreSQL 18** (not a cloud provider):

- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `employee_leave_db`
- **User**: `postgres`

For full, step-by-step Windows setup, service management, backup/restore, and troubleshooting, see [RUNNING.md](RUNNING.md).

```bash
# Create the primary and test databases:
psql -U postgres -c "CREATE DATABASE employee_leave_db;"
psql -U postgres -c "CREATE DATABASE leave_management_test;"
```

## 8. Environment Variables

Copy `backend.env.example` to `backend/.env` and set your local credentials:

**backend/.env**
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/employee_leave_db
JWT_SECRET_KEY=your-secure-random-32-character-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**frontend/.env**
```
VITE_API_BASE_URL=http://localhost:8000/api
```

## 9. Installation

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit values as needed

# Frontend
cd ../frontend
npm install
cp .env.example .env
```

## 10. Migration Commands

```bash
cd backend
source venv/bin/activate
alembic upgrade head             # apply all migrations
alembic revision --autogenerate -m "your message"   # create a new migration after model changes
alembic downgrade -1              # roll back the last migration
```

## 11. Seeding Sample Data (optional but recommended)

Since employees cannot self-register, run the seed script to create a full sample hierarchy
(CEO, Director, Senior Manager, Manager, Team Lead, Employee, HR chain, and one Admin), four leave
types, and two holidays:

```bash
cd backend
source venv/bin/activate
python -m app.utils.seed
```

All seeded accounts use the password `Password123`. Sample logins:

| Email                       | Role          |
|------------------------------|---------------|
| ceo@company.com              | CEO           |
| director@company.com         | DIRECTOR      |
| seniormanager@company.com    | SENIOR_MANAGER|
| manager@company.com          | MANAGER       |
| teamlead@company.com         | TEAM_LEAD     |
| employee@company.com         | EMPLOYEE      |
| hrdirector@company.com       | HR_DIRECTOR   |
| hrmanager@company.com        | HR_MANAGER    |
| hrassociate@company.com      | HR_ASSOCIATE  |
| admin@company.com            | HR_ASSOCIATE + is_admin=true |

## 12. Backend Execution

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API base URL: `http://localhost:8000/api`
Health check: `http://localhost:8000/api/health`

## 13. Frontend Execution

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

App URL: `http://localhost:5173`

## 14. Testing

79 pytest tests cover authentication, employee management, leave types, balances, the full leave
request lifecycle (including edge cases like zero working days, weekend+holiday combos, and
paid/unpaid splitting), the entire 8-step approval hierarchy, notifications, and holidays — run
against a **real PostgreSQL test database** (`leave_management_test`), not mocks.

```bash
cd backend
source venv/bin/activate
pytest                    # run everything
pytest -v                 # verbose
pytest tests/test_approvals.py   # a single module
```

**Actual last run result: 79 passed, 0 failed, 0 skipped** (see §Test Summary in the final chat
response for the full breakdown).

## 15. Swagger / OpenAPI

Once the backend is running, interactive API docs are available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Raw OpenAPI JSON: `http://localhost:8000/openapi.json`

## 16. Postman Usage

1. Import the OpenAPI spec directly: Postman → Import → paste `http://localhost:8000/openapi.json`.
2. Call `POST /api/auth/login` with `{"email": "...", "password": "..."}` to get an `access_token`.
3. Add header `Authorization: Bearer <access_token>` to all subsequent requests.
4. Or set a Postman collection variable `token` and use `{{token}}` in an Authorization header.

## 17. Docker Execution

```bash
# from the project root
docker compose up --build
```

This starts three containers: `db` (Postgres 16), `backend` (runs Alembic migrations automatically
on startup, then serves the API on :8000), and `frontend` (nginx serving the built React app on
:5173). Set a real `JWT_SECRET_KEY` env var before running in anything resembling production.

> **Note:** Docker was not available in the sandbox this project was built in, so the
> `docker-compose.yml` / Dockerfiles could not be executed end-to-end here. They follow standard,
> well-tested patterns (multi-stage frontend build served by nginx, `alembic upgrade head` on
> backend startup, a Postgres healthcheck gate), but please do a first-run sanity check in your
> own Docker environment.

## 18. Production Deployment Notes

- Set a long, random `JWT_SECRET_KEY` (never reuse the dev default).
- Set `DEBUG=false` and `ENVIRONMENT=production`.
- Run behind a reverse proxy (nginx/Caddy) with HTTPS termination.
- Use a managed PostgreSQL instance with regular backups.
- Run `alembic upgrade head` as part of your deploy pipeline, before starting new backend instances.
- Restrict `CORS_ORIGINS` to your real frontend domain(s).

## 19. Limitations

- Single-tenant (no multi-company support).
- Leave year is simply the calendar year of `start_date`; no custom fiscal-year support.
- No email delivery — notifications are in-app/database only.
- No file attachments on leave requests (e.g. medical certificates).
- Manager reassignment mid-flight does not automatically re-route already-pending requests.
- Frontend UI is intentionally minimal (per project scope: prioritize correctness over visual polish).

## 20. Future Improvements

- Email/SMS notification delivery.
- Configurable leave-year start date per organization.
- Bulk employee import (CSV).
- Calendar view of team leave.
- Soft-delete / undo for holidays and leave types instead of hard delete/deactivate only.
- Rate limiting and refresh tokens (currently a single long-lived access token).
