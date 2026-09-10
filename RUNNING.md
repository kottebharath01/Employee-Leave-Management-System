# Running the Employee Leave & Approval Workflow Management System

This guide provides complete instructions for setting up, running, testing, and managing the local PostgreSQL database and FastAPI backend on Windows.

---

## Architecture Overview

```
Local Windows Machine
  └── PostgreSQL 18 Service (localhost:5432)
        └── Database: employee_leave_db
              └── SQLAlchemy 2.0 (ORM) & Alembic (Migrations)
                    └── FastAPI Application (Backend API)
                          └── React + Vite (Frontend SPA)
```

> **Primary Setup**: Runs on native Windows PostgreSQL installed locally (`employee_leave_db`).  
> **Optional Alternative**: Docker Compose is available as a containerized option if desired.

---

## 1. How to Check PostgreSQL Installation

Check whether PostgreSQL and client utilities are installed on Windows:

```powershell
# Check psql CLI version
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" --version
# or if psql is in your PATH:
psql --version

# Check pg_dump utility version
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" --version
```

Expected output:
```text
psql (PostgreSQL) 18.4
pg_dump (PostgreSQL) 18.4
```

---

## 2. How to Start PostgreSQL on Windows

If the PostgreSQL service is stopped, start it via PowerShell (as Administrator):

```powershell
Start-Service postgresql-x64-18
```

Or using the Windows Command Prompt:
```cmd
net start postgresql-x64-18
```

---

## 3. How to Check PostgreSQL Service & Port Availability

Verify that the Windows service is running and listening on port 5432:

```powershell
# Check Windows service status
Get-Service postgresql-x64-18

# Verify port 5432 is open and listening
Test-NetConnection -ComputerName localhost -Port 5432
```

Expected output:
- `Status: Running`
- `TcpTestSucceeded: True`

---

## 4. How to Create `employee_leave_db`

To create the database if it doesn't already exist:

```powershell
# Using psql command line:
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432 -c "CREATE DATABASE employee_leave_db;"

# Verify database existence:
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432 -c "\l"
```

---

## 5. How to Configure `DATABASE_URL`

Environment variables are managed in `backend/.env`.

1. Copy the example environment template:
   ```powershell
   cd D:\Employee-Leave-Management-System\backend
   Copy-Item .env.example .env
   ```

2. Open `.env` and set your `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/employee_leave_db
   JWT_SECRET_KEY=your-secure-random-32-character-secret
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=development
   DEBUG=true
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

> **Important (Special Characters in Password)**:  
> If your PostgreSQL password contains special characters (such as `@`, `#`, `%`, `:`, `/`), URL-encode them:
> - `@` → `%40`
> - `:` → `%3A`
> - `/` → `%2F`
> - `%` → `%25`  
> Example: `password@123` becomes `postgresql://postgres:password%40123@localhost:5432/employee_leave_db`

---

## 6. How to Install Python Dependencies

Activate the virtual environment and install dependencies:

```powershell
cd D:\Employee-Leave-Management-System\backend

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install requirements
pip install -r requirements.txt
```

---

## 7. How to Run Alembic Migrations

Apply database migrations to create all required tables, foreign keys, and indexes:

```powershell
cd D:\Employee-Leave-Management-System\backend
.\venv\Scripts\Activate.ps1

# Apply migrations to latest revision
alembic upgrade head
```

Verify tables created in PostgreSQL:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432 -d employee_leave_db -c "\dt"
```

Tables created:
- `departments`
- `employees`
- `leave_types`
- `leave_balances`
- `leave_requests`
- `approval_history`
- `notifications`
- `holidays`
- `alembic_version`

---

## 8. How to Seed Development Data

Seed departments, leave types, employees across both approval hierarchies, initial leave balances, and company holidays:

```powershell
cd D:\Employee-Leave-Management-System\backend
python -m app.utils.seed
```

### Seed Accounts Summary (Development Password: `Password123`)

| Role | Email | Department | Approver / Reports To | Admin |
|------|-------|------------|------------------------|-------|
| `CEO` | `ceo@company.com` | Engineering | Auto-approved | No |
| `DIRECTOR` | `director@company.com` | Engineering | Carol CEO | No |
| `SENIOR_MANAGER` | `seniormanager@company.com` | Engineering | Dan Director | No |
| `MANAGER` | `manager@company.com` | Engineering | Sara SeniorManager | No |
| `TEAM_LEAD` | `teamlead@company.com` | Engineering | Mike Manager | No |
| `EMPLOYEE` | `employee@company.com` | Engineering | Tom TeamLead | No |
| `HR_DIRECTOR` | `hrdirector@company.com` | HR | Carol CEO | No |
| `HR_MANAGER` | `hrmanager@company.com` | HR | Helen HRDirector | No |
| `HR_EXECUTIVE` | `hrexecutive@company.com` | HR | Harry HRManager | No |
| `HR_ASSOCIATE` | `hrassociate@company.com` | HR | Harry HRManager | No |
| `ADMIN` | `admin@company.com` | HR | Carol CEO | **Yes** |
| `EMPLOYEE` | `finance@company.com` | Finance | Mike Manager | No |
| `EMPLOYEE` | `operations@company.com` | Operations | Mike Manager | No |

---

## 9. How to Start FastAPI

Start the backend application using Uvicorn:

```powershell
cd D:\Employee-Leave-Management-System\backend
.\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 10. How to Verify Swagger Documentation

