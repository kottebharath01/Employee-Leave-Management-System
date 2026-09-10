"""
Central place for every enum / constant used across the system.

Keeping these in one file makes the approval-routing and authorization
logic easy to read and change later.
"""
from enum import Enum


class Role(str, Enum):
    # --- Employee (business) hierarchy ---
    EMPLOYEE = "EMPLOYEE"
    TEAM_LEAD = "TEAM_LEAD"
    MANAGER = "MANAGER"
    SENIOR_MANAGER = "SENIOR_MANAGER"
    DIRECTOR = "DIRECTOR"
    CEO = "CEO"

    # --- HR hierarchy ---
    HR_ASSOCIATE = "HR_ASSOCIATE"
    HR_EXECUTIVE = "HR_EXECUTIVE"
    HR_MANAGER = "HR_MANAGER"
    HR_DIRECTOR = "HR_DIRECTOR"

    # --- System role ---
    ADMIN = "ADMIN"


# Roles that belong to the "employee business hierarchy" approval chain.
EMPLOYEE_HIERARCHY_CHAIN: dict[str, str | None] = {
    Role.EMPLOYEE: Role.TEAM_LEAD,
    Role.TEAM_LEAD: Role.MANAGER,
    Role.MANAGER: Role.SENIOR_MANAGER,
    Role.SENIOR_MANAGER: Role.DIRECTOR,
    Role.DIRECTOR: Role.CEO,
    Role.CEO: None,  # CEO leave is auto-approved, no approver above.
}

# Roles that belong to the "HR hierarchy" approval chain.
HR_HIERARCHY_CHAIN: dict[str, str | None] = {
    Role.HR_ASSOCIATE: Role.HR_MANAGER,
    Role.HR_EXECUTIVE: Role.HR_MANAGER,
    Role.HR_MANAGER: Role.HR_DIRECTOR,
    Role.HR_DIRECTOR: Role.CEO,
}

# Roles that are allowed to act as an "approver" in the system (i.e. can
# have leave requests routed to them and can approve/reject).
APPROVER_ROLES = {
    Role.TEAM_LEAD,
    Role.MANAGER,
    Role.SENIOR_MANAGER,
    Role.DIRECTOR,
    Role.HR_MANAGER,
    Role.HR_DIRECTOR,
    Role.CEO,
}

# Roles allowed to perform HR operations (employees, leave types, balances,
# holidays, leave records).
HR_ROLES = {Role.HR_ASSOCIATE, Role.HR_EXECUTIVE, Role.HR_MANAGER, Role.HR_DIRECTOR}

ALL_ROLES = {r.value for r in Role}


class LeaveRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ApprovalAction(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AUTO_APPROVED = "AUTO_APPROVED"
    CANCELLED = "CANCELLED"


class NotificationType(str, Enum):
    LEAVE_REQUEST_SUBMITTED = "LEAVE_REQUEST_SUBMITTED"
    LEAVE_REQUEST_APPROVED = "LEAVE_REQUEST_APPROVED"
    LEAVE_REQUEST_REJECTED = "LEAVE_REQUEST_REJECTED"
    LEAVE_REQUEST_CANCELLED = "LEAVE_REQUEST_CANCELLED"


def get_next_approver_role(current_role: str) -> str | None:
    """
    Given an employee's role, return the role of the person their leave
    request should be routed to, or None if it should be auto-approved
    (CEO) / the role does not participate in either hierarchy.
    """
    if current_role in EMPLOYEE_HIERARCHY_CHAIN:
        return EMPLOYEE_HIERARCHY_CHAIN[current_role]
    if current_role in HR_HIERARCHY_CHAIN:
        return HR_HIERARCHY_CHAIN[current_role]
    return None
