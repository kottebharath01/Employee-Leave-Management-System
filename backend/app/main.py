from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routes import (
    auth_routes,
    employee_routes,
    leave_type_routes,
    leave_balance_routes,
    leave_request_routes,
    approval_routes,
    notification_routes,
    holiday_routes,
    department_routes,
    admin_routes,
)
from app.utils.exceptions import AppError

app = FastAPI(
    title=settings.APP_NAME,
    description="A role-based employee leave request & approval workflow system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.session import get_db


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming users and directing to docs and health checks."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "status": "running",
        "docs_url": "/docs",
        "health_url": "/health",
        "api_prefix": "/api",
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint confirming application and database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "app": settings.APP_NAME, "database": f"error: {str(exc)}"},
        )
    return {"status": "ok", "app": settings.APP_NAME, "database": db_status}


@app.get("/api/health", tags=["Health"])
def api_health_check(db: Session = Depends(get_db)):
    """Backwards-compatible API health check endpoint."""
    return health_check(db)


app.include_router(auth_routes.router)
app.include_router(employee_routes.router)
app.include_router(leave_type_routes.router)
app.include_router(leave_balance_routes.router)
app.include_router(leave_request_routes.router)
app.include_router(approval_routes.router)
app.include_router(notification_routes.router)
app.include_router(holiday_routes.router)
app.include_router(department_routes.router)
app.include_router(admin_routes.router)