Once the server is running, open your web browser to:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 11. How to Test Database Connection

Verify end-to-end connectivity (FastAPI → SQLAlchemy → PostgreSQL → `employee_leave_db`):

```powershell
# Using PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get

# Or using curl
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "app": "Employee Leave & Approval Workflow Management System",
  "database": "connected"
}
```

---

## 12. How to Run Tests

Run the test suite against the isolated test database:

```powershell
cd D:\Employee-Leave-Management-System\backend
.\venv\Scripts\Activate.ps1

# Run all 81 automated tests
pytest

# Run with verbose output
pytest -v
```

---

## 13. How to Back Up the Database

Back up the local `employee_leave_db` using `pg_dump`:

```powershell
# Format 1: Plain SQL script
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -h localhost -p 5432 -d employee_leave_db -F p -f "D:\Employee-Leave-Management-System\backup_employee_leave_db.sql"

# Format 2: Custom binary format (recommended for large databases)
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -h localhost -p 5432 -d employee_leave_db -F c -f "D:\Employee-Leave-Management-System\backup_employee_leave_db.dump"
```

---

## 14. How to Restore the Database

Restore `employee_leave_db` from a backup:

```powershell
# Restoring from plain SQL script:
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432 -d employee_leave_db -f "D:\Employee-Leave-Management-System\backup_employee_leave_db.sql"

# Restoring from custom binary format (.dump):
& "C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" -U postgres -h localhost -p 5432 -d employee_leave_db --clean --if-exists "D:\Employee-Leave-Management-System\backup_employee_leave_db.dump"
```

---

## 15. Database Reset / Rebuild Utility

To cleanly drop, recreate schema, re-run Alembic migrations, and reseed the development database:

```powershell
cd D:\Employee-Leave-Management-System\backend
python -m app.utils.rebuild_db --force
```

*(Note: Data is **never** automatically deleted when the backend starts. This utility is strictly on-demand).*

---

## 16. Troubleshooting Connection Errors

### 1. `FATAL: password authentication failed for user "postgres"`
- Ensure the password in `.env` is correct.
- If your password contains `@`, `#`, or other special characters, URL-encode them (e.g. `@` → `%40`).

### 2. `could not connect to server: Connection refused (0x0000274D)`
- Check if PostgreSQL service is running: `Get-Service postgresql-x64-18`.
- Start it if stopped: `Start-Service postgresql-x64-18`.

### 3. `FATAL: database "employee_leave_db" does not exist`
- Create the database: `& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE employee_leave_db;"`.

### 4. `ValueError: invalid interpolation syntax in ... at position ...`
- Occurs when `%` in URL-encoded passwords is misunderstood by configparser. This has been resolved in `alembic/env.py`.

---

## 17. Optional Alternative: Docker Setup

If you prefer running via Docker Compose instead of local Windows PostgreSQL:

```powershell
cd D:\Employee-Leave-Management-System
docker-compose up -d --build
```

---

## 18. Frontend Setup & Execution (React + Vite)

The frontend application communicates with the FastAPI backend at `http://localhost:8000/api`.

### 1. Navigate to the Frontend Directory
```powershell
cd D:\Employee-Leave-Management-System\frontend
```

### 2. Environment Configuration
The `.env` file is already created:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 3. Install Dependencies
```powershell
npm install
```

### 4. Start the Frontend Development Server
```powershell
npm run dev
```

The Vite dev server will start at:
👉 **[http://localhost:5173](http://localhost:5173)**

### 5. Build for Production
```powershell
npm run build
```
