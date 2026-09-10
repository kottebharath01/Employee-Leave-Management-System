"""
Import every model here so that:
  1. `Base.metadata` is aware of all tables (needed for Alembic autogenerate).
  2. SQLAlchemy relationship() string references resolve correctly.
"""
from app.models.department import Department  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.leave_type import LeaveType  # noqa: F401
from app.models.leave_balance import LeaveBalance  # noqa: F401
from app.models.leave_request import LeaveRequest  # noqa: F401
from app.models.approval_history import ApprovalHistory  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.holiday import Holiday  # noqa: F401
